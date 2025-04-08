import gymnasium as gym
from gymnasium import spaces
import pygame
import numpy as np
import math
import time

from SimpleSearch import SimpleSearch
from new_House import House
from Robot import Robot


# Global
dist_threshold = 30


class Game_Env(gym.Env):
    metadata = {"render_modes": ["human", "rgb_array"], "render_fps": 30}

    def __init__(self, render_mode="human", size=512, ran_house=True):
        super().__init__()
        self.render_mode = render_mode
        self.size = size
        self.window = None
        self.clock = None
        self.font = None  # <-- Add font attribute
        self.start_time = 0

        # --- Initialize House and Robot instances ---
        self.robot_start_pos = [40, size // 2 - 10]
        self.house = House(size, self.robot_start_pos, ran_house)
        self.robot = Robot(
            start_pos=self.robot_start_pos,
            start_angle=0.0,
            ray_length=self.house.size * 0.7  # Ensure ray length is based on house size
        )

        # --- Action and Observation Spaces (same as before) ---
        self.action_space = spaces.Discrete(3)
        self.observation_space = spaces.Box(low=0.0, high=1.0, shape=(self.robot.num_rays + 3,), dtype=np.float32)

        # --- Target Finding Parameters ---
        self.target_distance_threshold = self.house.target_size * 50
        # How close is "found"

        self.num_of_failed_moved = 0

    def check_collision_rays(self, rays):  # Keep the existing collision check for reward calculation
        # collision_dist = 0.2
        # count = 0
        # for ray in rays:
        #     if ray / self.robot.ray_length < collision_dist:
        #         count += 1
        # if count >= 3:
        #     return True
        # return False

        collision_dist = 0.2
        for ray in rays:
            if ray / self.robot.ray_length > collision_dist:
                return False
        return True

    def step(self, action):
        prev_location = self.robot.pos

        # 1. Process Action
        if action == 0:
            self.robot.move_forward(self.house.walls)  # Pass walls for collision check inside move_forward
        elif action == 1:
            self.robot.turn_left()
        elif action == 2:
            self.robot.turn_right()

        if self.robot.pos[0] == prev_location[0] and self.robot.pos[1] == prev_location[1]:
            self.num_of_failed_moved += 1
        else:
            self.num_of_failed_moved = 0

        # 2. Calculate Rays and Observation
        rays = self.robot.cast_rays(self.house.walls)

        # 3. Check for Collision (AFTER movement, for reward calculation)
        collision = self.check_collision_rays(rays)

        # 4. Check if Target Found
        target_found, distance_from_target, target_in_direction, rays = self._check_target_found(rays)

        # 4. normalize
        rays = np.array(rays, dtype=np.float32) / self.robot.ray_length  # Normalize

        # 6. Calculate Reward
        reward = self._calculate_reward(collision, target_found, distance_from_target, rays)

        # 7. Determine if Done
        terminated = target_found and (
                    distance_from_target <= dist_threshold)  # Episode ends only when target is found now
        truncated = False  # No truncation for now
        info = {"rays": rays, "target_found": target_found, "collision": collision}  # Add collision info

        # 8. set up obs:
        obs = np.append(rays, [1 if target_found else 0, target_in_direction, self.num_of_failed_moved])

        #9. render if necessary
        if self.render_mode == "human":
            self.render()

        # print(">target: ", target_found, "> collision: ", collision, "> target dir: ", target_in_direction)

        return obs, reward, terminated, truncated, info

    def reset(self, seed=None, options=None):
        super().reset(seed=seed, options=options)
        self.robot.pos = np.array(self.robot_start_pos, dtype=np.float32)
        self.robot.angle = 0.0
        # Re-place target on reset (optional, can be fixed if you want target to stay in same place)
        rays = self.robot.cast_rays(self.house.walls)
        target_found, distance_from_target, target_in_direction, rays = self._check_target_found(rays)
        rays = np.array(rays, dtype=np.float32) / self.robot.ray_length  # Normalize
        obs = np.append(rays, [1 if target_found else 0, target_in_direction, self.num_of_failed_moved])

        # --- Start Timer ---
        self.start_time = time.time()

        if self.render_mode == "human":
            self.render()

        return obs, {}

    def render(self):
        if self.render_mode is None:
            gym.logger.warn(
                "You are calling render method without specifying any render mode. "
                "You may experience issues when calling .step()."
            )
            return

        if self.window is None and self.render_mode == "human":
            pygame.init()
            pygame.display.init()
            pygame.font.init()
            self.window = pygame.display.set_mode((self.size, self.size))
            self.font = pygame.font.SysFont(None, 30)
        if self.clock is None:
            self.clock = pygame.time.Clock()

        canvas = pygame.Surface((self.size, self.size))
        canvas.fill((255, 255, 255))  # white background

        # Draw House elements
        self.house.draw(canvas)

        # Cast rays to get lengths for drawing
        rays = self.robot.cast_rays(self.house.walls)
        target_found, distance_from_target, target_in_direction, rays = self._check_target_found(rays)
        # Draw Robot and Rays
        self.robot.draw(canvas, rays)

        # --- Draw Timer ---
        if self.start_time is not None and self.render_mode == "human":
            elapsed_time = time.time() - self.start_time
            timer_text = f"Time: {elapsed_time:.2f}s"
            text_surface = self.font.render(timer_text, True, (0, 0, 0))  # Black color
            canvas.blit(text_surface, (10, 10))  # Position at top-left

        if self.render_mode == "human":
            self.window.blit(canvas, canvas.get_rect())
            pygame.event.pump()
            pygame.display.flip()
            self.clock.tick(self.metadata["render_fps"])
        else:  # rgb_array
            return np.transpose(
                np.array(pygame.surfarray.pixels3d(canvas)), axes=(1, 0, 2)
            )

    def close(self):
        if self.window is not None:
            pygame.display.quit()
            pygame.font.quit() # <-- Quit font module
            pygame.quit()
            self.window = None  # Reset window state
            self.clock = None  # Reset clock state
            self.font = None  # Reset font state

    def _calculate_reward(self, collision, target_found, distance_from_target, rays):
        if collision:
            return -20
        elif self.num_of_failed_moved >= 3:
            return -10
        elif target_found:
            if distance_from_target > dist_threshold:
                return -1
            else:
                return 1000
        return -5

    def signed_angle_between(self):
        robot_pos = self.robot.pos
        target_pos = self.house.target_pos
        robot_angle_degrees = self.robot.angle

        # 1. Vector from robot to target in world coordinates
        vec_to_target_world = target_pos - robot_pos

        # 2. Distance to target
        distance_to_target = np.linalg.norm(vec_to_target_world)

        # 3. Angle to target in world coordinates (radians)
        angle_to_target_radians_world = math.atan2(vec_to_target_world[1], vec_to_target_world[0])

        # 4. Convert robot's angle to radians
        robot_angle_radians = math.radians(robot_angle_degrees)

        # 5. Calculate relative angle (angle in robot's coordinate system)
        angle_to_target_radians_relative = angle_to_target_radians_world - robot_angle_radians

        # 6. Convert relative angle to degrees and normalize to [-180, 180]
        angle_to_target_degrees_relative = math.degrees(angle_to_target_radians_relative)

        # Normalize angle to be within -180 to 180 degrees (or -pi to pi radians) - Redundant as atan2 already returns value in range -pi to pi
        angle_to_target_degrees_relative = (angle_to_target_degrees_relative + 180) % 360 - 180

        return distance_to_target, angle_to_target_degrees_relative

    def _check_target_found(self, rays):
        distance_to_target, angle_vec = self.signed_angle_between()

        # Get ray directions
        num_rays = self.robot.num_rays
        fov = self.robot.fov
        angle_increment = fov / (num_rays - 1) if num_rays > 1 else 0
        start_angle = 0 - fov / 2

        target_found_by_ray = False  # Flag to track if target is found by ray
        target_in_direction = 400

        # for i in range(int(len(rays)/2)-1, int(len(rays)/2)+1):  # Iterate through rays and their directions
        for i in range(len(rays)):  # Iterate through rays and their directions
            ray_angle = start_angle + i * angle_increment

            if abs(ray_angle - angle_vec) < 1.5:  # Adjust threshold (0.9 means quite aligned)
                # print(f"Debug: Ray {i} direction similarity to target: {angle_vec:.3f}, {ray_angle:.3f} - Passed threshold")  # Debug print 2

                # 3. Check for wall intersections along this ray *before* reaching target
                intersection_point = (rays[i] >= distance_to_target)  # here add intersection of ray with target
                if intersection_point:
                    target_found_by_ray = True  # Set the flag to True TODO remove comment out
                    rays[i] = distance_to_target
                    # print(f"Debug: Ray {i} target intersection found. Distance to target: {distance_to_target:.2f}")  # Debug print 3
                    if abs(target_in_direction) > abs(ray_angle):
                        target_in_direction = ray_angle

        if target_found_by_ray:
            return True, distance_to_target, target_in_direction, rays  # Target found by ray AND within distance
        else:
            return False, math.inf, 0, rays

# if __name__ == "__main__":
#     env = Game_Env(render_mode="human", ran_house=False)
#     obs, _ = env.reset()
#
#     for _ in range(1000):
#         action = env.action_space.sample()  # random actions
#         obs, reward, terminated, truncated, info = env.step(action)
#
#         if terminated:
#             if info.get('target_found', False):
#                 print("Target Found!")
#             obs, _ = env.reset()
#         if truncated:
#             obs, _ = env.reset()
#
#     env.close()

# --- Parameters ---
render_simple_algo = True # Set to True to watch the simple algo, False for faster runs
num_episodes = 20         # Number of runs for averaging time
max_steps_per_episode = 3000 # Max steps before considering episode timed out (truncated)
use_random_house = True   # True=new house each episode, False=same house layout
env_size = 512            # Size parameter for Game_Env

if __name__ == "__main__":
    print("Starting SimpleSearch Algorithm Test...")

    # --- Environment Setup ---
    # Uses the unmodified Game_Env class
    env = Game_Env(render_mode="human" if render_simple_algo else None,
                   ran_house=use_random_house,
                   size=env_size)

    # --- Simple Algorithm Setup ---
    # Pass the environment's spaces to the agent's constructor
    simple_agent = SimpleSearch(env.observation_space, env.action_space)

    # --- Simulation Loop ---
    episode_times = []
    success_count = 0
    total_steps = 0

    for i in range(num_episodes):
        print(f"\n--- Episode {i+1}/{num_episodes} ---")
        obs, info = env.reset()
        start_time = env.start_time # Get start time recorded by env during reset
        terminated = False
        truncated = False
        step_count = 0
        episode_done = False

        while not episode_done:
            # Get action from the simple algorithm's predict method
            action, _ = simple_agent.predict(obs) # We only need the action

            # Step the environment
            try:
                obs, reward, terminated, truncated, info = env.step(action)
                step_count += 1
                total_steps += 1
            except Exception as e:
                print(f"!! Error during env.step on step {step_count}: {e}")
                import traceback
                traceback.print_exc()
                truncated = True # End episode on error

            # Check for episode end conditions
            episode_done = terminated or truncated

            # Check for timeout based on steps
            if step_count >= max_steps_per_episode and not episode_done:
                print(f"Episode truncated at step {step_count} due to max steps.")
                truncated = True
                episode_done = True

            # Optional delay for human viewing if rendering is enabled
            if render_simple_algo:
                # time.sleep(0.01) # Uncomment to slow down rendering
                pass

        # --- Episode End ---
        end_time = time.time()
        duration = end_time - start_time

        if terminated:
            print(f"Target Found! Duration: {duration:.2f} seconds, Steps: {step_count}")
            episode_times.append(duration)
            success_count += 1
        elif truncated:
             # Check if truncation was due to timeout or other reason (like error)
             if step_count >= max_steps_per_episode:
                 print(f"Episode Timed Out. Duration: {duration:.2f} seconds, Steps: {step_count}")
             else:
                 print(f"Episode Truncated (possibly due to error). Duration: {duration:.2f} seconds, Steps: {step_count}")
        else:
             # This case shouldn't normally be reached if episode_done logic is correct
             print(f"Episode ended without termination or truncation? Duration: {duration:.2f}s, Steps: {step_count}")


    # --- Final Results ---
    env.close() # Important to close the environment window
    print("\n--- SimpleSearch Algorithm Final Results ---")
    print(f"Ran {num_episodes} episodes.")
    print(f"Total steps across all episodes: {total_steps}")
    print(f"Target found successfully in {success_count} episodes ({success_count/num_episodes*100:.1f}% success rate).")

    if episode_times: # Calculate stats only if there were successful episodes
        average_time = np.mean(episode_times)
        std_dev_time = np.std(episode_times)
        min_time = np.min(episode_times)
        max_time = np.max(episode_times)
        print(f"\nStatistics for {success_count} SUCCESSFUL episodes:")
        print(f"  Average time: {average_time:.2f} seconds")
        print(f"  Standard deviation: {std_dev_time:.2f} seconds")
        print(f"  Min time: {min_time:.2f}s, Max time: {max_time:.2f}s")
    elif num_episodes > 0:
        print("\nTarget was not found successfully in any episode.")

    print("\nCompare these results (average time, success rate) with your A2C agent's performance.")