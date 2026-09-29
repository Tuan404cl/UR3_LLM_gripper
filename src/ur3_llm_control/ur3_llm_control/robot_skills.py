import rclpy
from rclpy.node import Node
from visualization_msgs.msg import Marker, MarkerArray
from moveit_msgs.srv import GetPositionIK
from control_msgs.action import FollowJointTrajectory, GripperCommand
from trajectory_msgs.msg import JointTrajectoryPoint
from sensor_msgs.msg import JointState
# Import thư viện để tạo mặt phẳng va chạm
from moveit_msgs.msg import CollisionObject
from shape_msgs.msg import SolidPrimitive
from geometry_msgs.msg import Pose
from rclpy.action import ActionClient
import time
import threading

class RobotSkills(Node):
    def __init__(self):
        super().__init__('robot_skills_node')
        self.get_logger().info("[INFO] Khởi tạo Robot Skills (Có mặt phẳng chống va chạm)...")

        # ==========================================
        # ⚙️ KHU VỰC TINH CHỈNH THÔNG SỐ (FINE-TUNING)
        # ==========================================
        # 1. Chiều dài kẹp (Z-Offset): Tăng số này lên nếu mũi kẹp vẫn đâm xuống đất. Giảm nếu kẹp gắp trượt trên không.
        self.Z_OFFSET = 0.22  # Gợi ý: 0.18m - 0.22m
        
        # 2. Độ khép ngón tay: Tùy chỉnh để ngón tay chạm vừa khít mặt khối lập phương
        self.GRIP_OPEN_VAL = 0.0   # Mở hết cỡ
        self.GRIP_CLOSE_VAL = 0.4  # Đóng vừa đủ (Số càng lớn kẹp càng chặt. Tối đa khoảng ~0.7)
        # ==========================================

        self.marker_pub = self.create_publisher(MarkerArray, 'llm_cubes', 10)
        self.collision_pub = self.create_publisher(CollisionObject, '/collision_object', 10)

        self.ik_client = self.create_client(GetPositionIK, '/compute_ik')
        self.arm_client = ActionClient(self, FollowJointTrajectory, '/arm_controller/follow_joint_trajectory')
        self.gripper_client = ActionClient(self, GripperCommand, '/gripper_controller/gripper_cmd')

        self.current_joint_state = JointState()
        self.joint_sub = self.create_subscription(JointState, '/joint_states', self.joint_cb, 10)

        self.executor_ = rclpy.executors.SingleThreadedExecutor()
        self.executor_.add_node(self)
        self.spin_thread = threading.Thread(target=self.executor_.spin, daemon=True)
        self.spin_thread.start()

        self.get_logger().info("Đang chờ các tiến trình MoveIt...")
        self.ik_client.wait_for_service()
        self.arm_client.wait_for_server()
        self.gripper_client.wait_for_server()
        
        while not self.current_joint_state.name:
            time.sleep(0.1)

        # Thêm mặt bàn ngay sau khi khởi động
        time.sleep(1.0)
        self.add_collision_table()

        self.get_logger().info("✅ Hệ thống sẵn sàng!")

        self.zones = {
            "zone_a": [0.3,  0.2, 0.025],
            "zone_b": [0.3,  0.0, 0.025],
            "zone_c": [0.3, -0.2, 0.025]
        }

        self.objects = {
            "red_cube":    {"frame": "base_link", "pos": [-0.25,  0.15, 0.025], "color": [1.0, 0.0, 0.0], "id": 10},
            "yellow_cube": {"frame": "base_link", "pos": [-0.25,  0.00, 0.025], "color": [1.0, 1.0, 0.0], "id": 11},
            "blue_cube":   {"frame": "base_link", "pos": [-0.25, -0.15, 0.025], "color": [0.0, 0.0, 1.0], "id": 12}
        }

        self.timer = self.create_timer(0.5, self.update_rviz)

    def joint_cb(self, msg):
        self.current_joint_state = msg

    def add_collision_table(self):
        """Tạo một mặt phẳng ảo ngăn cánh tay cắm xuống đất"""
        table = CollisionObject()
        table.header.frame_id = "base_link"
        table.id = "virtual_table"

        box = SolidPrimitive()
        box.type = SolidPrimitive.BOX
        box.dimensions = [2.0, 2.0, 0.02] # Mặt bàn rộng 2m x 2m, dày 2cm

        pose = Pose()
        pose.position.x = 0.0
        pose.position.y = 0.0
        pose.position.z = -0.011 # Đặt chìm xuống dưới đất, mặt trên cùng vừa chạm Z=0.0

        table.primitives.append(box)
        table.primitive_poses.append(pose)
        table.operation = CollisionObject.ADD

        self.collision_pub.publish(table)
        self.get_logger().info("Đã trải mặt phẳng chống va chạm (Z < 0).")

    def update_rviz(self):
        msg = MarkerArray()
        for obj_name, data in self.objects.items():
            marker = Marker()
            marker.header.frame_id = data["frame"]
            marker.header.stamp = self.get_clock().now().to_msg()
            marker.ns = "cubes"
            marker.id = data["id"]
            marker.type = Marker.CUBE
            marker.action = Marker.ADD
            marker.pose.position.x = float(data["pos"][0])
            marker.pose.position.y = float(data["pos"][1])
            marker.pose.position.z = float(data["pos"][2])
            marker.pose.orientation.w = 1.0
            marker.scale.x = 0.05
            marker.scale.y = 0.05
            marker.scale.z = 0.05
            marker.color.r = float(data["color"][0])
            marker.color.g = float(data["color"][1])
            marker.color.b = float(data["color"][2])
            marker.color.a = 1.0
            msg.markers.append(marker)
        self.marker_pub.publish(msg)

    def _move_arm_to_joints(self, target_joints):
        import math
        goal = FollowJointTrajectory.Goal()
        arm_joint_names = ['shoulder_pan_joint', 'shoulder_lift_joint', 'elbow_joint', 'wrist_1_joint', 'wrist_2_joint', 'wrist_3_joint']
        goal.trajectory.joint_names = arm_joint_names
        current_positions = []
        for name in arm_joint_names:
            if name in self.current_joint_state.name:
                idx = self.current_joint_state.name.index(name)
                current_positions.append(self.current_joint_state.position[idx])
            else:
                current_positions.append(0.0)

        # THUẬT TOÁN ÉP ĐI ĐƯỜNG NGẮN NHẤT (Chống lật cổ tay)
        for i in range(len(target_joints)):
            diff = target_joints[i] - current_positions[i]
            while diff > math.pi:
                target_joints[i] -= 2 * math.pi
                diff = target_joints[i] - current_positions[i]
            while diff < -math.pi:
                target_joints[i] += 2 * math.pi
                diff = target_joints[i] - current_positions[i]
        
        pt = JointTrajectoryPoint()
        pt.positions = target_joints
        
        pt = JointTrajectoryPoint()
        pt.positions = target_joints
        pt.velocities = [0.0] * 6  
        pt.time_from_start.sec = 2 
        goal.trajectory.points.append(pt)

        future = self.arm_client.send_goal_async(goal)
        while not future.done(): time.sleep(0.1)
        goal_handle = future.result()
        if not goal_handle.accepted: return False
        
        res_future = goal_handle.get_result_async()
        while not res_future.done(): time.sleep(0.1)
        
        result = res_future.result().result
        if result.error_code != 0:
            return False
            
        return True

    def _move_to_pose(self, x, y, z):
        req = GetPositionIK.Request()
        req.ik_request.group_name = 'arm'
        req.ik_request.avoid_collisions = True
        
        # 1. CẤP CHO THUẬT TOÁN 1.0 GIÂY ĐỂ TÍNH TOÁN (Tránh bỏ cuộc sớm)
        req.ik_request.timeout.sec = 1
        req.ik_request.timeout.nanosec = 0
        
        req.ik_request.pose_stamped.header.frame_id = 'base_link'
        req.ik_request.pose_stamped.pose.position.x = float(x)
        req.ik_request.pose_stamped.pose.position.y = float(y)
        req.ik_request.pose_stamped.pose.position.z = float(z)
        
        req.ik_request.pose_stamped.pose.orientation.x = 1.0
        req.ik_request.pose_stamped.pose.orientation.y = 0.0
        req.ik_request.pose_stamped.pose.orientation.z = 0.0
        req.ik_request.pose_stamped.pose.orientation.w = 0.0

        # LẦN 1: Thử giải với góc khớp hiện tại
        req.ik_request.robot_state.joint_state = self.current_joint_state
        future = self.ik_client.call_async(req)
        while not future.done(): time.sleep(0.1)
        res = future.result()

        # LẦN 2: Nếu Lần 1 bị kẹt toán học, mượn tạm tư thế Home làm điểm nháp để giải lại!
        if res.error_code.val != 1:
            # self.get_logger().warn("IK kẹt ở tư thế hiện tại, đang mượn Seed từ tư thế Home...")
            req.ik_request.robot_state.joint_state.name = ['shoulder_pan_joint', 'shoulder_lift_joint', 'elbow_joint', 'wrist_1_joint', 'wrist_2_joint', 'wrist_3_joint']
            req.ik_request.robot_state.joint_state.position = [0.0, -1.57, 1.0, -1.0, -1.57, 0.0]
            
            future = self.ik_client.call_async(req)
            while not future.done(): time.sleep(0.1)
            res = future.result()

            if res.error_code.val != 1:
                self.get_logger().error(f"IK thất bại hoàn toàn (Mã lỗi: {res.error_code.val}). Điểm đích ngoài tầm với!")
                return False

        # Nếu giải thành công, trích xuất góc quay gửi cho động cơ
        target_joints = []
        arm_joint_names = ['shoulder_pan_joint', 'shoulder_lift_joint', 'elbow_joint', 'wrist_1_joint', 'wrist_2_joint', 'wrist_3_joint']
        for name in arm_joint_names:
            idx = res.solution.joint_state.name.index(name)
            target_joints.append(res.solution.joint_state.position[idx])

        return self._move_arm_to_joints(target_joints)

    def _control_gripper(self, close=True):
        goal = GripperCommand.Goal()
        # Áp dụng thông số tùy chỉnh
        goal.command.position = self.GRIP_CLOSE_VAL if close else self.GRIP_OPEN_VAL 
        goal.command.max_effort = 10.0
        future = self.gripper_client.send_goal_async(goal)
        while not future.done(): time.sleep(0.1)
        return True

    def home(self):
        self.get_logger().info("Đang về tư thế Home...")
        success = self._move_arm_to_joints([0.0, -1.57, 1.0, -1.0, -1.57, 0.0])
        return "SUCCESS" if success else "FAILED"

    def pick(self, object_name):
        if object_name not in self.objects: return "INVALID_OBJECT"
        x, y, z = self.objects[object_name]["pos"]
        
        tool0_z = z + self.Z_OFFSET 
        clearance_z = tool0_z + 0.15  # Tự động tính trần bay: Cách vật 15cm

        self.get_logger().info(f"==> Đang gắp {object_name}...")
        
        if not self._move_to_pose(x, y, clearance_z): return "IK_FAILED"
        self._control_gripper(close=False)       
        if not self._move_to_pose(x, y, tool0_z): return "IK_FAILED"
        self._control_gripper(close=True)        
        
        self.objects[object_name]["frame"] = "tool0"
        self.objects[object_name]["pos"] = [0.0, 0.0, self.Z_OFFSET] 

        if not self._move_to_pose(x, y, clearance_z): return "IK_FAILED"
        self.home()
        return "SUCCESS"

    def place(self, object_name, zone_name):
        if object_name not in self.objects or zone_name not in self.zones: return "INVALID_PARAMS"
        x, y, z = self.zones[zone_name]
        
        tool0_z = z + self.Z_OFFSET
        clearance_z = tool0_z + 0.15  # Tự động tính trần bay: Cách vùng thả 15cm

        self.get_logger().info(f"==> Đang thả {object_name} xuống {zone_name}...")
        
        if not self._move_to_pose(x, y, clearance_z): return "IK_FAILED"
        if not self._move_to_pose(x, y, tool0_z): return "IK_FAILED"
        self._control_gripper(close=False)       
        
        self.objects[object_name]["frame"] = "base_link"
        self.objects[object_name]["pos"] = self.zones[zone_name]

        if not self._move_to_pose(x, y, clearance_z): return "IK_FAILED"
        self.home ()
        return "SUCCESS"