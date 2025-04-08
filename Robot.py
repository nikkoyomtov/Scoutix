
import pygame
import numpy as np
import math


class Robot:
    def __init__(self, start_pos, start_angle, size=10, speed=5, num_rays=17, fov=60.0, ray_length=None):
        self.size = size
        self.pos = np.array(start_pos, dtype=np.float32)
        self.angle = float(start_angle)
        self.speed = speed
        self.num_rays = num_rays
        self.fov = fov  # field of view
        self.ray_length = ray_length if ray_length is not None else 512 * 0.7  # Default ray length
        if self.ray_length is None:
            raise ValueError("ray_length must be specified or default must be calculable from house size")

    def move_forward(self, walls):  # Added walls argument
        angle_rad = math.radians(self.angle)
        direction = np.array([math.cos(angle_rad), math.sin(angle_rad)])
        proposed_pos = self.pos + direction * self.speed  # Calculate the position robot would move to
        prev = self.pos
        self.pos = proposed_pos  # Move only if no collision is imminent

        if not self.check_collision_walls(walls):
            return False  # No collision occurred during movement
        else:
            self.pos = prev  # Move only if no collision is imminent
            return True  # Collision occurred (robot stayed in place)

    def check_collision_walls(self, walls):
        robot_rect = pygame.Rect(
            self.pos[0] - self.size,
            self.pos[1] - self.size,
            self.size * 2,
            self.size * 2
        )

        for wall in walls:
            if robot_rect.colliderect(wall):
                return True
        return False


        # for wall in walls:
        #     # Find closest point on the wall to the circle's center
        #     closest_x = max(wall.left, min(self.pos[0], wall.right))
        #     closest_y = max(wall.top, min(self.pos[1], wall.bottom))
        #
        #     # Calculate distance between circle center and closest point
        #     distance_x = self.pos[0] - closest_x
        #     distance_y = self.pos[1] - closest_y
        #
        #     # If the distance is less than the circle's radius (size), there is a collision
        #     distance_squared = (distance_x ** 2) + (distance_y ** 2)
        #     if distance_squared < (self.size ** 2):
        #         return True
        #
        # return False

    def turn_left(self, angle_step=15):
        self.angle += angle_step
        return True

    def turn_right(self, angle_step=15):
        self.angle -= angle_step
        return True

    def cast_rays(self, walls):
        rays = []
        angle_increment = self.fov / (self.num_rays - 1) if self.num_rays > 1 else 0
        start_angle = self.angle - self.fov / 2

        for i in range(self.num_rays):
            ray_angle = start_angle + i * angle_increment
            ray_direction = np.array([math.cos(math.radians(ray_angle)), math.sin(math.radians(ray_angle))])
            ray_origin = self.pos
            ray_end = ray_origin + ray_direction * self.ray_length

            closest_intersection_distance = self.ray_length  # Initialize max distance
            for wall in walls:
                intersection_point = wall.clipline(ray_origin[0], ray_origin[1], ray_end[0], ray_end[1])
                if intersection_point:
                    p1, p2 = intersection_point  # clipline returns two points if it intersects
                    intersection = np.array(p1) if p1 else np.array(p2)  # Take the valid point
                    if p1 and p2:  # If both points are valid, take the closer one
                        dist1 = np.linalg.norm(intersection - ray_origin)
                        intersection = np.array(p2)
                        dist2 = np.linalg.norm(intersection - ray_origin)
                        intersection = np.array(p1) if dist1 < dist2 else np.array(p2)
                    elif p1:
                        intersection = np.array(p1)
                    else:
                        intersection = np.array(p2)

                    distance_to_intersection = np.linalg.norm(intersection - ray_origin)
                    closest_intersection_distance = min(closest_intersection_distance, distance_to_intersection)

            rays.append(closest_intersection_distance)
        return rays

    def get_ray_endpoints(self, ray_lengths):  # For visualization
        endpoints = []
        angle_increment = self.fov / (self.num_rays - 1) if self.num_rays > 1 else 0
        start_angle = self.angle - self.fov / 2

        for i in range(self.num_rays):
            ray_angle = start_angle + i * angle_increment
            ray_direction = np.array([math.cos(math.radians(ray_angle)), math.sin(math.radians(ray_angle))])
            ray_origin = self.pos
            ray_length = ray_lengths[i]  # Use the actual ray length
            ray_end = ray_origin + ray_direction * ray_length
            endpoints.append(ray_end)
        return endpoints

    def draw(self, surface, ray_lengths):
        # Draw Rays
        ray_endpoints = self.get_ray_endpoints(ray_lengths)
        for end_point in ray_endpoints:
            pygame.draw.line(surface, (255, 0, 0), self.pos, end_point, 1)  # Red rays
        # Draw Robot
        pygame.draw.circle(surface, (0, 0, 255), self.pos.astype(int), self.size)  # Blue robot
        # Draw robot direction indicator
        robot_direction_vector = np.array(
            [math.cos(math.radians(self.angle)), math.sin(math.radians(self.angle))]) * self.size
        pygame.draw.line(surface, (255, 255, 255), self.pos, self.pos + robot_direction_vector,
                         3)  # White direction line

