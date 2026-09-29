# ur3_llm_control/task_validator.py

def get_student_task(student_id):
    """
    Tính toán yêu cầu sắp xếp dựa trên 2 số cuối của MSSV.
    P = XX mod 6
    """
    try:
        # Lấy 2 chữ số cuối của MSSV
        student_id_str = str(student_id).strip()
        last_two_digits = int(student_id_str[-2:])
        p = last_two_digits % 6
        
        # Bảng quy ước từ đề bài
        mapping = {
            0: {"zone_a": "red_cube", "zone_b": "yellow_cube", "zone_c": "blue_cube"},
            1: {"zone_a": "red_cube", "zone_b": "blue_cube", "zone_c": "yellow_cube"},
            2: {"zone_a": "yellow_cube", "zone_b": "red_cube", "zone_c": "blue_cube"},
            3: {"zone_a": "yellow_cube", "zone_b": "blue_cube", "zone_c": "red_cube"},
            4: {"zone_a": "blue_cube", "zone_b": "red_cube", "zone_c": "yellow_cube"},
            5: {"zone_a": "blue_cube", "zone_b": "yellow_cube", "zone_c": "red_cube"},
        }
        
        target_layout = mapping[p]
        print(f"[VALIDATOR] MSSV: {student_id} -> P = {p}")
        print(f"[VALIDATOR] Nhiệm vụ: {target_layout}")
        
        return target_layout
    except ValueError:
        print("[VALIDATOR ERROR] MSSV không hợp lệ. Vui lòng nhập số.")
        return None

class TaskValidator:
    def __init__(self):
        # Định nghĩa các thông số cho phép từ đề bài
        self.valid_skills = ["pick", "place", "home"]
        self.valid_objects = ["red_cube", "yellow_cube", "blue_cube"]
        self.valid_zones = ["zone_a", "zone_b", "zone_c"]

    def validate(self, plan_json):
        """
        Kiểm tra xem kế hoạch LLM trả về có đúng định dạng và có an toàn để chạy không.
        """
        if not plan_json or "plan" not in plan_json:
            return False, "Cấu trúc JSON bị thiếu mảng 'plan'."
        
        steps = plan_json["plan"]
        if len(steps) == 0:
            return False, "Kế hoạch rỗng."

        for i, step in enumerate(steps):
            skill = step.get("skill")
            
            # 1. Kiểm tra Skill
            if skill not in self.valid_skills:
                return False, f"Bước {i+1}: Lỗi - Skill '{skill}' không được hỗ trợ."
            
            # 2. Kiểm tra Object (nếu có)
            if "object" in step:
                obj = step["object"]
                if obj not in self.valid_objects:
                    return False, f"Bước {i+1}: Lỗi - Vật thể '{obj}' không tồn tại."
                    
            # 3. Kiểm tra Zone (nếu có)
            if "zone" in step:
                zone = step["zone"]
                if zone not in self.valid_zones:
                    return False, f"Bước {i+1}: Lỗi - Vùng '{zone}' không tồn tại."

            # 4. Kiểm tra logic tham số bắt buộc của từng skill
            if skill == "pick" and "object" not in step:
                return False, f"Bước {i+1}: Lỗi - Skill 'pick' thiếu tham số 'object'."
            if skill == "place" and ("object" not in step or "zone" not in step):
                return False, f"Bước {i+1}: Lỗi - Skill 'place' thiếu tham số 'object' hoặc 'zone'."

        return True, "Kế hoạch hợp lệ và an toàn để thực thi."