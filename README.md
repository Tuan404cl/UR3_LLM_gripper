## Chạy ở chế độ phát triển

Build một luồng và bật symlink-install:

```bash
cd ~/tuan_ws
MAKEFLAGS=-j1 CMAKE_BUILD_PARALLEL_LEVEL=1 colcon --log-base log_symlink build \
  --build-base build_symlink --install-base install_symlink \
  --symlink-install --parallel-workers 1
```

Package Python `ur3_llm_control` hiện được colcon cài thành bản copy với phiên bản setuptools đang dùng. Để Python lấy code trực tiếp từ `src` mà không cần build lại sau mỗi lần sửa, source helper trong **mỗi terminal mới**:

```bash
cd ~/tuan_ws/src/UR3_LLM_gripper
source source_dev.bash
```

Terminal 1 mở MoveIt/RViz:

```bash
ros2 launch ur3_llm_control llm_robot.launch.py
```

Terminal 2 chạy bộ nhận lệnh ngôn ngữ tự nhiên:

```bash
ros2 run ur3_llm_control skill_executor
```

Sau khi sửa file Python, thoát và chạy lại tiến trình Python để nó import code mới. Với helper trên không cần build lại cho các thay đổi trong package Python. Thay đổi launch file hoặc file cài vào `share` vẫn cần build lại.

Khi không có Internet, có thể nhập `test` ở terminal của `skill_executor` để chạy kịch bản dựng sẵn.
