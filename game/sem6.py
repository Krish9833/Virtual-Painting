import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Set the dimensions of the window
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
WINDOW_SIZE = (WINDOW_WIDTH, WINDOW_HEIGHT)

# Set colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# Set FPS (frames per second)
FPS = 60
clock = pygame.time.Clock()

# Class for circle
class Circle(pygame.sprite.Sprite):
    def __init__(self, is_bomb=False):  # Fixed the __init__ method
        super().__init__()  # Correct usage of super()
        self.radius = 30
        if is_bomb:
            self.radius *= 3  # Triple the radius for the bomb
        self.image = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        if is_bomb:
            pygame.draw.circle(self.image, RED, (self.radius, self.radius), self.radius)
            self.value = -10  # Bomb value (negative score)
            self.speed = 3  # Bomb moves faster
        else:
            pygame.draw.circle(self.image, GREEN, (self.radius, self.radius), self.radius)
            self.value = 1  # Normal circle value
            self.speed = 1  # Normal circles move slower
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, WINDOW_WIDTH - self.rect.width)  # Random initial x position
        self.rect.y = random.randint(0, WINDOW_HEIGHT - self.rect.height)  # Random initial y position
        self.direction = [random.choice([-1, 1]), random.choice([-1, 1])]  # Random initial direction

    def update(self):
        # Move the circle
        self.rect.x += self.direction[0] * self.speed
        self.rect.y += self.direction[1] * self.speed

        # Bounce off edges of the screen
        if self.rect.left < 0 or self.rect.right > WINDOW_WIDTH:
            self.direction[0] = -self.direction[0]
        if self.rect.top < 0 or self.rect.bottom > WINDOW_HEIGHT:
            self.direction[1] = -self.direction[1]

# Function to draw text on screen
def draw_text(surface, text, size, color, x, y):
    font = pygame.font.Font(None, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surface.blit(text_surface, text_rect)

# Main function
def main():
    # Set up the window
    screen = pygame.display.set_mode(WINDOW_SIZE)
    pygame.display.set_caption("Avoid the Bomb")

    # Create circles (including the bomb)
    circles = pygame.sprite.Group()
    for _ in range(3):  # Three normal circles
        circle = Circle()
        circles.add(circle)
    # One bomb
    bomb = Circle(is_bomb=True)
    circles.add(bomb)

    # Score
    score = 0

    # Game loop
    while True:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Handle mouse click events
            if event.type == pygame.MOUSEBUTTONDOWN:
                for circle in list(circles):  # Convert to list to modify during iteration
                    if circle.rect.collidepoint(event.pos):
                        if circle.value < 0:
                            # Game over if the bomb is clicked
                            print("Game Over! You clicked the bomb!")
                            pygame.quit()
                            sys.exit()
                        else:
                            # Increase score and remove the circle
                            score += circle.value
                            circles.remove(circle)
                            # Add a new circle to replace the one clicked
                            new_circle = Circle()
                            circles.add(new_circle)

        # Fill the background
        screen.fill(BLACK)

        # Update and draw circles
        circles.update()
        circles.draw(screen)

        # Draw score
        draw_text(screen, "Score: " + str(score), 30, WHITE, WINDOW_WIDTH // 2, 10)

        # Update the display
        pygame.display.flip()

        # Cap the frame rate
        clock.tick(FPS)

# ✅ Corrected the if __name__ condition
if __name__ == "__main__":
    main()

