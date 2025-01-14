# This is the main driver file. It will be responsible for handling user input and displaying the current GameState object.

import pygame as p

try:
    from Chess import ChessEngine, SmartMoveFinder
except ModuleNotFoundError:
    import ChessEngine, SmartMoveFinder

WIDTH = HEIGHT = 512 # 400 is also a good option
DIMENSION = 8 # The dimension of a chess board is 8x8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 60 # For the animations
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
    p.display.set_caption("Chess") # Set the title of the window

    # Set the icon of the window
    try:
        icon = p.image.load('images/chess.png')
    except FileNotFoundError:
        icon = p.image.load('Chess/images/chess.png')

    p.display.set_icon(icon)

    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()

    screen.fill(p.Color('white'))

    gs = ChessEngine.GameState()
    validMoves = gs.getValidMoves()
    moveMade = False # Flag variable for when a move is made
    animate = False # Flag variable for when we should animate a move
    running = True
    sqSelected = () # No square is selected, keep track of the last click of the user (tuple: (row, col))
    playerClicks = [] # Keep track of player clicks (two tuples: [(6, 4), (4, 4)])
    gameOver = False
    playerOne = True # If a human is playing white, then this will be True. If a bot is playing, then it is going to be False
    playerTwo = False # Same as above but for black

    loadImages() # Only do this once, before the while loop

    while running:
        humanTurn = (gs.whiteToMove and playerOne) or (not gs.whiteToMove and playerTwo)

        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            # Mouse handler
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver and humanTurn:
                    location = p.mouse.get_pos() # (x, y) location of mouse
                    col = location[0] // SQ_SIZE
                    row = location[1] // SQ_SIZE

                    if sqSelected == (row, col): # The user clicked the same square twice
                        sqSelected = () # Deselect
                        playerClicks = [] # Clear player clicks
                    else:
                        sqSelected = (row, col)
                        playerClicks.append(sqSelected) # Append for both 1st and 2nd clicks
                    
                    if len(playerClicks) == 2:  # After 2nd click
                        move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)

                        for i in range(len(validMoves)):                        
                            if move == validMoves[i]:  # Only print and execute valid moves
                                print(f'{move.pieceMoved} {move.getChessNotation()[:2]} => {move.getChessNotation()[2:]}')
                                gs.makeMove(validMoves[i])

                                moveMade = True
                                animate = True
                                sqSelected = () # Reset user clicks
                                playerClicks = []
                        if not moveMade:
                            playerClicks = [sqSelected]  # Keep the second click for correction
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z: # undo when 'z' is pressed
                    gs.undoMove()

                    gameOver = False
                    moveMade = True
                    animate = False

                if e.key == p.K_r: # Reset the board when 'r' is pressed
                    gameOver = False
                    gs = ChessEngine.GameState()
                    validMoves = gs.getValidMoves()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = False
                    animate = False

        # Bot move finder
        if not gameOver and not humanTurn:
            BotMove = SmartMoveFinder.findBestMove(gs, validMoves)
            if BotMove is None:
                BotMove = SmartMoveFinder.findRandomMove(validMoves)

            gs.makeMove(BotMove)

            moveMade = True
            animate = True

        if moveMade:
            if animate:
                animateMove(gs.moveLog[-1], screen, gs.board, clock)

            validMoves = gs.getValidMoves()
            moveMade = False 
            animate = False        

        drawGameState(screen, gs, validMoves, sqSelected)

        if gs.checkMate:
            gameOver = True

            if gs.whiteToMove:
                drawText(screen, 'Black wins by checkmate')
            else:
                drawText(screen, 'White wins by checkmate')
        elif gs.staleMate:
            gameOver = True

            drawText(screen, 'Stalemate')

        clock.tick(MAX_FPS)
        p.display.flip()

