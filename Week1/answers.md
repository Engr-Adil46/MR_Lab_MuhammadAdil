# 1

## Node
A node is a running process in ROS 2 that carries out a given activity such as sensing, controlling, or computing data.
## Topic
A topic is a communication path that nodes use to exchange messages.
## Package
A package is a folder that contains ROS 2 code, configuration files, dependencies, and build information.
## Workspace
A workspace is a development folder that contains ROS 2 packages along with build, install, and log directories.

# 2 Why sourcing is necessary
Sourcing loads environment variables so ROS 2 can locate packages and executables in the workspace. If the workspace is not sourced, ROS cannot detect newly built packages. Commands such as ros2 run or ros2 pkg list will not find the package.

# 3 Purpose of colcon build
colcon build compiles and installs all ROS 2 packages in the workspace so they can run in ROS 2.
It generates these folders.
## src
Contains package source code.
## build
Contains intermediate build files.
## install
Contains installed packages and executables.
## log
Contains build logs.

# 4 Purpose of entry-points console script in setup.py
The console script connects a command name with a Python function. When ros2 run package executable is used, ROS 2 checks setup.py to determine which Python file and function should run. This allows the node to execute as a ROS 2 command.

## 5 Publisher/Subscriber Diagram
Node A (Publisher) --->(Topic)---> Node B (Subscriber)
