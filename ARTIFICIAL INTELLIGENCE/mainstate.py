# main.py
# The main entry/starting point for the Busy Bees simulation.

import pygame
from Simulation import Simulation

def draw_text(screen, text, font, color, x, y):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))
    screen.blit(text_surface, text_rect)

def main():
    """
    Initializes and runs the Busy Bees simulation.
    """
    # --- Pygame Initialization ---
    pygame.init()

    # Constants from the Simulation class
    SCREEN_WIDTH = Simulation.GRID_SIZE * Simulation.CELL_SIZE
    SCREEN_HEIGHT = Simulation.GRID_SIZE * Simulation.CELL_SIZE
    SIMULATION_SPEED = 200 # 

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Busy Bees FSM Simulation")
    clock = pygame.time.Clock()

    # Create the simulation instance
    sim = Simulation()
    sim.setup()
    
    
    font = pygame.font.Font(None, 36)
    
    running = True
    paused = False

    # Start screen loop
    start_screen = True
    while start_screen:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                start_screen = False
                running = False
            if event.type == pygame.KEYDOWN:
                start_screen = False

        screen.fill(Simulation.LIGHT_BLUE)
        draw_text(screen, "Press any key to start the simulation", font, (0, 0, 0), SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        pygame.display.flip()

    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    paused = True
                elif event.key == pygame.K_r:
                    paused = False
                elif event.key == pygame.K_q or event.key == pygame.K_ESCAPE:
                    running = False

        
        if not paused:
            sim.update()

        sim.draw(screen)
        
       
        if paused:
            draw_text(screen, "PAUSED", font, (255, 0, 0), SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

        # Control the frame rate and simulation speed
        pygame.time.wait(SIMULATION_SPEED)
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()