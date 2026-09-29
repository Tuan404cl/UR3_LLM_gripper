import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'ur3_llm_control'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        # Copy file launch
        (os.path.join('share', package_name, 'launch'), glob(os.path.join('launch', '*launch.[pxy][yma]*'))),
        # Copy các file mô hình URDF
        (os.path.join('share', package_name, 'urdf', 'cubes'), glob('urdf/cubes/*.urdf')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Your Name',
    maintainer_email='your.email@todo.todo',
    description='LLM Planner for UR3e',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'skill_executor = ur3_llm_control.skill_executor:main',
            'zone_visualizer = ur3_llm_control.zone_visualizer:main', 
        ],
    },
)