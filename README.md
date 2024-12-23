# Maze-Exploration-Robot
We tried to implement a maze exploration robot, we assume that there is a target object(cup) in a checkered maze, the robot need to find it and issue a warning.  
We just simply implement the robot with a raspberry pi, a AlphaBot2-Pi(autonomous car), camera, and ultrasound sensor, and it can find the target object and go out the maze.  
In the process of exiting the maze, we adopt two algorithm: Wall Follower, Depth-First-Search, detecting distance and object using ultrasound sensor and YOLOv5s.  

## Hardware
* Raspberry Pi 4  
  ![Raspberry Pi 4](readmefiles/raspberrypi.png)
* AlphaBot2-Pi (with Picamera V2 and ultrasonic sensor)  
  ![AlphaBot2-Pi](readmefiles/AlphaBot2-Pi.png)

## Software
* Raspberry Pi OS
* Python
* PyTorch
* OpenCV
* YOLOv5

## Methodology
### Object Detection
Object Detection is for finding the target object in the maze. We implement the object detection function with YOLOv5s, because it doesn’t need high computational performance, performing well in detection speed, and it also can maintain good accuracy.  
![YOLOv5 Compare](readmefiles/YOLOv5_compare.png)

### Maze Exploration
1. Wall Follower  
Maze-solving algorithm with spatial mapping capability. The maze-solving method is based on the wall-following rule.  
If the maze is simply connected, meaning all the walls in the maze are connected to the outer boundary of the maze, then by continuously advancing while keeping one hand on the wall, it is guaranteed that you will reach the exit of the maze without getting lost.  
![Wall Follower](readmefiles/Wall%20Follower%20Algorithm.png)

2. Depth-First-Search
Depth-First-Search (DFS) is an algorithm for traversing or searching tree or graph data structures. Starting from the root node, it explores as far as possible along each branch before backtracking. It’s useful for finding paths and solving puzzles like mazes due to its systematic exploration of nodes and paths, ensuring all possible routes are considered.  

## Experiment Results
### Object Detection
![Object Detection Cup](readmefiles/object%20detection%20cup.png)
![Object Detection Ball](readmefiles/object%20detection%20ball.png)

### Maze Exploration
![Warning1](readmefiles/warning1.gif)
![Warning2](readmefiles/warning2.gif)