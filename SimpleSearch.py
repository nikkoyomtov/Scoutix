import numpy as np
import math

import numpy as np
import math # Keep math import if needed elsewhere, not strictly needed in this class anymore

class SimpleSearch:
    """
    A simple rule-based policy for navigating the Game_Env.
    Mimics the predict method of a Stable Baselines3 policy.
    CORRECTED: Uses observation values directly as provided by the unmodified Game_Env.
    Observation format assumed:
    [ray1(norm), ..., rayN(norm), target_found(0/1), target_angle(degrees), failed_moves(count)]
    """
    def __init__(self, observation_space, action_space):
        self.observation_space = observation_space
        self.action_space = action_space
        # Extract number of rays from observation space shape
        # Shape is (num_rays + 3,)
        self.num_rays = observation_space.shape[0] - 3

        # --- Tunable Parameters ---
        self.target_angle_threshold = 15.0  # Degrees: If target angle is within this, move forward
        self.wall_proximity_threshold = 0.15 # Normalized distance: If front ray is below this, turn
        self.stuck_threshold = 3            # Number of failed FORWARD moves before forcing a turn
        self.side_clearance_hysteresis = 0.05 # Turn towards side that is *significantly* clearer
        # --- End Tunable Parameters ---

        # --- Calculate Ray Indices ---
        self.front_ray_indices = self._get_front_ray_indices()
        self.left_ray_indices = self._get_left_ray_indices()
        self.right_ray_indices = self._get_right_ray_indices()

        # Optional: Print calculated indices for verification
        print(f"--- SimpleSearch Initialized ---")
        print(f"  Num Rays: {self.num_rays}")
        print(f"  Front Indices: {self.front_ray_indices}")
        print(f"  Left Indices: {self.left_ray_indices}")
        print(f"  Right Indices: {self.right_ray_indices}")
        print(f"  Params: TargetAngle={self.target_angle_threshold}, WallProx={self.wall_proximity_threshold}, StuckThresh={self.stuck_threshold}")
        print(f"---------------------------------")


    def _get_front_ray_indices(self):
        # Define 'front' as the center ray(s)
        center_index = self.num_rays // 2
        # Example: Use center 3 rays if possible (adjust width as needed)
        width = 1 # rays to each side (0=center only, 1=3 rays, 2=5 rays etc.)
        start = max(0, center_index - width)
        end = min(self.num_rays, center_index + width + 1)
        indices = list(range(start, end))
        # Handle edge case of very few rays (e.g., 1 or 2)
        if not indices and self.num_rays > 0:
            indices = [center_index] # Use center if list is empty
        return indices

    def _get_left_ray_indices(self):
         # Indices representing roughly the front-left quarter (e.g., 0 to N/4)
         # Ensure indices are valid and list is not empty if possible
         end_index = max(1, self.num_rays // 4) # At least index 0 if num_rays > 0
         indices = list(range(0, end_index))
         return indices

    def _get_right_ray_indices(self):
        # Indices representing roughly the front-right quarter (e.g., 3N/4 to N-1)
        # Ensure indices are valid and list is not empty if possible
        start_index = min(self.num_rays - 1, 3 * self.num_rays // 4) # Ensure start index is valid
        indices = list(range(start_index, self.num_rays))
        # Handle case where start_index might be num_rays if num_rays is small
        if not indices and self.num_rays > 0:
            indices = [self.num_rays - 1] # Use last ray if list is empty
        return indices

    def predict(self, observation, deterministic=True):
        """
        Predicts an action based on simple rules using raw values from observation.

        Args:
            observation (np.ndarray): The observation from the environment.
                Format: [rays(norm)..., target_found(0/1), target_angle(deg), failed_moves(count)]
            deterministic (bool): Ignored in this simple policy, always deterministic.

        Returns:
            tuple: (action, None), mirroring SB3 policy output format.
                   action is int: 0 (forward), 1 (left), 2 (right)
        """
        # --- Unpack Observation ---
        # Assumes env provides observation in the specified format
        rays_normalized = observation[:self.num_rays]           # Normalized [0, 1]
        target_found = observation[self.num_rays] > 0.5         # Boolean flag (0 or 1)
        target_in_direction_deg = observation[self.num_rays + 1]  # Angle in degrees
        num_failed_moved = int(observation[self.num_rays + 2])  # Raw count

        action = 0 # Default: move forward

        # --- Rule 1: Target Seen ---
        if target_found:
            # print(f"DEBUG SimpleSearch: Target Seen. Angle: {target_in_direction_deg:.1f}") # Optional debug
            if abs(target_in_direction_deg) <= self.target_angle_threshold:
                action = 0  # Move forward towards target
            elif target_in_direction_deg < 0: # Target is to the left (negative angle)
                action = 1  # Turn left
            else: # Target is to the right (positive angle)
                action = 2  # Turn right
            return action, None # Prioritize target following, exit prediction

        # --- Rule 2: Stuck ---
        # Checks consecutive FAILED FORWARD moves (env tracks this)
        if num_failed_moved >= self.stuck_threshold:
            action = 1 # Force a turn (e.g., turn left consistently) to get unstuck
            # print(f"DEBUG SimpleSearch: Stuck! ({num_failed_moved} failed fwd). Forcing Left Turn.") # Optional debug
            return action, None # Exit prediction

        # --- Rule 3: Wall Ahead ---
        min_front_dist = 1.0 # Default to max distance (clear)
        # Check if front indices are valid and exist before accessing rays
        if self.front_ray_indices:
            # Ensure indices are within the bounds of the received rays array
            valid_front_indices = [i for i in self.front_ray_indices if 0 <= i < len(rays_normalized)]
            if valid_front_indices:
                min_front_dist = np.min(rays_normalized[valid_front_indices])
            # else: print("Warning: No valid front ray indices found!") # Debugging

        # If minimum distance of front rays is below threshold, obstacle detected
        if min_front_dist < self.wall_proximity_threshold:
            # print(f"DEBUG SimpleSearch: Wall Ahead! (Min front dist: {min_front_dist:.2f}). Checking sides.") # Optional debug
            # Wall is close in front, decide which way to turn based on side clearance

            # Calculate average distances on sides (handle empty lists and check index validity)
            avg_left_dist = 1.0 # Default clear
            if self.left_ray_indices:
                valid_left_indices = [i for i in self.left_ray_indices if 0 <= i < len(rays_normalized)]
                if valid_left_indices:
                    avg_left_dist = np.mean(rays_normalized[valid_left_indices])

            avg_right_dist = 1.0 # Default clear
            if self.right_ray_indices:
                valid_right_indices = [i for i in self.right_ray_indices if 0 <= i < len(rays_normalized)]
                if valid_right_indices:
                    avg_right_dist = np.mean(rays_normalized[valid_right_indices])

            # print(f"  DEBUG Side Clearance: Avg Left={avg_left_dist:.2f}, Avg Right={avg_right_dist:.2f}") # Optional debug

            # Turn towards the side with significantly more average space
            if avg_left_dist > avg_right_dist + self.side_clearance_hysteresis:
                action = 1 # Turn left
                # print("  DEBUG Action: Turning Left (more space left)") # Optional debug
            elif avg_right_dist > avg_left_dist + self.side_clearance_hysteresis:
                 action = 2 # Turn Right
                 # print("  DEBUG Action: Turning Right (more space right)") # Optional debug
            else:
                 # If space is roughly equal, default to one direction (e.g., right)
                 action = 2
                 # print("  DEBUG Action: Turning Right (space ~equal or default)") # Optional debug

            return action, None # Exit prediction

        # --- Rule 4: Default ---
        # If no target seen, not stuck, and no wall immediately ahead, default action is 0 (move forward).
        # print("DEBUG SimpleSearch: Default Action: Move Forward") # Optional debug
        return action, None