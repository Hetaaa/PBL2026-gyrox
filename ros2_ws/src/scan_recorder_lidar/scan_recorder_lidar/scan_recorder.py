"""ROS2 node for recording /scan data to CSV and SQLite, plus /scan2."""

from __future__ import annotations

import csv
import os
import sqlite3
from typing import Iterable, Sequence

from .filtrfunkcja import filter_scan

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan

CSV_HEADER = (
    'scan_id',
    'stamp_sec',
    'stamp_nanosec',
    'frame_id',
    'angle_min',
    'angle_max',
    'angle_increment',
    'time_increment',
    'scan_time',
    'range_min',
    'range_max',
    'idx',
    'range',
    'intensity',
)

INSERT_SQL = (
    'INSERT INTO scan_measurements ('
    'scan_id, stamp_sec, stamp_nanosec, frame_id, angle_min, angle_max, '
    'angle_increment, time_increment, scan_time, range_min, range_max, '
    'idx, range, intensity'
    ') VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'
)


class ScanRecorder(Node):
    """Subscribe to /scan, publish /scan2, and persist LaserScan data."""

    def __init__(self) -> None:
        super().__init__('scan_recorder')
        self.declare_parameter('csv_path', 'scan_data.csv')
        self.declare_parameter('sqlite_path', 'scan_data.sqlite')

        self._csv_path = os.path.expanduser(
            self.get_parameter('csv_path').value
        )
        self._sqlite_path = os.path.expanduser(
            self.get_parameter('sqlite_path').value
        )
        self._scan_id = 0

        self._ensure_parent_dir(self._csv_path)
        self._ensure_parent_dir(self._sqlite_path)
        try:
            self._setup_csv()
            self._setup_sqlite()
        except Exception:
            self._close_resources()
            raise

        self._scan_publisher = self.create_publisher(
            LaserScan,
            '/scan2',
            10,
        )
        self.subscription = self.create_subscription(
            LaserScan,
            '/scan',
            self._callback,
            10,
        )
        self.get_logger().info(
            'Scan recorder saving CSV to '
            f'{self._csv_path} and SQLite to {self._sqlite_path}.'
        )

    def destroy_node(self) -> None:
        """Close file handles and database connections."""
        self._close_resources()
        super().destroy_node()

    def _setup_csv(self) -> None:
        write_header = (
            not os.path.exists(self._csv_path)
            or os.path.getsize(self._csv_path) == 0
        )
        self._csv_file = open(
            self._csv_path, 'a', newline='', encoding='utf-8'
        )
        self._csv_writer = csv.writer(self._csv_file)
        try:
            if write_header:
                self._csv_writer.writerow(CSV_HEADER)
                self._csv_file.flush()
        except Exception:
            self._csv_file.close()
            raise

    def _setup_sqlite(self) -> None:
        self._db = sqlite3.connect(self._sqlite_path)
        self._db.execute(
            """
            CREATE TABLE IF NOT EXISTS scan_measurements (
                scan_id INTEGER NOT NULL,
                stamp_sec INTEGER NOT NULL,
                stamp_nanosec INTEGER NOT NULL,
                frame_id TEXT NOT NULL,
                angle_min REAL NOT NULL,
                angle_max REAL NOT NULL,
                angle_increment REAL NOT NULL,
                time_increment REAL NOT NULL,
                scan_time REAL NOT NULL,
                range_min REAL NOT NULL,
                range_max REAL NOT NULL,
                idx INTEGER NOT NULL,
                range REAL,
                intensity REAL
            )
            """
        )
        self._db.commit()

    def _callback(self, msg: LaserScan) -> None:
        filtered_msg = filter_scan(msg, min_angle_deg=20.0, max_angle_deg=160.0)
        self._scan_publisher.publish(filtered_msg)
        self._scan_id += 1
        rows = self._build_rows(filtered_msg)
        if not rows:
            return

        self._csv_writer.writerows(rows)
        self._csv_file.flush()
        self._db.executemany(INSERT_SQL, rows)
        self._db.commit()

    def _build_rows(self, msg: LaserScan) -> Sequence[Sequence[object]]:
        stamp = msg.header.stamp
        intensities = msg.intensities
        rows = []
        for idx, range_value in enumerate(msg.ranges):
            intensity_value = (
                float(intensities[idx]) if idx < len(intensities) else None
            )
            rows.append(
                (
                    self._scan_id,
                    stamp.sec,
                    stamp.nanosec,
                    msg.header.frame_id,
                    float(msg.angle_min),
                    float(msg.angle_max),
                    float(msg.angle_increment),
                    float(msg.time_increment),
                    float(msg.scan_time),
                    float(msg.range_min),
                    float(msg.range_max),
                    idx,
                    float(range_value),
                    intensity_value,
                )
            )
        return rows

    def _close_resources(self) -> None:
        """Close any open file or database resources."""
        if hasattr(self, '_csv_file') and not self._csv_file.closed:
            self._csv_file.close()
        if hasattr(self, '_db'):
            self._db.close()

    @staticmethod
    def _ensure_parent_dir(path: str) -> None:
        """Ensure the parent directory for the given path exists."""
        directory = os.path.dirname(path)
        if directory:
            os.makedirs(directory, exist_ok=True)


def main(args: Iterable[str] | None = None) -> None:
    """Run the scan recorder node."""
    rclpy.init(args=args)
    recorder = ScanRecorder()
    try:
        rclpy.spin(recorder)
    except KeyboardInterrupt:
        pass
    finally:
        recorder.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
