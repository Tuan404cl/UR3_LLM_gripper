cd ~/ur3e_ws
colcon build
source install/setup.bash

ter1
ros2 launch ur3_llm_control llm_robot.launch.py
ter2
ros2 run ur3_llm_control skill_executor
Demo: https://drive.google.com/file/d/1ak0sozop2ywob3BppOx0Dmt_AR-KIuPf/view?usp=sharing
Trong trường hợp không thể kết nối internet đã có sẵn kịch bản để test bằng cách sử lệnh :"test"
