import numpy as np
import time
import matplotlib.pyplot as plt

from Robotagentlearning import (
    Robot,
    NUM_ROOMS, TREASURE_ROOM, ACTIONS,
    NUM_EPISODES, MAX_STEPS_PER_EPISODE
)

def get_greedy_policy(q_table):
    
    policy = []
    for i in range(NUM_ROOMS):
        
        best_action_index = np.argmax(q_table[i])
        best_action = 'Right' if best_action_index == 1 else 'Left'
        policy.append(f"Room {i:2}: {best_action}")
    return policy

def get_rollout_path(q_table):
   
    path = []
    current_room = 0
    while current_room != TREASURE_ROOM:
        path.append(current_room)
        best_action_index = np.argmax(q_table[current_room])
        best_action = ACTIONS[best_action_index]
        current_room += best_action
    path.append(current_room)
    return path

# --- Main Simulation Execution ---
if __name__ == "__main__":
    robot = Robot()
    
    for episode in range(NUM_EPISODES):
        print(f"\n--- Starting Episode {episode + 1} of {NUM_EPISODES} ---")
        
        episode_log = robot.run_q_learning_episode()
        robot.steps_per_episode.append(len(episode_log))
        
        for step_data in episode_log:
            reward_string = "Reward"
            if step_data['reward'] > 0:
                reward_string = "Treasure! 💰"
            elif step_data['reward'] < -1:
                reward_string = "Trap! ❌"
            
            print(f"   Step {step_data['step']:3}: Robot moves from Room {step_data['from_room']:2} to Room {step_data['to_room']:2}. {reward_string}: {step_data['reward']}")
        
        # End of episode summary
        if len(episode_log) < MAX_STEPS_PER_EPISODE:
            print(f"\nEpisode {episode + 1} finished in {len(episode_log)} steps. Treasure found! 🏆")
        else:
            print(f"\nEpisode {episode + 1} finished. Maximum steps reached ({len(episode_log)}).")

        # Display the current Q-table and policy every 50 episodes for a progress check
        if (episode + 1) % 50 == 0:
            print("\n" + "="*50)
            print(f"Progress Check after Episode {episode + 1}")
            print("="*50)
            print("\n--- Current Q-table ---")
            print("Rooms | Left      | Right    ")
            print("------------------------------")
            for i in range(NUM_ROOMS):
                print(f"   {i:<2}   | {robot.q_table[i, 0]:<9.4f} | {robot.q_table[i, 1]:<9.4f}")
            
            print("\n--- Current Greedy Policy ---")
            for i in range(NUM_ROOMS):
                best_action_index = np.argmax(robot.q_table[i])
                best_action = 'Right' if best_action_index == 1 else 'Left'
                print(f"Room {i:2}: {best_action}")
            
            # Learning Process - Graph of Learning Curve 
            plt.figure(figsize=(10, 6))
            plt.plot(robot.steps_per_episode)
            plt.title("Learning Curve: Steps to Treasure Room vs. Episode")
            plt.xlabel("Episode Number")
            plt.ylabel("Steps Taken")
            plt.grid(True)
            plt.show()

            input("\nPress Enter to continue to the next episode...")

    # --- Final Outputs ---
    print("\n\n" + "="*50)
    print("Simulation Complete. Final Results:")
    print("="*50)

    print("\n--- Final Q-table (16 x 2) ---")
    print("Rooms | Left      | Right    ")
    print("------------------------------")
    for i in range(NUM_ROOMS):
        print(f"   {i:<2}   | {robot.q_table[i, 0]:<9.4f} | {robot.q_table[i, 1]:<9.4f}")

    print("\n--- Final Greedy Policy ---")
    final_policy = get_greedy_policy(robot.q_table)
    for line in final_policy:
        print(line)

    print("\n--- Rollout Demonstration ---")
    final_path = get_rollout_path(robot.q_table)
    print("Sequence of rooms visited:", " -> ".join(map(str, final_path)))