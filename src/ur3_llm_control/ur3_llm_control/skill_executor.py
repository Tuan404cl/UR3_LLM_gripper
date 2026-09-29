#!/usr/bin/env python3
import rclpy
import sys
import time
import re
from .llm_planner import LLMPlanner
from .task_validator import TaskValidator, get_student_task
from .robot_skills import RobotSkills

def main(args=None):
    rclpy.init(args=args)
    
    print("Đang khởi tạo hệ thống (ROS 2, LLM)...")
    robot = RobotSkills()
    
    # Chờ 1 giây để kết nối Publisher và vẽ các khối lên màn hình RViz
    time.sleep(1.0)
    robot.update_rviz()
    
    planner = LLMPlanner()
    validator = TaskValidator()
    
    print("\n" + "="*50)
    print("  HỆ THỐNG ĐIỀU KHIỂN ROBOT BẰNG NGÔN NGỮ TỰ NHIÊN  ")
    print("="*50)
    
    while rclpy.ok():
        try:
            # Nhập lệnh trực tiếp, không hỏi han lằng nhằng
            command = input("\nUSER COMMAND: ")
            if command.lower() in ['exit', 'quit']:
                print("Đang thoát chương trình...")
                break
            if not command.strip():
                continue
                
            context = ""
            
            # Nếu phát hiện chế độ TEST (Cheat code để bỏ qua AI)
            if command.strip().lower() == "test":
                print("[DEBUG] Đang chạy chế độ TEST (Bỏ qua AI)...")
                plan_json = {
                    "plan": [
                        {"skill": "pick", "object": "blue_cube"},
                        {"skill": "place", "object": "blue_cube", "zone": "zone_a"},
                        {"skill": "home"}
                    ]
                }
            else:
                # TỰ ĐỘNG BẮT MÃ SỐ SINH VIÊN TRONG CÂU LỆNH
                # Tìm chuỗi số có từ 5 chữ số trở lên
                match = re.search(r'\d{5,}', command)
                if match:
                    student_id = match.group(0)
                    print(f"[VALIDATOR] Đã phát hiện MSSV: {student_id} trong câu lệnh.")
                    target_layout = get_student_task(student_id)
                    context = str(target_layout)

                print("⏳ Đang gửi yêu cầu lên Trí tuệ nhân tạo (MIMO Flash)...")
                plan_json = planner.generate_plan(command, context)

            if not plan_json:
                print("❌ Lỗi: LLM không trả về kết quả hợp lệ.")
                continue

            # Xác thực Plan
            is_valid, msg = validator.validate(plan_json)
            if not is_valid:
                print(f"\nPLAN REJECTED: {msg}")
                continue
                
            # In kế hoạch ra Terminal
            print("\nLLM PLAN:")
            for step in plan_json["plan"]:
                if step['skill'] == 'home':
                    print("home()")
                elif step['skill'] == 'pick':
                    print(f"pick({step['object']})")
                elif step['skill'] == 'place':
                    print(f"place({step['object']}, {step['zone']})")
            
            # Thực thi Plan
            print("\nEXECUTION:")
            all_success = True
            for step in plan_json["plan"]:
                skill = step["skill"]
                status = "FAILED"
                log_str = ""
                
                if skill == "home":
                    log_str = "home()"
                    status = robot.home()
                elif skill == "pick":
                    log_str = f"pick({step['object']})"
                    status = robot.pick(step['object'])
                elif skill == "place":
                    log_str = f"place({step['object']}, {step['zone']})"
                    status = robot.place(step['object'], step['zone'])
                    
                print(f"{log_str:.<30} {status}")
                
                if "FAILED" in status or "INVALID" in status:
                    all_success = False
                    break 
                    
            if all_success:
                print("\nTASK SUCCESS")
            else:
                print("\nTASK ABORTED")
                
        except KeyboardInterrupt:
            break

    rclpy.shutdown()

if __name__ == '__main__':
    main()