def highlightSquares(screen, gs, validMoves, sqSelected):
    if sqSelected != ():
        r, c = sqSelected

        if gs.board[r][c][0] == ('w' if gs.whiteToMove else 'b'):  # sqSelected is a piece that can be moved
            # Highlight selected piece
            s = p.Surface((SQ_SIZE, SQ_SIZE))

            s.set_alpha(100)  # Transparency value -> 0: Transparent; 255: Opaque
            s.fill(p.Color('yellow'))
            screen.blit(s, (c * SQ_SIZE, r * SQ_SIZE))

            # Highlight moves with a circle
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    # Draw a circle for possible moves
                    circle_radius = SQ_SIZE // 5  # Adjust the radius as needed
                    circle_color = (0, 0, 0, 75)  # Green with transparency (RGBA)
                    # Create a transparent surface for the circle
                    circle_surface = p.Surface((SQ_SIZE, SQ_SIZE), p.SRCALPHA)

                    p.draw.circle(circle_surface, circle_color, (SQ_SIZE // 2, SQ_SIZE // 2), circle_radius)
                    screen.blit(circle_surface, (move.endCol * SQ_SIZE, move.endRow * SQ_SIZE))


# Responsible for all the graphics within a current game state.
def drawGameState(screen, gs, validMoves, sqSelected):
    drawBoard(screen) # Draw squares on the board
    highlightSquares(screen, gs, validMoves, sqSelected)
    drawPieces(screen, gs.board) # Draw pieces on top of those squares

# Draw the squares on the board. The top left square is always light.
def drawBoard(screen):
    global colors

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

# Animating a move
def animateMove(move, screen, board, clock):
    global colors

    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol

    animationTime = 0.1  # Total animation time in seconds (constant)
    frameCount = int(animationTime * MAX_FPS)  # Total number of frames
    
    for frame in range(frameCount + 1):
        # Compute the current row and column positions based on the frame
        r = move.startRow + dR * (frame / frameCount)
        c = move.startCol + dC * (frame / frameCount)
        
        # Redraw the board and pieces
        drawBoard(screen)
        drawPieces(screen, board)

        # Handle en passant: Erase the captured pawn
        if move.isEnPassantMove:
            enPassantRow = move.startRow + (1 if move.pieceMoved[0] == 'w' else -1)
            color = colors[(enPassantRow + move.endCol) % 2]
            enPassantSquare = p.Rect(move.endCol * SQ_SIZE, enPassantRow * SQ_SIZE, SQ_SIZE, SQ_SIZE)
            p.draw.rect(screen, color, enPassantSquare)

        # Erase the piece moved from its ending square
        color = colors[(move.endRow + move.endCol) % 2]
        endSquare = p.Rect(move.endCol * SQ_SIZE, move.endRow * SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, endSquare)

        # Draw the captured piece (if any, excluding en passant)
        if move.pieceCaptured != '--' and not move.isEnPassantMove:
            screen.blit(IMAGES[move.pieceCaptured], endSquare)

        # Draw the moving piece
        screen.blit(IMAGES[move.pieceMoved], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))
        
        # Update the display and control the frame rate
        p.display.flip()
        clock.tick(MAX_FPS)

def drawText(screen, text):
    # Define font and colors
    font = p.font.SysFont('Sans Serif', 48, False, False)
    outlineColor = p.Color("black")  # Black outline
    textColor = p.Color((129, 182, 76))  # Main green text color

    # Render the text object for the main text
    textObject = font.render(text, True, textColor)
    textOutline = font.render(text, True, outlineColor)

    # Determine the location for the text (centered)
    textLocation = p.Rect(0, 0, WIDTH, HEIGHT).move(
        WIDTH / 2 - textObject.get_width() / 2,
        HEIGHT / 2 - textObject.get_height() / 2)

    # Draw outline by rendering slightly offset versions of the text
    offsets = [(-2, -2), (-2, 0), (-2, 2), (0, -2), (0, 2), (2, -2), (2, 0), (2, 2)]
    for dx, dy in offsets:
        screen.blit(textOutline, textLocation.move(dx, dy))

    # Draw the main text on top of the outline
    screen.blit(textObject, textLocation)


if __name__ == '__main__':
    main()