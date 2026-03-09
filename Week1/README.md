# Brief description of Week 1 lab
In this lab basic Linux commands and fundamental ROS 2 concepts were practiced. A ROS 2 workspace was created and a Python package named Adil_First_Pkg was developed. A simple ROS 2 node was written that prints a message when executed. The package was built using colcon and the node was executed using ros2 run.

# Commands used
## 1
ros2 --version
## 2
source /opt/ros/humble/setup.bash
## 3
mkdir -p ~/ros2_ws/src
## 4
cd ~/ros2_ws
## 5
colcon build
## 6
source install/setup.bash
## 7
ros2 pkg create --build-type ament_python my_first_pkg
## 8
ros2 pkg list | grep my_first_pkg
## 9
chmod +x simple_node.py
## 10
ros2 run my_first_pkg simple_node

# Problems faced and solutions
## Setup.py naming issue
The console script entry point was written incorrectly at first so the node did not run. The problem was solved by correcting the executable mapping in setup.py.
## Forgot to run colcon build
After editing files the changes did not appear. Running colcon build again fixed the issue.
## Workspace not sourced
ROS 2 could not detect the package. Running source install/setup.bash solved the problem.
## Wrong directory placement
The node file was initially created in the wrong location. Moving it inside the my_first_pkg folder fixed the structure.
## File permission issue
The Python node was not executable. Using chmod +x simple_node.py solved the problem.

# Reflection
This lab provided a basic understanding of the ROS 2 development workflow. 
I learned how to create a workspace and organize packages correctly. 
Writing and running a node helped me understand how ROS 2 executes programs through registered entry points. 
I also practiced important Linux terminal commands required for robotics development. 
Troubleshooting build and environment issues improved my ability to identify and fix common problems. 
This lab created a strong foundation for future labs involving node communication and more advanced ROS 2 features.
