import requests
import json
import re

class LLMPlanner:
    def __init__(self):
        # ⚠️ THAY API KEY CỦA BẠN VÀO ĐÂY (Nằm trong cặp dấu ngoặc kép, KHÔNG có ngoặc < >)
        # Ví dụ: self.api_key = "sk-or-v1-1a2b3c4d..."
        self.api_key = ""
        
        self.url = "https://openrouter.ai/api/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        self.system_prompt = """
        You are a robot task planner controlling a UR3e robot.
        Available skills: "pick", "place", "home".
        Available objects: "red_cube", "yellow_cube", "blue_cube".
        Available zones: "zone_a", "zone_b", "zone_c".
        
        RULES:
        1. Always output ONLY a JSON object containing a "plan" array.
        2. Each element in the array must be an object with "skill" (and "object", "zone" if applicable).
        3. Always end the plan with the "home" skill.
        4. If a Target Layout is provided in the context, you must pick and place the cubes EXACTLY as the layout specified.
        """

    def generate_plan(self, user_command, context=""):
        prompt_content = f"User Command: {user_command}"
        if context:
            prompt_content += f"\nTarget Layout Context: {context}"
            
        # Áp dụng chính xác cấu trúc Payload bạn yêu cầu
        data = {
            "model": "xiaomi/mimo-v2.6-flash",
            "messages": [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt_content}
            ],
            "reasoning": {"enabled": True},
            "provider": {
                "only": [
                    "xiaomi/fp8"
                ],
                "allow_fallbacks": False
            }
        }
        
        try:
            # Thêm timeout để tránh kẹt tiến trình
            response = requests.post(self.url, headers=self.headers, data=json.dumps(data), timeout=30)
            response.raise_for_status()
            
            result = response.json()
            message = result['choices'][0]['message']
            content = message.get('content', '')
            
            # Trích xuất JSON từ chuỗi trả về của AI
            try:
                json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', content, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1)
                else:
                    json_match = re.search(r'\{.*\}', content, re.DOTALL)
                    json_str = json_match.group(0) if json_match else content
                    
                plan_json = json.loads(json_str)
                return plan_json
                
            except json.JSONDecodeError:
                print(f"[LLM ERROR] Không thể parse JSON từ AI. Chuỗi thô:\n{content}")
                return None
                
        except Exception as e:
            print(f"[API ERROR] Lỗi kết nối tới OpenRouter: {e}")
            return None