import pygame
import random
import os
from enum import Enum

pygame.init()

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
GRID_SIZE = 20
GRID_WIDTH = WINDOW_WIDTH // GRID_SIZE
GRID_HEIGHT = WINDOW_HEIGHT // GRID_SIZE
FPS = 10

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
ORANGE = (255, 165, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Icon lists
POWERUP_ICONS = [
    "Client VPN", "CloudTrail", "GuardDuty", "IAM Identity Center",
    "Key Management Service", "Network Firewall", "Shield", "WAF"
]

ATTACK_ICONS = [
    "DDOS", "Malware", "Phishing", "Ransomware", "SQL_injection"
]

# Directions
class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

class SnakeGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("AWS Snake Game")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 24)
        self.load_assets()
        self.reset_game()

    def load_assets(self):
        self.background = pygame.transform.scale(
            pygame.image.load("background/background1.png"),
            (WINDOW_WIDTH, WINDOW_HEIGHT)
        )
        self.powerup_images = [
            pygame.transform.scale(pygame.image.load(f"icons/{name}.png"), (GRID_SIZE * 2, GRID_SIZE * 2))
            for name in POWERUP_ICONS
        ]
        self.attack_images = [
            pygame.transform.scale(pygame.image.load(f"attacks/{name}.png"), (GRID_SIZE * 2, GRID_SIZE * 2))
            for name in ATTACK_ICONS
        ]

    def reset_game(self):
        self.snake = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = Direction.RIGHT
        self.score = 0
        self.running = True
        self.item_type = None  # 'powerup' or 'bomb'
        self.item_position = None
        self.item_icon = None
        self.item_timer = 0
        self.powerup_counter = 0
        self.spawn_item()

    def get_random_position(self):
        scoreboard_reserved_height = self.font.get_height() + 10
        reserved_grid_y = scoreboard_reserved_height // GRID_SIZE + 1

        while True:
            x = random.randint(0, GRID_WIDTH - 2)
            y = random.randint(reserved_grid_y, GRID_HEIGHT - 2)
            pos = (x, y)
            if pos not in self.snake:
                return pos

    def spawn_item(self):
        self.item_position = self.get_random_position()
        if self.powerup_counter >= 3:
            self.item_type = 'bomb'
            self.item_icon = random.choice(self.attack_images)
            self.powerup_counter = 0
        else:
            self.item_type = 'powerup'
            self.item_icon = random.choice(self.powerup_images)
            self.powerup_counter += 1
        self.item_timer = pygame.time.get_ticks()

    def move_snake(self):
        head_x, head_y = self.snake[0]
        dx, dy = self.direction.value
        new_head = (head_x + dx, head_y + dy)

        if (
            new_head in self.snake or
            new_head[0] < 0 or new_head[0] >= GRID_WIDTH or
            new_head[1] < 0 or new_head[1] >= GRID_HEIGHT
        ):
            self.running = False
            return

        # Check collision with item
        item_rect = pygame.Rect(
            self.item_position[0] * GRID_SIZE, self.item_position[1] * GRID_SIZE,
            GRID_SIZE * 2, GRID_SIZE * 2
        )
        snake_head_rect = pygame.Rect(
            new_head[0] * GRID_SIZE, new_head[1] * GRID_SIZE,
            GRID_SIZE, GRID_SIZE
        )

        if snake_head_rect.colliderect(item_rect):
            if self.item_type == 'bomb':
                self.running = False
                return
            else:
                self.snake.insert(0, new_head)
                self.score += 1
                self.spawn_item()
                return

        self.snake.insert(0, new_head)
        self.snake.pop()

    def draw_scoreboard(self):
        score_text = f"Score: {self.score}"
        score_surface = self.font.render(score_text, True, WHITE)
        padding = 10
        box_width = score_surface.get_width() + padding
        box_height = score_surface.get_height() + padding
        pygame.draw.rect(self.screen, BLACK, pygame.Rect(0, 0, box_width, box_height))
        self.screen.blit(score_surface, (padding // 2, padding // 2))
        return pygame.Rect(0, 0, box_width, box_height)

    def draw_elements(self):
        self.screen.blit(self.background, (0, 0))
        scoreboard_rect = self.draw_scoreboard()

        for segment in self.snake:
            pygame.draw.circle(
                self.screen,
                ORANGE,
                (segment[0] * GRID_SIZE + GRID_SIZE // 2, segment[1] * GRID_SIZE + GRID_SIZE // 2),
                GRID_SIZE // 2
            )

        if self.item_position:
            x, y = self.item_position[0] * GRID_SIZE, self.item_position[1] * GRID_SIZE
            icon_rect = pygame.Rect(x, y, GRID_SIZE * 2, GRID_SIZE * 2)

            border_color = RED if self.item_type == 'bomb' else GREEN
            pygame.draw.rect(self.screen, border_color, icon_rect, 3)
            self.screen.blit(self.item_icon, (x, y))

    def update(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.item_timer > 5000:
            self.spawn_item()
        self.move_snake()

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP and self.direction != Direction.DOWN:
                        self.direction = Direction.UP
                    elif event.key == pygame.K_DOWN and self.direction != Direction.UP:
                        self.direction = Direction.DOWN
                    elif event.key == pygame.K_LEFT and self.direction != Direction.RIGHT:
                        self.direction = Direction.LEFT
                    elif event.key == pygame.K_RIGHT and self.direction != Direction.LEFT:
                        self.direction = Direction.RIGHT

            self.update()
            self.draw_elements()
            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()

if __name__ == '__main__':
    game = SnakeGame()
    game.run()
