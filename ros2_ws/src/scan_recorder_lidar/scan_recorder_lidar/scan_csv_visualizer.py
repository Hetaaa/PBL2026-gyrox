"""Standalone visualizer for scan_recorder CSV output."""

from __future__ import annotations

import argparse
import csv
import math
from dataclasses import dataclass
from typing import Iterable, Sequence

import matplotlib.pyplot as plt


@dataclass
class ScanMetadata:
    """Metadata shared across measurements in a single scan."""

    scan_id: int
    stamp_sec: int
    stamp_nanosec: int
    frame_id: str
    angle_min: float
    angle_increment: float


def _parse_float(value: str | None, field: str) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except ValueError as exc:
        raise ValueError(f'Invalid float for {field}: {value!r}') from exc


def _parse_int(value: str | None, field: str) -> int:
    if value is None:
        raise ValueError(f'Missing value for {field}.')
    try:
        return int(value)
    except ValueError as exc:
        raise ValueError(f'Invalid integer for {field}: {value!r}') from exc


def load_scan_rows(
    csv_path: str,
    scan_id: int | None,
) -> tuple[ScanMetadata, Sequence[dict[str, str]]]:
    """Load all rows for a specific scan id (or the latest if None)."""
    selected_rows: list[dict[str, str]] = []
    latest_scan_id: int | None = None

    with open(csv_path, newline='', encoding='utf-8') as csv_file:
        reader = csv.DictReader(csv_file)
        if not reader.fieldnames:
            raise ValueError('CSV file is missing a header row.')
        for row in reader:
            row_scan_id = _parse_int(row.get('scan_id'), 'scan_id')
            if scan_id is None:
                if latest_scan_id is None or row_scan_id > latest_scan_id:
                    latest_scan_id = row_scan_id
                    selected_rows = []
                if row_scan_id == latest_scan_id:
                    selected_rows.append(row)
            elif row_scan_id == scan_id:
                selected_rows.append(row)

    if scan_id is None:
        scan_id = latest_scan_id

    if scan_id is None or not selected_rows:
        raise ValueError('No scan rows found for the requested scan id.')

    first = selected_rows[0]
    stamp_nanosec = _parse_int(first.get('stamp_nanosec'), 'stamp_nanosec')
    if not 0 <= stamp_nanosec <= 999_999_999:
        raise ValueError(
            f'stamp_nanosec out of range: {stamp_nanosec}.'
        )
    metadata = ScanMetadata(
        scan_id=scan_id,
        stamp_sec=_parse_int(first.get('stamp_sec'), 'stamp_sec'),
        stamp_nanosec=stamp_nanosec,
        frame_id=first.get('frame_id') or 'unknown',
        angle_min=_parse_float(first.get('angle_min'), 'angle_min') or 0.0,
        angle_increment=_parse_float(
            first.get('angle_increment'),
            'angle_increment',
        )
        or 0.0,
    )
    return metadata, selected_rows


def build_measurements(
    metadata: ScanMetadata,
    rows: Iterable[dict[str, str]],
) -> tuple[list[float], list[float], list[float | None]]:
    """Convert CSV rows into angle/range/intensity sequences."""
    angles: list[float] = []
    ranges: list[float] = []
    intensities: list[float | None] = []

    for row in rows:
        range_value = _parse_float(row.get('range'), 'range')
        if range_value is None or not math.isfinite(range_value):
            continue
        idx = _parse_int(row.get('idx'), 'idx')
        angle = metadata.angle_min + idx * metadata.angle_increment
        intensity = _parse_float(row.get('intensity'), 'intensity')
        angles.append(angle)
        ranges.append(range_value)
        intensities.append(intensity)

    if not angles:
        raise ValueError('No valid range measurements found for this scan.')

    return angles, ranges, intensities


def _build_color_values(
    intensities: Sequence[float | None],
    use_intensity: bool,
) -> list[float] | None:
    if not use_intensity:
        return None
    color_values: list[float] = []
    has_finite = False
    for value in intensities:
        if value is None or not math.isfinite(value):
            color_values.append(float('nan'))
        else:
            color_values.append(value)
            has_finite = True
    return color_values if has_finite else None


def plot_scan(
    metadata: ScanMetadata,
    angles: Sequence[float],
    ranges: Sequence[float],
    intensities: Sequence[float | None],
    plot_mode: str,
    color_by_intensity: bool,
    title: str | None,
) -> None:
    """Render a matplotlib plot for the selected scan."""
    color_values = _build_color_values(intensities, color_by_intensity)
    scatter_kwargs = {'c': color_values, 's': 8, 'cmap': 'viridis'}

    if plot_mode == 'polar':
        axis = plt.subplot(projection='polar')
        scatter = axis.scatter(angles, ranges, **scatter_kwargs)
        axis.set_theta_zero_location('N')
        axis.set_theta_direction(-1)
        axis.set_rlabel_position(90)
        axis.set_title(title or f'Scan {metadata.scan_id}')
    else:
        x_values = [r * math.cos(a) for r, a in zip(ranges, angles)]
        y_values = [r * math.sin(a) for r, a in zip(ranges, angles)]
        axis = plt.subplot()
        scatter = axis.scatter(x_values, y_values, **scatter_kwargs)
        axis.set_aspect('equal', adjustable='box')
        axis.set_xlabel('X (m)')
        axis.set_ylabel('Y (m)')
        axis.set_title(title or f'Scan {metadata.scan_id}')

    if color_values is not None:
        plt.colorbar(scatter, ax=axis, label='Intensity')


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description=(
            'Visualize scan_recorder CSV files using matplotlib.'
        )
    )
    parser.add_argument(
        'csv_path',
        nargs='?',
        default='scan_data.csv',
        help='Path to scan_recorder CSV file.',
    )
    parser.add_argument(
        '--scan-id',
        type=int,
        help='Scan id to plot. Defaults to the latest scan in the file.',
    )
    parser.add_argument(
        '--plot',
        choices=('polar', 'cartesian'),
        default='polar',
        help='Plot mode (polar or cartesian).',
    )
    parser.add_argument(
        '--color-intensity',
        action='store_true',
        help='Color points by intensity values when available.',
    )
    parser.add_argument(
        '--title',
        help='Optional plot title.',
    )
    return parser.parse_args()


def main() -> None:
    """Run the CSV visualizer."""
    args = parse_args()
    metadata, rows = load_scan_rows(args.csv_path, args.scan_id)
    angles, ranges, intensities = build_measurements(metadata, rows)
    title = args.title or (
        f'Scan {metadata.scan_id} '
        f'({metadata.frame_id}) '
        f'@ {metadata.stamp_sec}.{metadata.stamp_nanosec:09d}'
    )
    plot_scan(
        metadata,
        angles,
        ranges,
        intensities,
        args.plot,
        args.color_intensity,
        title,
    )
    plt.show()


if __name__ == '__main__':
    main()
