import numpy as np
import time

# --- 1. Environment and Parameters ---
NUM_ROOMS = 16
TREASURE_ROOM = 15
TRAP_ROOM = 7
ACTIONS = [-1, 1]  # Left, Right

ALPHA = 0.1
GAMMA = 0.9
EPSILON = 0.2
NUM_EPISODES = 500
MAX_STEPS_PER_EPISODE = 200

# --- 2. Q-Learning Implementation ---

def get_next_state_and_reward(room, action_index):
    
    action_value = ACTIONS[action_index]
    next_room = room + action_value
    reward = -1  # Energy cost
    
    if next_room == TREASURE_ROOM:
        reward += 10
    elif next_room == TRAP_ROOM:
        reward += -5
    elif next_room < 0 or next_room >= NUM_ROOMS:
        next_room = room
        reward = -1 # A move that doesn't change position still costs energy
    
    return next_room, reward

class Robot:
    def __init__(self):
        self.q_table = np.zeros((NUM_ROOMS, len(ACTIONS)))
        self.steps_per_episode = []

    def run_q_learning_episode(self):
        
        current_room = 0
        steps = 0
        episode_log = []
        
        while current_room != TREASURE_ROOM and steps < MAX_STEPS_PER_EPISODE:
            # Epsilon-greedy action selection
            if np.random.uniform(0, 1) < EPSILON:
                action_index = np.random.randint(0, len(ACTIONS))
            else:
                action_index = np.argmax(self.q_table[current_room])
                
            next_room, reward = get_next_state_and_reward(current_room, action_index)
            
            # Q-Learning update rule
            old_q_value = self.q_table[current_room, action_index]
            if next_room == TREASURE_ROOM:
                max_future_q = 0 # Episode ends
            else:
                max_future_q = np.max(self.q_table[next_room])
                
            new_q_value = old_q_value + ALPHA * (reward + GAMMA * max_future_q - old_q_value)
            self.q_table[current_room, action_index] = new_q_value
            
            # Log the step, reward, and action
            episode_log.append({
                'step': steps + 1,
                'from_room': current_room,
                'to_room': next_room,
                'action': ACTIONS[action_index],
                'reward': reward
            })
            
            current_room = next_room
            steps += 1
        
        return episode_log