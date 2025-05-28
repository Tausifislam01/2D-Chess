import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

def draw_chessboard():
    """Draw an 8x8 chessboard with alternating colors."""
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glBegin(GL_QUADS)
    
    square_size = 1.0 / 8  # Each square is 1/8 of the window
    for row in range(8):
        for col in range(8):
            # Alternate colors: white (1, 1, 1) and brown (0.6, 0.3, 0)
            if (row + col) % 2 == 0:
                glColor3f(1.0, 1.0, 1.0)  # White
            else:
                glColor3f(0.6, 0.3, 0.0)  # Brown
            
            # Draw square
            x = col * square_size
            y = row * square_size
            glVertex2f(x, y)
            glVertex2f(x + square_size, y)
            glVertex2f(x + square_size, y + square_size)
            glVertex2f(x, y + square_size)
    
    glEnd()

def main():
    """Set up Pygame window and OpenGL context, then draw chessboard."""
    pygame.init()
    display = (800, 800)  # Window size
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    pygame.display.set_caption("2D Chess Game")
    
    # Set up OpenGL orthographic projection
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0, 1, 0, 1)  # Map 0-1 to window
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    
    # Main loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        draw_chessboard()
        pygame.display.flip()
        pygame.time.wait(10)
    
    pygame.quit()

if __name__ == "__main__":
    main()