# main.py

import math
import random
import sys
import time

import pygame

# Game settings
SCREEN_WIDTH, SCREEN_HEIGHT = 600, 700
SNAKE_SIZE = 40
FOOD_SIZE = 50
SNAKE_SPEED = 15
game_over = False
restart_clicked = False
score = 0

# Initialize pygame
pygame.init()
pygame.mixer.init()
pygame.mixer.music.load("assets/background_music.wav")
pygame.mixer.music.play(-1)
pygame.mixer.music.set_volume(0.3)

# Wave animation settings for food
WAVE_AMPLITUDE = 5  # Amplitude of the wave motion
WAVE_FREQUENCY = 0.5  # Frequency of the wave motion
wave_phase = 0  # Phase of the wave

# Snake body wave animation settings
SNAKE_WAVE_AMPLITUDE = 3  # Amplitude for snake body wave motion
SNAKE_WAVE_FREQUENCY = 0.8  # Frequency for snake body wave motion
snake_wave_phase = 0  # Initial phase for snake body wave

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Snake Game")


# Load sprite images
snake_head_sprite = pygame.image.load("assets\snake_head.png")
snake_head_sprite = pygame.transform.scale(snake_head_sprite, (SNAKE_SIZE, SNAKE_SIZE))

food_sprite = pygame.image.load("assets\snake_food.png")
food_sprite = pygame.transform.scale(food_sprite, (FOOD_SIZE, FOOD_SIZE))

snake_body_sprite = pygame.image.load("assets\snake_body.png")
snake_body_sprite = pygame.transform.scale(snake_body_sprite, (SNAKE_SIZE, SNAKE_SIZE))

restart_button_sprite = pygame.image.load("assets\snake_restart_button.png")

background_image = pygame.image.load("assets\sbackground_image.png")
background_image = pygame.transform.scale(
    background_image, (SCREEN_WIDTH, SCREEN_HEIGHT)
)

# Load sound effects
eat_sound = pygame.mixer.Sound("assets/eat_sound.wav")

button_click_sound = pygame.mixer.Sound("assets/button_click_sound.wav")

# Snake setup
snake_pos = [100, 50]
snake_body = [[100, 50], [80, 50], [60, 50]]
direction = "RIGHT"
change_to = direction

