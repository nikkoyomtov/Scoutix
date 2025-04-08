# 💡 Scoutix
Autonomous Navigation and Object Detection Robot for Indoor Environments

<!-- cool project cover image -->
![Project Cover Image](/media/project-cover-img.jpg)

<!-- table of content -->
## Table of Contents
- [The Team](#the-team)
- [Project Description](#project-description)
- [Getting Started](#getting-started)
- [Prerequisites](#prerequisites)
- [Installing](#installing)
- [Testing](#testing)
- [Deployment](#deployment)

## 👥 The Team 
**Team Members**
- [Roy Platzky](roy.platzky@mail.hujia.ac.il)
- [Neriah Yomtov](neriah.yomtov@mail.huji.ac.il)

**Mentor & Advisor**
- **MSc Hadar Tal at Senior Lecturer Oron Sabag’s ‘Reinforcement Learning Algorithms for Robotics’ Lab**


## 📚 Project Description
Our proposed solution is an AI-powered autonomous robot designed to navigate complex indoor environments and efficiently detect specified objects.
- Real-time sensor data (e.g., cameras, depth sensors) to understand the robot's surroundings.
- Image processing-based object detection models to identify target objects with precision.
- Reinforcement learning-based navigation policies to enable adaptive and optimal path planning.


## ⚡ Getting Started

These instructions will give you a copy of the project up and running on
your local machine for development and testing purposes. 

### 🧱 Prerequisites
Requirements for the software and other tools to build, test and push 
- [Python 3.9](https://www.python.org/downloads/release/python-3920/)
- [Gymnasium - A toolkit for developing and testing RL algorithms](https://gymnasium.farama.org/)

### 🏗️ Installing
A step by step series of examples that tell you how to get a development environment running

Clone the repository:

    git clone https://github.com/nikkoyomtov/Scoutix.git

Navigate to the project directory:

    cd Scoutix

Install the required dependencies:

    pip install -r requirements.txt
    
## 🧪 Testing
To test the functionalities of this project, we’ve included a test_policy.py script. This script allows you to evaluate and test different policies integrated into the project.

### Sample Tests
The test_policy.py script can be used to test various policies implemented in the project.

For a well-performing policy: This policy has been designed or trained to perform effectively within the environment. Use "p_2_vec_normalize.pkl".

A "simple" baseline policy: This is a non-reinforcement learning (non-RL) policy, included for comparison to highlight the improvements provided by the more sophisticated RL-based policies. Use "p_4_vec_normalize.pkl"

## 🚀 Deployment
Once your system is up and running, you have the flexibility to experiment with and create various policies by modifying the variables in the A2C algorithm. This enables you to customize the behavior of the AI agent to suit different use cases or improve its performance within the environment.
