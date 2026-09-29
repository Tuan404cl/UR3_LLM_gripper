import rclpy
from rclpy.node import Node
from visualization_msgs.msg import Marker, MarkerArray

class ZoneVisualizer(Node):
    def __init__(self):
        super().__init__('zone_visualizer')
        self.publisher = self.create_publisher(MarkerArray, 'visualization_marker_array', 10)
        self.timer = self.create_timer(1.0, self.publish_markers)

        # Định nghĩa 3 Zone: X, Y, Z, R, G, B
        self.zones = [
            (0.3,  0.2, 0.0, 1.0, 0.4, 0.0), # Vùng A (Màu cam)
            (0.3,  0.0, 0.0, 0.0, 1.0, 0.5), # Vùng B (Màu xanh lam nhạt)
            (0.3, -0.2, 0.0, 0.5, 0.0, 1.0)  # Vùng C (Màu tím)
        ]

    def publish_markers(self):
        marker_array = MarkerArray()
        id_count = 0

        for x, y, z, r, g, b in self.zones:
            marker = Marker()
            marker.header.frame_id = "base_link"
            marker.header.stamp = self.get_clock().now().to_msg()
            marker.ns = "zones_area"
            marker.id = id_count
            marker.type = Marker.CUBE
            marker.action = Marker.ADD
            marker.pose.position.x = x
            marker.pose.position.y = y
            marker.pose.position.z = z - 0.005 # Chìm xuống sàn 5mm
            marker.scale.x = 0.15
            marker.scale.y = 0.15
            marker.scale.z = 0.01 
            marker.color.r = float(r)
            marker.color.g = float(g)
            marker.color.b = float(b)
            marker.color.a = 0.6 
            marker_array.markers.append(marker)
            id_count += 1

        self.publisher.publish(marker_array)

def main(args=None):
    rclpy.init(args=args)
    node = ZoneVisualizer()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()