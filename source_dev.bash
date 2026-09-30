# Source this file in each terminal to use the live Python package in src.
# Usage: source source_dev.bash

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    echo "Run this with: source ${BASH_SOURCE[0]}" >&2
    exit 2
fi

_ur3_repo_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
_ur3_workspace_root="$(cd -- "${_ur3_repo_root}/../.." && pwd)"
_ur3_ros_distro="${ROS_DISTRO:-humble}"

if [[ -f "/opt/ros/${_ur3_ros_distro}/setup.bash" ]]; then
    source "/opt/ros/${_ur3_ros_distro}/setup.bash"
fi

if [[ -f "${_ur3_workspace_root}/install_symlink/setup.bash" ]]; then
    source "${_ur3_workspace_root}/install_symlink/setup.bash"
elif [[ -f "${_ur3_workspace_root}/install/setup.bash" ]]; then
    source "${_ur3_workspace_root}/install/setup.bash"
else
    echo "Không tìm thấy install/setup.bash trong ${_ur3_workspace_root}; hãy build workspace trước." >&2
    unset _ur3_repo_root _ur3_workspace_root _ur3_ros_distro
    return 1
fi

_ur3_python_source="${_ur3_repo_root}/src/ur3_llm_control"
export PYTHONPATH="${_ur3_python_source}${PYTHONPATH:+:${PYTHONPATH}}"

unset _ur3_repo_root _ur3_workspace_root _ur3_ros_distro _ur3_python_source
