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

x_{t+1} = x_t + \theta(\mu - x_t) + \sigma \cdot \mathcal{N}(0,1)

**(오류 해결해야 함.)**

x_t is the state at time t, μ is the value to which the process converges in the long run, θ is the rate of return to the mean μ, σ is the volatility of the noise term, and “𝒩(0,1)” is a Gaussian random variable.


**To aid exploration in continuous action spaces, generate smooth noise over time.**

1) **Max_sigma**: The maximum noise level applied during the initial exploration phase, representing the magnitude of uncertainty imposed on the action
2) **Min_sigma**: Ensure that noise does not completely disappear even as learning progresses, while maintaining minimal searchability
3) **Decay_Period**: The period during which noise intensity decays from max_sigma to min_sigma

## **5. TD3 Parameters**
**Target Policy Smoothing**: Adding random noise to target actions for more robust policy learning and preventing overfitting

**Policy Delayed Update**: Updating the Actor network after the Critic network is sufficiently trained to reduce learning instability

1) **Policy_noise**: The magnitude of policy smoothing noise added to the Target Actor's actions
2) **Policy_noise_clip**: Limit noise values to prevent sudden fluctuations
3) **Policy_update_frequency**: Update Cycle for Actor and Target Networks

## **6. Reawrd Functions**
All rewards except 𝒓_𝒕𝒆𝒓𝒎𝒊𝒏𝒂𝒍, which is applied once at episode end, are calculated at each step; the final reward is the sum of these elements

1) **DRL-1**: Added distance difference reward and direction alignment reward to prevent ‘unnecessary circular motion in place’ frequently occurring in complex environments
2) **DRL-2**: Resolved circular drift and local optimum issues through rotation suppression, straight-line behavior induction, and strengthened action-specific incentive structure

## **7. Experiment Procedure**

**The entire process of one simulation run**

1) Select and execute one DRL algorithm (DQN, DDPG, TD3)
2) Observe step: 200,000 steps
3) Subsequently train the robot for 8,000 episodes
4) After training, test the robot for 2,000 episodes
5) After 2,000 test episodes, record the evaluation metrics from the log (success rate, timeouts, distance traveled, etc.)

※ Training Map: Hallway Map
※ Test Map: Courtyard and Looby Map
※ Total simulation time: approximately 16 hours for training + 2 hours for testing (with speedup applied)


## **8. Experiment Results**
<p align="center">
SR= Success Rate, CW= Static Obstacle Collision Rate, CD= Dynamic Obstacle Collision Rate
</p>
<p align="center">
TO= Time Out, TB= Robot Tilt, Dist= Travel Distance
</p>
<p align="center">
Travel Distance Unit: [m], Remaining Elements Unit: [%]
</p>

### **1) Ornstein-Uhlenbeck Process Adjustment (Based on TD3-1)**

### **2) TD3 Parameters Adjustment (Based on TD3-1)**

### **3) Results on the Courtyard map after adjustment**

### **4) Results on the Lobby map after adjustment**


<p align="center">
Left top: outcomes, Right top: critic loss
</p>
<p align="center">
Left bottom: actor loss, Right bottom: reward
</p>
### **1) Learning graph results for the DQN algorithm**

### **2) Learning graph results for the DDPG algorithm**

### **3) Learning graph results for the TD3 algorithm**


## **9. Conclusion**
* Improved autonomous driving performance of robots using DRL algorithms through adjustments to noise, parameters, and reward functions

* Application of the latest DRL algorithm TD3 improved success rate and stability compared to existing methods (DQN, DDPG)

* Demonstrated the ability to enhance robot autonomous driving reliability even in complex and dynamic environments

* Proposed follow-up tasks including application in real-world environments beyond simulation and strengthening social interactions

## **10. References**
1) [Official Paper on DRL Robot Navigation](https://scifiniti.com/3104-4719/1/2024.0003) or the [GitHub repository](https://github.com/tomasvr/turtlebot3_drlnav.git).
2) [SiT Dataset official page](https://spalaboratory.github.io/SiT/) or the [GitHub repository](https://github.com/SPALaboratory/SiT-Dataset).
