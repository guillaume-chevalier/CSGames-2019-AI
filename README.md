# Artificial Intelligence

This is our team's code for the competition at the CS Games 2019. 

Solution: Deep Reinforcement Learning.
- Inputs to the ML pipeline: featurized game state, action to do, predicted resulting game state. 
- Outputs to the ML pipeline: probability to win the game by doing that move. 

Because the action is an input to the deep reinforcement learning algorithm, one must try every actions (with all of their guessed resulting game state) and choose the one that maximizes the probability to play the game. 

Ironically enough, we manually did a simulated annealing by changing the random value in the choice of the best action throughout training by stopping training, changing the value in the code, and resuming training (the random that is added in the function that choose which action to take). 

Our algorithm is all coded in [this file](competition/agent/data_builder.py). You need the pickles (.pkl) and the json files (.json) in the subfolders for the algorithm to work, because it has been trained.  

We may have failed submitting the solution properly on time at the end of the competition by submitting a corrupted zip file by error. Anyways, this is our solution. 

Enjoy!