# Food setup
food_pos = [
    random.randrange(1, (SCREEN_WIDTH // SNAKE_SIZE)) * SNAKE_SIZE,
    random.randrange(1, (SCREEN_HEIGHT // SNAKE_SIZE)) * SNAKE_SIZE,
]
food_spawn = True

# Font settings
font_path = "assets/font.ttf"
font_size = 28
font_color = (255, 255, 255)  # White color


# Draw Score
def draw_score(
    surface, text, size, x, y, outline_thickness=2, wave_amplitude=5, wave_frequency=2
):
    font = pygame.font.Font(font_path, size)
    outline_color = (0, 0, 0)  # Black color for the outline

    # Create a function to render text with an outline
    def render_with_outline(message, font, main_color, outline_color, thickness):
        # The base text without outline
        base = font.render(message, True, main_color)

        # Calculate the size of the surface with the outline based on the thickness
        outline_size = (
            base.get_width() + 2 * thickness,
            base.get_height() + 2 * thickness,
        )

        # Create a surface with per-pixel alpha to allow alpha blending of the outline
        outline = pygame.Surface(outline_size, pygame.SRCALPHA)

        # Render the outline by offsetting the text in multiple directions
        for dx in range(-thickness, thickness + 1):
            for dy in range(-thickness, thickness + 1):
                if dx != 0 or dy != 0:  # Avoid redrawing base text
                    temp = font.render(message, True, outline_color)
                    outline.blit(temp, (dx + thickness, dy + thickness))

        # Blit the base text onto the outline surface
        outline.blit(base, (thickness, thickness))
        return outline

    # Time-based phase for the wave effect
    time_ms = time.time() * 1000
    phase = wave_frequency * time_ms / 1000

    # Calculate the wave offset
    wave_offset = wave_amplitude * math.sin(phase)

    # Adjust y position based on the wave offset
    y_with_wave = y + wave_offset

    # Render the text with an outline
    text_surface = render_with_outline(
        text, font, font_color, outline_color, outline_thickness
    )
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y_with_wave)
    surface.blit(text_surface, text_rect)


# Particle System
class Particle:
    def __init__(self, x, y, color, direction):
        self.x = x
        self.y = y
        self.color = color
        self.size = random.randint(2, 5)
        self.lifetime = random.randint(5, 10)

        # Adjust velocity based on the snake's direction
        velocity = random.uniform(1, 3)
        if direction == "UP":
            self.x_vel = random.uniform(-1, 1)
            self.y_vel = -velocity
        elif direction == "DOWN":
            self.x_vel = random.uniform(-1, 1)
            self.y_vel = velocity
        elif direction == "LEFT":
            self.x_vel = -velocity
            self.y_vel = random.uniform(-1, 1)
        elif direction == "RIGHT":
            self.x_vel = velocity
            self.y_vel = random.uniform(-1, 1)
        else:
            self.x_vel = random.uniform(-1, 1)
            self.y_vel = random.uniform(-1, 1)

    def update(self):
        self.x += self.x_vel
        self.y += self.y_vel
        self.lifetime -= 1

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, [self.x, self.y, self.size, self.size])


# New list to hold particles
particles = []


# Game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and direction != "DOWN":
                change_to = "UP"
            elif event.key == pygame.K_DOWN and direction != "UP":
                change_to = "DOWN"
            elif event.key == pygame.K_LEFT and direction != "RIGHT":
                change_to = "LEFT"
            elif event.key == pygame.K_RIGHT and direction != "LEFT":
                change_to = "RIGHT"

    if not game_over:  # Only execute this block if the game is not over
        # Update the direction of the snake
        direction = change_to

        # Move the snake
        if direction == "UP":
            snake_pos[1] -= SNAKE_SPEED
        elif direction == "DOWN":
            snake_pos[1] += SNAKE_SPEED
        elif direction == "LEFT":
            snake_pos[0] -= SNAKE_SPEED
        elif direction == "RIGHT":
            snake_pos[0] += SNAKE_SPEED

        # Snake body growing mechanism
        snake_body.insert(0, list(snake_pos))
        if (
            snake_pos[0] >= food_pos[0]
            and snake_pos[0] < food_pos[0] + FOOD_SIZE
            and snake_pos[1] >= food_pos[1]
            and snake_pos[1] < food_pos[1] + FOOD_SIZE
        ):
            score += 1  # Increment score
            food_spawn = False
            for _ in range(20):  # Create 20 particles
                color = random.choice(
                    [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
                )  # Random color
                particles.append(Particle(snake_pos[0], snake_pos[1], color, direction))
            print("Food eaten at", food_pos)  # Debug message
        else:
            snake_body.pop()

        # Update wave phase
        wave_phase += WAVE_FREQUENCY

        # Update snake wave phase
        snake_wave_phase += SNAKE_WAVE_FREQUENCY

        # Update food position for wave animation
        food_pos[1] = (
            food_pos[1] + WAVE_AMPLITUDE * math.sin(wave_phase)
        ) % SCREEN_HEIGHT

        # Snake body movement with wave
        for i, pos in enumerate(snake_body[1:]):
            # Calculate wave offset
            offset = SNAKE_WAVE_AMPLITUDE * math.sin(snake_wave_phase + i * 0.5)
            if direction in ["LEFT", "RIGHT"]:
                snake_body[i][1] += offset
            else:
                snake_body[i][0] += offset

        # Food spawn
        if not food_spawn:
            food_pos = [
                random.randrange(1, (SCREEN_WIDTH // SNAKE_SIZE)) * SNAKE_SIZE,
                random.randrange(1, (SCREEN_HEIGHT // SNAKE_SIZE)) * SNAKE_SIZE,
            ]
            print("New food position:", food_pos)  # Debug message
            food_spawn = True
            eat_sound.play()

    # Background
    screen.blit(background_image, (0, 0))

    # Draw snake body
    for pos in snake_body[1:]:
        screen.blit(snake_body_sprite, (pos[0], pos[1]))

    # Draw snake head
    screen.blit(snake_head_sprite, (snake_pos[0], snake_pos[1]))

    # Draw food
    screen.blit(
        food_sprite, (food_pos[0], food_pos[1] - WAVE_AMPLITUDE * math.sin(wave_phase))
    )

    # Draw score
    draw_score(
        screen,
        f"Score: {score}",
        font_size,
        SCREEN_WIDTH / 2,
        10,
        outline_thickness=3,
        wave_amplitude=6,
        wave_frequency=3,
    )

    # Update and draw particles
    for particle in particles[:]:
        particle.update()
        particle.draw(screen)
        if particle.lifetime <= 0:
            particles.remove(particle)

    if snake_pos[0] < 0 or snake_pos[0] > SCREEN_WIDTH - SNAKE_SIZE:
        game_over = True
    if snake_pos[1] < 0 or snake_pos[1] > SCREEN_HEIGHT - SNAKE_SIZE:
        game_over = True
    for block in snake_body[1:]:
        if snake_pos[0] == block[0] and snake_pos[1] == block[1]:
            game_over = True

    # If the game is over, display the restart button and overlay
    if game_over:
        pygame.mixer.music.stop()

        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))  # Semi-transparent black overlay

        # Draw overlay
        screen.blit(overlay, (0, 0))

        # Draw restart button in the middle
        restart_button_rect = restart_button_sprite.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        )
        screen.blit(restart_button_sprite, restart_button_rect)

        pygame.display.update()

    # Check for restart button click outside the main game loop
    if game_over and pygame.mouse.get_pressed()[0]:  # 0 indicates left mouse button
        # Restart the game
        score = 0
        game_over = False
        snake_pos = [100, 50]
        snake_body = [[100, 50], [80, 50], [60, 50]]
        direction = "RIGHT"
        change_to = direction
        button_click_sound.play()
        pygame.mixer.music.play()

    # Refresh game screen
    pygame.display.update()
    pygame.time.Clock().tick(20)
