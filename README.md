# Smart Adaptive Lighting System
Final project for the course Redes e Sistemas Autónomos (Autonomous Networks and Systems) 2023.</br>

## Infrastructure and Communication  ##

The advent of Intelligent Transportation Systems (ITS) presents a unique opportunity to re-imagine infrastructure for greater safety and energy efficiency. </br> </br>
We have devised a system that uses a limited number of Road-Side Units (RSUs), integrated into selected smart lamp posts, to process Cooperative Awareness Messages (CAMs) from vehicles’ On-Board Units (OBUs), that dynamically **adjusts road lighting** based on vehicle presence, speed, and proximity. </br> </br>
An integral part of our system is the use of V2I communication technology. Our goal is to effectively leverage this technology, utilizing the ETSI C-ITS protocol through the NAP-Vanetza network stack, for seamless transmission and processing of information. </br> </br>

## Cost-efficiency ## 

In the interest of cost-efficiency, another objective is to create a system that works effectively with a mix of RSU-equipped and internet-only lamp posts (these ”internet-only” lamp posts only need a small computational unit to process data from an active connection to the RSUs network). </br> </br>
This involves designing a communication model where LSMs (our novel Light Support Messages) can be relayed effectively to both types of lamp posts. 

## System Architecture ##
![rsa_architecture](https://github.com/jp-amaral/Adaptive-Lighting-System/assets/80011136/edaf9b0c-8257-407a-9e24-a7462619691c)

## Challenges and Solutions ##

*  **Light Intensity Calculation**: The challenge was to create a formula that maps speed, distance, and arrival time to the right light intensity level, considering a bias. The solution was an equation that inversely correlates arrival time with light intensity, with a bias multiplier for varying light rates among posts in the same conditions.

*  **Optimization of Resources**: A significant challenge was resource and bandwidth optimization, especially for larger messages. The solution involved restricting light intensity computation to nearby posts based on a dynamic radius parameter during program execution.

*  **Multiple OBUs Interaction**: Introducing multiple OBUs caused lights to flicker due to conflicting intensity orders from different RSUs. To address this, a feature was implemented where an RSU sends an LSM message with -1 intensity when out of OBU range, triggering the removal of the RSU from the order list and recalculating light intensity based on the remaining RSUs.

*  **Script Unification**: To handle any number of OBUs and RSUs, we created a single Python script for both. This approach enables us to run the same program with customized parameters for each OBU or RSU in the system, making it versatile and scalable.


## Results ##

The Smart Adaptive Lighting System has been successfully developed and implemented, achieving all the set project objectives. Notably, the system has shown remarkable robustness and adaptability, effectively handling complex scenarios with multiple OBUs in a given zone.
