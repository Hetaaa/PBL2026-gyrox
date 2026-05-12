import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Range
from std_msgs.msg import String
import serial


class UltrasonicDriver(Node):
    def __init__(self):
        super().__init__('ultrasonic_driver')

        self.sensor_config = [
            ('front_left', '/dev/serial/by-path/pci-0000:00:14.0-usb-0:1.1:1.0-port0', 'ultrasonic_front_left_link'),
            ('front_right', '/dev/serial/by-path/pci-0000:00:14.0-usb-0:1.3:1.0-port0', 'ultrasonic_front_right_link'),
            ('front_center', '/dev/serial/by-path/pci-0000:00:14.0-usb-0:1.2:1.0-port0',
             'ultrasonic_front_center_link'),
            ('side_left', '/dev/serial/by-path/pci-0000:00:14.0-usb-0:1.4.1:1.0-port0', 'ultrasonic_side_left_link'),
            ('side_right', '/dev/serial/by-path/pci-0000:00:14.0-usb-0:1.4.4:1.0-port0', 'ultrasonic_side_right_link'),
            ('back', '/dev/serial/by-path/pci-0000:00:14.0-usb-0:1.4.3:1.0-port0', 'ultrasonic_back_link')
        ]

        # KLUCZOWE: Inicjalizacja zmiennych pomocniczych
        self.history = {conf[2]: [float('inf')] for conf in self.sensor_config}
        self.last_update = {conf[2]: self.get_clock().now().nanoseconds for conf in self.sensor_config}
        self.index = 0  # To tutaj brakowało!
        self.current_zone = ""

        self.sensors = []
        for name, path, frame in self.sensor_config:
            try:
                # Timeout=0 dla odczytu nieblokującego
                ser = serial.Serial(path, 9600, timeout=0)
                ser.reset_input_buffer()
                pub = self.create_publisher(Range, f'ultrasonic/{name}', 10)
                self.sensors.append({'serial': ser, 'pub': pub, 'frame': frame, 'name': name})
                self.get_logger().info(f'Podlaczono: {name}')
            except Exception as e:
                self.get_logger().error(f'Blad portu {name} ({path}): {e}')

        # Subskrypcja stref od kolegów
        self.create_subscription(String, '/zones_info', self.lidar_status_callback, 10)

        # Timer 50Hz
        self.create_timer(0.02, self.timer_callback)

    def lidar_status_callback(self, msg):
        self.current_zone = msg.data.strip()

    def timer_callback(self):
        if not self.sensors:
            return

        current_time = self.get_clock().now().nanoseconds
        s = self.sensors[self.index]
        f_id = s['frame']
        is_front = s['name'].startswith('front')

        # Sprawdzamy, czy czujnik juz cos widzi bardzo blisko (np. < 0.4m)
        already_detecting_close = any(d < 0.5 for d in self.history[f_id])

        # Aktywujemy przód jeśli jest Strefa 1 LUB jeśli czujnik już trzyma przeszkodę blisko
        if is_front and self.current_zone != 'Strefa 1' and not already_detecting_close:
            self.publish_range(s, float('inf'))
            self.index = (self.index + 1) % len(self.sensors)
            return

        try:
            # Odczyt najnowszej ramki
            if s['serial'].in_waiting >= 4:
                raw = s['serial'].read(s['serial'].in_waiting)
                idx = raw.rfind(b'\xff')
                if idx != -1 and len(raw) >= idx + 4:
                    frame = raw[idx:idx + 4]
                    if (0xff + frame[1] + frame[2]) & 0xff == frame[3]:
                        dist = ((frame[1] << 8) + frame[2]) / 1000.0
                        self.history[f_id].append(dist)
                        if len(self.history[f_id]) > 3:
                            self.history[f_id].pop(0)
                        self.last_update[f_id] = current_time

            # Publikacja: jeśli brak danych przez 0.5s, wyślij inf (Fail-safe)
            if current_time - self.last_update[f_id] > 0.5 * 1e9:
                self.publish_range(s, float('inf'))
            else:
                median = sorted(self.history[f_id])[len(self.history[f_id]) // 2]
                self.publish_range(s, median)

        except Exception:
            pass

        # Przejdź do następnego czujnika
        self.index = (self.index + 1) % len(self.sensors)

    def publish_range(self, sensor, range_value):
        msg = Range()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = sensor['frame']
        msg.radiation_type = Range.ULTRASOUND
        msg.field_of_view = 0.26
        msg.min_range = 0.03
        msg.max_range = 4.5
        msg.range = float(range_value)
        sensor['pub'].publish(msg)

    def __del__(self):
        for s in self.sensors:
            try:
                s['serial'].close()
            except:
                pass


def main(args=None):
    rclpy.init(args=args)
    node = UltrasonicDriver()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Zamykanie...')
    finally:
        # Zmieniona kolejność zamykania, aby uniknąć błędów w konsoli
        if rclpy.ok():
            node.destroy_node()
            rclpy.shutdown()


if __name__ == '__main__':
    main()