# This is the main driver file. It will be responsible for handling user input and displaying the current GameState object.

import pygame as p

try:
    from Chess import ChessEngine
except ModuleNotFoundError:
    import ChessEngine

WIDTH = HEIGHT = 512 # 400 is also a good option
DIMENSION = 8 # The dimension of a chess board is 8x8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15 # For the animations
IMAGES = {}

# Initialize a global dictionary if images. This will be called exactly once in the main.
def loadImages():
    pieces = ['wK', 'wQ', 'wR', 'wB', 'wN', 'wP', 'bK', 'bQ', 'bR', 'bB', 'bN', 'bP']

    for piece in pieces:
        try:
            IMAGES[piece] = p.transform.scale(p.image.load('images/' + piece + '.png'), (SQ_SIZE, SQ_SIZE))
        except FileNotFoundError:
             IMAGES[piece] = p.transform.scale(p.image.load('Chess/images/' + piece + '.png'), (SQ_SIZE, SQ_SIZE))
    # Note: we can access an image by saying "IMAGES['wP']"

# The main driver for our code. This will handle user input and updating the graphics.
def main():
    p.init()

    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()

    screen.fill(p.Color('white'))

    gs = ChessEngine.GameState()

    loadImages() # Only do this once, before the while loop
    
    running = True
    sqSelected = () # No square is selected, keep track of the last click of the user (tuple: (row, col))
    playerClicks = [] # Keep track of player clicks (two tuples: [(6, 4), (4, 4)])

    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            elif e.type == p.MOUSEBUTTONDOWN:
                location = p.mouse.get_pos() # (x, y) location of mouse
                col = location[0] // SQ_SIZE
                row = location[1] // SQ_SIZE

                if sqSelected == (row, col): # The user clicked the same square twice
                    sqSelected = () # Deselect
                    playerClicks = [] # Clear player clicks
                else:
                    sqSelected = (row, col)
                    playerClicks.append(sqSelected) # Append for both 1st and 2nd clicks
                
                if len(playerClicks) == 2: # After 2nd click
                    move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)

                    gs.makeMove(move)
                    
                    sqSelected = () # Reset user clicks
                    playerClicks = []

        drawGameState(screen, gs)
        clock.tick(MAX_FPS)
        p.display.flip()

# Responsible for all the graphics within a current game state.
def drawGameState(screen, gs):
    drawBoard(screen) # Draw squares on the board
    # Add in piece highlighting or move suggestions
    drawPieces(screen, gs.board) # Draw pieces on top of those squares

# Draw the squares on the board. The top left square is always light.
def drawBoard(screen):
    colors = [(240, 217, 181), (181, 136, 99)]

    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r+c) % 2)]

            p.draw.rect(screen, color, p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))


# Draw the pieces on the board using the current GameState.board
def drawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]

            if piece != '--': # Not empty square
                screen.blit(IMAGES[piece], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

if __name__ == '__main__':
    main()