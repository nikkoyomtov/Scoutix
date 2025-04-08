import pygame
import numpy as np
import random

class House:
    def __init__(self, size, robot_start_pos, randomize_house=True, num_random_walls=10):
        self.size = size
        self.wall_thickness = 10
        self.num_random_walls = num_random_walls  # Store the number of random walls
        self.robot_start_pos = np.array(robot_start_pos)  # Store robot start position
        self.randomize_house = randomize_house
        self.walls = self._create_layout()
        self.target_pos = self.place_target()
        self.target_size = 10  # Size of the target circle TODO return to size 10

    def _create_layout(self):
        if self.randomize_house:
            return self._create_random_layout()
        else:
            layout = random.choice(["layout1", "layout2", "layout3"])
            if layout == "layout1":
                return self._create_constant_layout1()
            elif layout == "layout2":
                return self._create_constant_layout2()
            elif layout == "layout3":
                return self._create_constant_layout3()
            else:
                return self._create_constant_layout1()

    def _create_constant_layout1(self):
        # Define room sizes and positions (adjust these)
        room_width = self.size // 4
        room_height = self.size // 4
        door_width = room_width // 4

        # Create walls
        walls = [
            # Outer walls DO NO TOUCH
            pygame.Rect(0, 0, self.size, self.wall_thickness),  # Top wall
            pygame.Rect(0, 0, self.wall_thickness, self.size),  # Left wall
            pygame.Rect(0, self.size - self.wall_thickness, self.size, self.wall_thickness),  # Bottom wall
            pygame.Rect(self.size - self.wall_thickness, 0, self.wall_thickness, self.size),  # Right wall

            # Internal Walls Defining Rooms with Doorways
            pygame.Rect(room_width, 0, self.wall_thickness, room_height // 2 - door_width // 2), # y = 0, y = 1/8 * board , x = 1/4 *board
            # Room 1/2 divider (top)
            # pygame.Rect(room_width, room_height // 2 + door_width // 2, self.wall_thickness,
            #             room_height - (room_height // 2 - door_width // 2) - (room_height // 2 + door_width // 2)),
            # Room 1/2 divider (bottom)

            pygame.Rect(0, room_height, room_width // 2 - door_width // 2, self.wall_thickness), # x = 0, x = 1/8 *board, y = 1/4 * board
            # Room 2/3 divider (left)
            # pygame.Rect(room_width // 2 + door_width // 2, room_height,
            #             room_width - (room_width // 2 - door_width // 2) - (room_width // 2 + door_width // 2),
            #             self.wall_thickness),  # Room 2/3 divider (right)

            pygame.Rect(room_width * 2, 0, self.wall_thickness, room_height - door_width // 2),  # x = 1/2 * board, y = 0, y = 1/4 * board
            # pygame.Rect(room_width * 2, room_height + door_width // 2, self.wall_thickness,
            #             room_height - (room_height + door_width // 2)),  # Room 4 divider (bottom)

            pygame.Rect(0, room_height * 2, room_width * 3, self.wall_thickness),  # x=0, x = 3/4 * board, y =1/2 * board

            pygame.Rect(room_width * 3, room_height * 2, self.wall_thickness, room_height // 2 - door_width // 2), # x = 3/4 * board, y = 1/2 * borad, y = 5/8 * board
            # Room 6 divider (top)
            # pygame.Rect(room_width * 3, room_height * 2 + room_height // 2 + door_width // 2, self.wall_thickness,
            #             room_height - (room_height // 2 - door_width // 2) - (
            #                         room_height * 2 + room_height // 2 + door_width // 2)),  # Room 6 divider (bottom)

            pygame.Rect(room_width * 3, room_height, self.size - room_width * 3, self.wall_thickness), # y = 1/4 * board, x = 3/4 * board, x = board
            # TopRightRoomsDivider

            pygame.Rect(room_width, room_height * 3, self.wall_thickness, self.size - room_height * 3),
            # BottomLeftRoomsDivider

            pygame.Rect(room_width, room_height, room_width // 2 - door_width // 2, self.wall_thickness), # tiny floating wall on top left
            # HorizontalWallForMiddleRooms (left)
            # pygame.Rect(room_width + room_width // 2 + door_width // 2, room_height,
            #             room_width - (room_width // 2 - door_width // 2) - (room_width // 2 + door_width // 2),
            #             self.wall_thickness)  # HorizontalWallForMiddleRooms (right)

        ]

        return walls

    def _create_constant_layout2(self):
        # Define room sizes and positions (adjust these)
        room_width = self.size // 4
        room_height = self.size // 4
        door_width = room_width // 4

        # Create walls
        walls = [
            # Outer walls DO NO TOUCH
            pygame.Rect(0, 0, self.size, self.wall_thickness),  # Top wall
            pygame.Rect(0, 0, self.wall_thickness, self.size),  # Left wall
            pygame.Rect(0, self.size - self.wall_thickness, self.size, self.wall_thickness),  # Bottom wall
            pygame.Rect(self.size - self.wall_thickness, 0, self.wall_thickness, self.size),  # Right wall

            # Internal Walls Defining Rooms with Doorways
            pygame.Rect(0, room_width, room_height // 2 - door_width // 2, self.wall_thickness),
            # x = 0, x = 1/8 * board , y = 1/4 *board

            pygame.Rect(room_height, 0, self.wall_thickness, room_width // 2 - door_width // 2),
            # y = 0, y = 1/8 *board, x = 1/4 * board

            pygame.Rect(0, room_width * 2, room_height - door_width // 2, self.wall_thickness),
            # y = 1/2 * board, x = 0, x = 1/4 * board

            pygame.Rect(room_height * 2, 0, self.wall_thickness, room_width * 3),
            # y=0, y = 3/4 * board, x =1/2 * board

            pygame.Rect(room_height * 2, room_width * 3, room_height // 2 - door_width // 2, self.wall_thickness),
            # y = 3/4 * board, x = 1/2 * borad, x = 5/8 * board

            pygame.Rect(room_height, room_width * 3, self.wall_thickness, self.size - room_width * 3),
            # x = 1/4 * board, y = 3/4 * board, y = board

            pygame.Rect(room_height * 3, room_width, self.size - room_height * 3, self.wall_thickness),
            # BottomLeftRoomsDivider

            pygame.Rect(room_height, room_width, self.wall_thickness, room_width // 2 - door_width // 2),
            # tiny floating wall on top left

        ]
        return walls

    def _create_constant_layout3(self):
        # Define room sizes and positions
        room_width = self.size // 4
        room_height = self.size // 4
        passage_width = room_width // 4  # Much wider passages

        # Create walls
        walls = [
            # Outer walls
            pygame.Rect(0, 0, self.size, self.wall_thickness),  # Top wall
            pygame.Rect(0, 0, self.wall_thickness, self.size),  # Left wall
            pygame.Rect(0, self.size - self.wall_thickness, self.size, self.wall_thickness),  # Bottom wall
            pygame.Rect(self.size - self.wall_thickness, 0, self.wall_thickness, self.size),  # Right wall

            # Vertical dividers
            # Central vertical divider with wide gap in middle
            pygame.Rect(self.size // 2, 0, self.wall_thickness, room_height * 2 - passage_width),  # Top section


            # Right quarter divider
            pygame.Rect(room_width * 3, room_height, self.wall_thickness, room_height * 2.5),  # Longer wall

            # Horizontal dividers
            # Upper horizontal divider
            pygame.Rect(0, room_height, room_width - passage_width, self.wall_thickness),  # Left section
            pygame.Rect(room_width + passage_width, room_height, room_width - passage_width, self.wall_thickness),
            # Right section

            # Lower horizontal divider with wide opening
            pygame.Rect(0, room_height * 3, room_width * 2 - passage_width, self.wall_thickness),  # Left section
            pygame.Rect(room_width * 2 + passage_width, room_height * 3, room_width * 2 - passage_width,
                        self.wall_thickness),  # Right section
        ]

        return walls

    def _create_random_layout(self):
        # Start with border walls
        walls = [
            pygame.Rect(0, 0, self.size, self.wall_thickness),  # Top wall
            pygame.Rect(0, 0, self.wall_thickness, self.size),  # Left wall
            pygame.Rect(0, self.size - self.wall_thickness, self.size, self.wall_thickness),  # Bottom wall
            pygame.Rect(self.size - self.wall_thickness, 0, self.wall_thickness, self.size),  # Right wall
        ]

        # Generate random inner walls
        min_wall_length = self.size // 5  # Minimum length of a random wall
        max_wall_length = self.size // 2  # Maximum length of a random wall
        min_wall_gap = self.size // 5  # Minimum gap between walls and from borders

        wall_free_zone_size = 30  # Adjust size as needed
        wall_free_zone = pygame.Rect(
            self.robot_start_pos[0] - wall_free_zone_size // 2,
            self.robot_start_pos[1] - wall_free_zone_size // 2,
            wall_free_zone_size,
            wall_free_zone_size
        )

        for _ in range(self.num_random_walls):
            orientation = random.choice(['horizontal', 'vertical'])
            if orientation == 'horizontal':
                # Horizontal wall
                length = random.randint(min_wall_length, max_wall_length)
                x = random.randint(self.wall_thickness + min_wall_gap,
                                   self.size - self.wall_thickness - min_wall_gap - length)
                y = random.randint(self.wall_thickness + min_wall_gap, self.size - self.wall_thickness - min_wall_gap)
                wall = pygame.Rect(x, y, length, self.wall_thickness)
            else:  # vertical
                # Vertical wall
                length = random.randint(min_wall_length, max_wall_length)
                x = random.randint(self.wall_thickness + min_wall_gap, self.size - self.wall_thickness - min_wall_gap)
                y = random.randint(self.wall_thickness + min_wall_gap,
                                   self.size - self.wall_thickness - min_wall_gap - length)
                wall = pygame.Rect(x, y, self.wall_thickness, length)

            # Basic check to avoid overlapping with border walls too closely (can be improved)
            valid_position = True

            if wall_free_zone.colliderect(wall):  # Check against wall_free_zone
                valid_position = False  # Reject if in wall_free_zone
            else:
                for existing_wall in walls:
                    if wall.colliderect(existing_wall):
                        valid_position = False
                        break

            if valid_position:
                walls.append(wall)  # Add the new random wall

        return walls

    def place_target(self):
        # Place target randomly within a randomly chosen quarter of the house

        quarter = random.randint(1, 4)  # Choose a random quarter (1, 2, 3, or 4)

        while True:
            if quarter == 1:  # Top-Left
                x = random.randint(self.wall_thickness, self.size // 2)
                y = random.randint(self.wall_thickness, self.size // 2)
            elif quarter == 2:  # Top-Right
                x = random.randint(self.size // 2, self.size - self.wall_thickness)
                y = random.randint(self.wall_thickness, self.size // 2)
            elif quarter == 3:  # Bottom-Left
                x = random.randint(self.wall_thickness, self.size // 2)
                y = random.randint(self.size // 2, self.size - self.wall_thickness)
            else:  # Bottom-Right (quarter == 4)
                x = random.randint(self.size // 2, self.size - self.wall_thickness)
                y = random.randint(self.size // 2, self.size - self.wall_thickness)

            target_pos = np.array([x, y], dtype=np.float32)

            if not self.is_inside_wall(target_pos):
                return target_pos

    def is_inside_wall(self, pos):
        point = pygame.Rect(pos[0], pos[1], 1, 1)  # Treat position as a point rect
        for wall in self.walls:
            if point.colliderect(wall):
                return True
        return False

    def draw(self, surface):
        # Draw walls
        for wall in self.walls:
            pygame.draw.rect(surface, (0, 0, 0), wall)  # Black walls
        # Draw target
        pygame.draw.circle(surface, (0, 255, 0), self.target_pos.astype(int), self.target_size)  # Green target
