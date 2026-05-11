import math
from sensor_msgs.msg import LaserScan

def normalize_angle_deg(angle_rad):
    """Normalizuje kat w radianach do 0-360 stopni."""
    return math.degrees(angle_rad) % 360.0

def filter_scan(scan_msg: LaserScan, min_angle_deg: float, max_angle_deg: float) -> LaserScan:
    """
    Przyjmuje strukture wiadomosci ze skanera (LaserScan), 
    zeruje (ustawia na inf, lub 0.0 w intensywnosci) pomiary spoza zadanego zakresu
    i zwraca nowa, przefiltrowana strukture LaserScan.
    """
    filtered_msg = LaserScan()
    
    # Kopiujemy naglowek i parametry metadanych (struktury RPLidar)
    filtered_msg.header = scan_msg.header
    filtered_msg.angle_min = scan_msg.angle_min
    filtered_msg.angle_max = scan_msg.angle_max
    filtered_msg.angle_increment = scan_msg.angle_increment
    filtered_msg.time_increment = scan_msg.time_increment
    filtered_msg.scan_time = scan_msg.scan_time
    filtered_msg.range_min = scan_msg.range_min
    filtered_msg.range_max = scan_msg.range_max
    
    # Tworzymy nowe listy do modyfikacji (rozmiar musi zostac ten sam dla LaserScan)
    filtered_ranges = list(scan_msg.ranges)
    filtered_intensities = list(scan_msg.intensities) if scan_msg.intensities else []
    
    for i in range(len(filtered_ranges)):
        current_angle_rad = scan_msg.angle_min + i * scan_msg.angle_increment
        current_angle_deg = normalize_angle_deg(current_angle_rad)
        
        keep_point = False
        if min_angle_deg <= max_angle_deg:
            keep_point = (min_angle_deg <= current_angle_deg <= max_angle_deg)
        else:
            keep_point = (current_angle_deg >= min_angle_deg or current_angle_deg <= max_angle_deg)
        
        # Odrzucanie niechcianych punktow
        if not keep_point:
            filtered_ranges[i] = float('inf')
            if filtered_intensities:
                filtered_intensities[i] = 0.0
                
    filtered_msg.ranges = filtered_ranges
    filtered_msg.intensities = filtered_intensities
    
    return filtered_msg
