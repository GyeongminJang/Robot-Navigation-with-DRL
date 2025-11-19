# Robot Navigagtion with DRL

### Comparative Evaluation of DRL Methodologies in Environments with Multiple Dynamic Objects of High Dynamic Complexity

## **1. Backgrounds and Purposes**

* As the importance of autonomous robots grows, there is a demand for safe and reliable path planning in complex environments.
* Existing navigation algorithms have limitations in handling environmental changes and interacting with pedestrians.
* Utilizing the latest deep reinforcement learning (DRL) algorithms to improve safety and success rates compared to existing methods.
* Validating model performance in simulations with realistic scenarios using datasets incorporating social interactions.

## **2. Simulation Environment Settings**
* Using ROS2 + Gazebo simulation tools
* Implementing LiDAR and Odometry on the robot
* Applying real indoor environments and moving obstacles using the SiT Dataset
* Creating three maps: Hallway for training, Courtyard and Looby for testing

## **3. DRL Algorithms**
* DQN: The first DRL algorithm combining deep learning and Q-learning
* DDPG: An Actor-Critic-based DRL algorithm for continuous actions
* TD3: An improved DDPG algorithm enhancing stability with two critics

## **4. Ornstein-Uhlenbeck Process**
$$
x_{t+1} = x_t + \theta(\mu - x_t) + \sigma \cdot \mathcal{N}(0,1)
$$



## **5. TD3 Parameters**


## **6. Reawrd Functions**


## **7. Experiment Procedure**


## **8. Experiment Results**



## **9. Conclusion**


## **10. References**
1) [Official Paper on DRL Robot Navigation](https://scifiniti.com/3104-4719/1/2024.0003) or the [GitHub repository](https://github.com/tomasvr/turtlebot3_drlnav.git).
2) [SiT Dataset official page](https://spalaboratory.github.io/SiT/) or the [GitHub repository](https://github.com/SPALaboratory/SiT-Dataset).
