import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Range
import sys


class UltrasonicMonitor(Node):
    def __init__(self):
        super().__init__('ultrasonic_monitor')
        self.topics = [
            'front_left', 'front_center', 'front_right',
            'side_left', 'side_right', 'back'
        ]
        self.values = {topic: 0.0 for topic in self.topics}
        self.stamps = {topic: 0 for topic in self.topics}

        for topic in self.topics:
            self.create_subscription(
                Range, f'ultrasonic/{topic}',
                lambda msg, t=topic: self.update_val(msg, t), 10)

        # Odświeżanie ekranu 10 razy na sekundę wystarczy do odczytu ludzkim okiem
        self.create_timer(0.1, self.display)
        print("\n" * 10)  # Przygotowanie miejsca w konsoli

    def update_val(self, msg, topic):
        self.values[topic] = msg.range
        self.stamps[topic] = msg.header.stamp.sec

    def display(self):
        # ANSI escape code: powrót kursora o 9 linii w górę (zamiast clear)
        sys.stdout.write("\033[9A")

        output = []
        output.append("=== MONITOR BEZPIECZENSTWA WOZKA (REAL-TIME) ===")
        output.append("-" * 50)
        output.append(f"{'POZYCJA':<20} | {'DYSTANS (m)':<15} | {'STATUS'}")
        output.append("-" * 50)

        for topic in self.topics:
            val = self.values[topic]
            # Kolorowanie: Czerwony < 0.5m, Żółty < 1.0m, Zielony reszta
            if val < 0.5:
                color = "\033[91m"
            elif val < 1.0:
                color = "\033[93m"
            else:
                color = "\033[92m"

            status = "OK" if val > 0.05 else "BLISKO/BLAD"
            output.append(f"{topic:<20} | {color}{val:>10.3f} m\033[0m | {status}")

        output.append("-" * 50)
        output.append("Nacisnij Ctrl+C aby zatrzymac")

        sys.stdout.write("\n".join(output) + "\n")
        sys.stdout.flush()


def main():
    rclpy.init()
    node = UltrasonicMonitor()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()