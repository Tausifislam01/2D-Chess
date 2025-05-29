import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import chess
from PIL import Image
import numpy as np
import logging
import asyncio
import platform

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

class ChessGame:
    def __init__(self):
        """Initialize Pygame, OpenGL, and chess board."""
        pygame.init()
        self.display = (800, 800)
        pygame.display.set_mode(self.display, DOUBLEBUF | OPENGL)
        pygame.display.set_caption("2D Chess Game")
        
        # OpenGL setup
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(0, 1, 0, 1)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glEnable(GL_TEXTURE_2D)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        self.board = chess.Board()
        self.square_size = 1.0 / 8
        self.selected_square = None
        self.legal_moves = []
        self.textures = self.load_textures()
        self.font = pygame.font.SysFont("arial", 16)
        self.player_color = None  # Will be set in choose_color
        logging.debug(f"Initial board: {self.board}")

    def load_textures(self):
        """Load chess piece PNGs as OpenGL textures."""
        piece_files = {
            'wp': 'pieces/wp.png', 'wn': 'pieces/wn.png', 'wb': 'pieces/wb.png',
            'wr': 'pieces/wr.png', 'wq': 'pieces/wq.png', 'wk': 'pieces/wk.png',
            'bp': 'pieces/bp.png', 'bn': 'pieces/bn.png', 'bb': 'pieces/bb.png',
            'br': 'pieces/br.png', 'bq': 'pieces/bq.png', 'bk': 'pieces/bk.png'
        }
        textures = {}
        for piece, file in piece_files.items():
            try:
                image = Image.open(file).convert('RGBA')
                image_data = np.array(image)
                width, height = image.size
                texture_id = glGenTextures(1)
                glBindTexture(GL_TEXTURE_2D, texture_id)
                glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
                glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
                glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, image_data)
                textures[piece] = texture_id
                logging.info(f"Loaded texture: {file}")
            except FileNotFoundError:
                logging.error(f"Texture not found: {file}")
            except Exception as e:
                logging.error(f"Error loading {file}: {e}")
        return textures

    def get_display_row(self, logical_row):
        """Map logical row to display row based on player color."""
        if self.player_color == chess.WHITE:
            return logical_row  # Rank 1 at bottom for White
        else:
            return 7 - logical_row  # Rank 8 at bottom for Black

    def choose_color(self):
        """Menu to choose player color."""
        menu_running = True
        # Define button rectangles
        button_width, button_height = 300, 60
        white_button_rect = pygame.Rect(250, 300, button_width, button_height)
        black_button_rect = pygame.Rect(250, 400, button_width, button_height)
        font = pygame.font.SysFont("arial", 24)  # Larger font for clarity
        
        while menu_running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    exit()
                elif event.type == MOUSEBUTTONDOWN:
                    x, y = event.pos
                    logging.info(f"Menu click at (x={x}, y={y})")
                    if white_button_rect.collidepoint(x, y):
                        self.player_color = chess.WHITE
                        menu_running = False
                        logging.info("Selected color: White")
                    elif black_button_rect.collidepoint(x, y):
                        self.player_color = chess.BLACK
                        menu_running = False
                        logging.info("Selected color: Black")
            
            # Draw menu
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            menu_surface = pygame.Surface(self.display, pygame.SRCALPHA)
            
            # Background
            menu_surface.fill((200, 200, 200))  # Light gray
            
            # Debug markers (colored squares at corners)
            pygame.draw.rect(menu_surface, (255, 0, 0), (0, 0, 20, 20))  # Top-left: Red
            pygame.draw.rect(menu_surface, (0, 255, 0), (780, 0, 20, 20))  # Top-right: Green
            pygame.draw.rect(menu_surface, (0, 0, 255), (0, 780, 20, 20))  # Bottom-left: Blue
            
            # Title
            title = font.render("Choose Your Color", True, (0, 0, 0))
            title_rect = title.get_rect(center=(400, 200))
            menu_surface.blit(title, title_rect)
            
            # Buttons
            pygame.draw.rect(menu_surface, (255, 255, 255), white_button_rect)  # White button
            pygame.draw.rect(menu_surface, (50, 50, 50), black_button_rect)     # Dark gray button
            white_text = font.render("Play as White", True, (0, 0, 0))
            black_text = font.render("Play as Black", True, (255, 255, 255))   # White text for contrast
            white_text_rect = white_text.get_rect(center=white_button_rect.center)
            black_text_rect = black_text.get_rect(center=black_button_rect.center)
            menu_surface.blit(white_text, white_text_rect)
            menu_surface.blit(black_text, black_text_rect)
            
            # Convert to OpenGL texture (no flip in Pygame)
            menu_data = pygame.image.tostring(menu_surface, 'RGBA', False)
            texture_id = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, texture_id)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, 800, 800, 0, GL_RGBA, GL_UNSIGNED_BYTE, menu_data)
            
            # Draw texture with corrected orientation
            glBegin(GL_QUADS)
            glTexCoord2f(0, 1); glVertex2f(0, 0)  # Bottom-left: texture top-left to screen bottom-left
            glTexCoord2f(1, 1); glVertex2f(1, 0)  # Bottom-right: texture top-right to screen bottom-right
            glTexCoord2f(1, 0); glVertex2f(1, 1)  # Top-right: texture bottom-right to screen top-right
            glTexCoord2f(0, 0); glVertex2f(0, 1)  # Top-left: texture bottom-left to screen top-left
            glEnd()
            glDeleteTextures(1, [texture_id])
            
            pygame.display.flip()
            pygame.time.wait(10)

    def draw_square(self, col, row, color):
        """Draw a single square with the specified color."""
        glBindTexture(GL_TEXTURE_2D, 0)
        glColor3f(*color)
        x = col * self.square_size
        y = row * self.square_size
        glBegin(GL_QUADS)
        glVertex2f(x, y)
        glVertex2f(x + self.square_size, y)
        glVertex2f(x + self.square_size, y + self.square_size)
        glVertex2f(x, y + self.square_size)
        glEnd()

    def draw_chessboard(self):
        """Draw 8x8 chessboard with alternating colors."""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        for display_row in range(8):
            for col in range(8):
                if (display_row + col) % 2 == 0:
                    color = (1.0, 1.0, 1.0)  # White
                else:
                    color = (0.6, 0.3, 0.0)  # Brown
                self.draw_square(col, display_row, color)
        glBindTexture(GL_TEXTURE_2D, 0)

    def draw_highlights(self):
        """Highlight selected square and legal moves."""
        if self.selected_square is not None:
            col = chess.square_file(self.selected_square)
            logical_row = chess.square_rank(self.selected_square)
            display_row = self.get_display_row(logical_row)
            self.draw_square(col, display_row, (1.0, 1.0, 0.0))  # Yellow
        for move in self.legal_moves:
            col = chess.square_file(move.to_square)
            logical_row = chess.square_rank(move.to_square)
            display_row = self.get_display_row(logical_row)
            self.draw_square(col, display_row, (0.0, 1.0, 0.0))  # Green

    def draw_labels(self):
        """Draw a-h and 1-8 labels using Pygame."""
        label_surface = pygame.Surface(self.display, pygame.SRCALPHA)
        files = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
        if self.player_color == chess.WHITE:
            ranks = ['1', '2', '3', '4', '5', '6', '7', '8']  # Bottom to top
        else:
            ranks = ['8', '7', '6', '5', '4', '3', '2', '1']  # Bottom to top
        
        # Adjust file labels based on player perspective
        display_files = files if self.player_color == chess.WHITE else files[::-1]
        
        # Draw file labels (a-h)
        for col, file in enumerate(display_files):
            x = col * 100 + 50
            text = self.font.render(file, True, (0, 0, 0))
            text_rect = text.get_rect(center=(x, 785))  # Bottom
            label_surface.blit(text, text_rect)
            text_rect = text.get_rect(center=(x, 5))    # Top
            label_surface.blit(text, text_rect)
            logging.debug(f"File {file} at x={x}")
        
        # Draw rank labels (1-8)
        for display_row in range(8):
            rank_label = ranks[display_row]
            y = display_row * 100 + 50
            text = self.font.render(rank_label, True, (0, 0, 0))
            text_rect = text.get_rect(center=(5, y))    # Left
            label_surface.blit(text, text_rect)
            text_rect = text.get_rect(center=(785, y))  # Right
            label_surface.blit(text, text_rect)
            logging.debug(f"Rank {rank_label} at y={y}")
        
        # Convert to OpenGL texture (no vertical flip)
        label_data = pygame.image.tostring(label_surface, 'RGBA', False)
        texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture_id)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, 800, 800, 0, GL_RGBA, GL_UNSIGNED_BYTE, label_data)
        
        # Draw texture with corrected orientation
        glBegin(GL_QUADS)
        glTexCoord2f(0, 1); glVertex2f(0, 0)  # Bottom-left: texture top-left to screen bottom-left
        glTexCoord2f(1, 1); glVertex2f(1, 0)  # Bottom-right: texture top-right to screen bottom-right
        glTexCoord2f(1, 0); glVertex2f(1, 1)  # Top-right: texture bottom-right to screen top-right
        glTexCoord2f(0, 0); glVertex2f(0, 1)  # Top-left: texture bottom-left to screen top-left
        glEnd()
        glDeleteTextures(1, [texture_id])

    def draw_pieces(self):
        """Draw chess pieces using textures."""
        piece_map = {
            'P': 'wp', 'N': 'wn', 'B': 'wb', 'R': 'wr', 'Q': 'wq', 'K': 'wk',
            'p': 'bp', 'n': 'bn', 'b': 'bb', 'r': 'br', 'q': 'bq', 'k': 'bk'
        }
        scale_factor = 0.8
        offset = (1 - scale_factor) / 2 * self.square_size
        
        for square in chess.SQUARES:
            piece = self.board.piece_at(square)
            if piece:
                piece_key = piece_map[piece.symbol()]
                col = chess.square_file(square)
                logical_row = chess.square_rank(square)
                display_row = self.get_display_row(logical_row)
                x = col * self.square_size + offset
                y = display_row * self.square_size + offset
                piece_size = self.square_size * scale_factor
                
                glColor3f(1.0, 1.0, 1.0)  # No tint
                if piece_key in self.textures:
                    glBindTexture(GL_TEXTURE_2D, self.textures[piece_key])
                    logging.debug(f"Rendering texture {piece_key} at {chess.square_name(square)}")
                else:
                    logging.warning(f"Texture {piece_key} not found, using fallback")
                    glBindTexture(GL_TEXTURE_2D, 0)
                    glColor3f(1.0, 0.0, 0.0 if piece.color == chess.WHITE else 0.0)  # Red/white, black/black
                
                glBegin(GL_QUADS)
                if piece_key in self.textures:
                    glTexCoord2f(0, 1); glVertex2f(x, y)
                    glTexCoord2f(1, 1); glVertex2f(x + piece_size, y)
                    glTexCoord2f(1, 0); glVertex2f(x + piece_size, y + piece_size)
                    glTexCoord2f(0, 0); glVertex2f(x, y + piece_size)
                else:
                    glVertex2f(x, y)
                    glVertex2f(x + piece_size, y)
                    glVertex2f(x + piece_size, y + piece_size)
                    glVertex2f(x, y + piece_size)
                glEnd()

    def get_square_from_mouse(self, pos):
        """Convert mouse position to chess square."""
        x, y = pos
        col = int((x / self.display[0]) * 8)
        if self.player_color == chess.WHITE:
            logical_row = 7 - int((y / self.display[1]) * 8)  # Bottom (y=800) -> rank 1
        else:
            logical_row = int((y / self.display[1]) * 8)      # Bottom (y=800) -> rank 8
        if 0 <= col < 8 and 0 <= logical_row < 8:
            square = chess.square(col, logical_row)
            logging.info(f"Clicked square: {chess.square_name(square)} at pixel (x={x}, y={y})")
            return square
        logging.warning("Clicked outside board")
        return None

    async def game_loop(self):
        """Main game loop for Pyodide compatibility."""
        self.choose_color()
        FPS = 60
        while True:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    return
                elif event.type == MOUSEBUTTONDOWN:
                    square = self.get_square_from_mouse(event.pos)
                    if square is not None:
                        piece = self.board.piece_at(square)
                        current_turn = "White" if self.board.turn else "Black"
                        logging.info(f"Current turn: {current_turn}")
                        if self.selected_square is None:
                            if piece and piece.color == self.board.turn:
                                self.selected_square = square
                                self.legal_moves = [move for move in self.board.legal_moves if move.from_square == square]
                                logging.info(f"Selected {piece.symbol()} at {chess.square_name(square)}, legal moves: {[str(m) for m in self.legal_moves]}")
                            else:
                                logging.warning(f"Invalid selection at {chess.square_name(square)}: No piece or wrong turn")
                        else:
                            move = next((m for m in self.legal_moves if m.to_square == square), None)
                            if move:
                                self.board.push(move)
                                logging.info(f"Moved {move.uci()} ({chess.square_name(move.from_square)} to {chess.square_name(move.to_square)})")
                                self.selected_square = None
                                self.legal_moves = []
                            else:
                                logging.warning(f"Invalid move to {chess.square_name(square)}")
                                self.selected_square = None
                                self.legal_moves = []
            
            self.draw_chessboard()
            self.draw_highlights()
            self.draw_pieces()
            self.draw_labels()
            pygame.display.flip()
            await asyncio.sleep(1.0 / FPS)

    def run(self):
        """Start the game."""
        if platform.system() == "Emscripten":
            asyncio.ensure_future(self.game_loop())
        else:
            asyncio.run(self.game_loop())

if __name__ == "__main__":
    game = ChessGame()
    game.run()