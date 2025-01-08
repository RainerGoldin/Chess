'''
This class is responsible for storing all the information about the current state of a chess game.
It will also be responsible for determining the valid moves at the current state and keep a move log.
'''

class GameState():
    def __init__(self):
        '''
        Board is an 8x8 2d list, each element of the list has 2 characters
        The first character represents the color of the pieces, 'b' or 'w'
        The second character represents the type of the pieces, 'K', 'Q', 'R', 'B', 'N', or 'P'
        The '--' represents an empty space with no piece
        '''
        self.board = [
            ['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR'],
            ['bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP'],
            ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR']]
        self.moveFunctions = {'P': self.getPawnMoves, 'N': self.getKnightMoves, 'B': self.getBishopMoves,
                              'R': self.getRookMoves, 'Q': self.getQueenMoves, 'K': self.getKingMoves}
        self.whiteToMove = True
        self.moveLog = []
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        self.checkMate = False
        self.staleMate = False
        self.enPassantPossible = () # Coordinates for the square where en Passant capture is possible
        self.currentCastlingRight = CastleRights(True, True, True, True)
        self.castleRightsLog = [CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks, 
                                             self.currentCastlingRight.wqs, self.currentCastlingRight.bqs)]

    # Takes a move as a parameter and executes it (this will not work for castling, and en'passant)
    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = '--'
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move) # Log the move so we can undo it
        self.whiteToMove = not self.whiteToMove # Swap players
        
        # Update the king's location if moved
        if move.pieceMoved == 'wK':
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == 'bK':
            self.blackKingLocation = (move.endRow, move.endCol)

        # Pawn promotion
        if move.pieceMoved[1] == 'P' and move.isPawnPromotion:
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + 'Q'

        # En Passant move
        if move.isEnPassantMove:
            self.board[move.startRow][move.endCol] = '--' # Capturing the pawn

        # Update en Passant Variable
        if move.pieceMoved[1] == 'P' and abs(move.startRow - move.endRow) == 2: # Only on 2 squares pawn advances
            self.enPassantPossible = ((move.startRow + move.endRow) // 2, move.startCol)
        else:
            self.enPassantPossible = ()

        # Castle move
        if move.isCastleMove:
            if move.endCol - move.startCol == 2: # King side castle move
                self.board[move.endRow][move.endCol-1] = self.board[move.endRow][move.endCol+1] # Moves the rook
                self.board[move.endRow][move.endCol+1] = '--' # Erase old rook
            else: # Queen side castle move
                self.board[move.endRow][move.endCol+1] = self.board[move.endRow][move.endCol-2] # Moves the rook
                self.board[move.endRow][move.endCol-2] = '--'

        # Update castling rights - whenever it is a rook or a king move
        self.updateCastleRights(move)
        self.castleRightsLog.append(CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks, 
                                                 self.currentCastlingRight.wqs, self.currentCastlingRight.bqs))

    # Undo the last move made
    def undoMove(self):
        # Make sure that there is a move to undo
        if len(self.moveLog) != 0:
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured 
            self.whiteToMove = not self.whiteToMove # Switch turns

            # Update the king's location if needed
            if move.pieceMoved == 'wK':
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == 'bK':
                self.blackKingLocation = (move.startRow, move.startCol)

            # Undo en Passant
            if move.isEnPassantMove:
                self.board[move.endRow][move.endCol] = '--' # Leave landing square blank
                self.board[move.startRow][move.endCol] = move.pieceCaptured
                self.enPassantPossible = (move.endRow, move.endCol)

            # Undo a 2 square pawn advance
            if move.pieceMoved[1] == 'P' and abs(move.startRow - move.endRow) == 2:
                self.enPassantPossible = ()

            # Undo castling rights
            self.castleRightsLog.pop() # Get rid of the new castle rights from the move we are undoing
            newRights = self.castleRightsLog[-1]
            self.currentCastlingRight = CastleRights(newRights.wks, newRights.bks, newRights.wqs, newRights.bqs)
            
            # Undo castle move
            if move.isCastleMove:
                if move.endCol - move.startCol == 2: # King side
                    self.board[move.endRow][move.endCol+1] = self.board[move.endRow][move.endCol-1]
                    self.board[move.endRow][move.endCol-1] = '--'
                else: # Queen side
                    self.board[move.endRow][move.endCol-2] = self.board[move.endRow][move.endCol+1]
                    self.board[move.endRow][move.endCol+1] = '--'         

    # Update the castle rights given the move
    def updateCastleRights(self, move):
        if move.pieceMoved == 'wK':
            self.currentCastlingRight.wks = False
            self.currentCastlingRight.wqs = False
        elif move.pieceMoved == 'bK':
            self.currentCastlingRight.bks = False
            self.currentCastlingRight.bqs = False
        elif move.pieceMoved == 'wR':
            if move.startRow == 7:
                if move.startCol == 0: # Left rook
                    self.currentCastlingRight.wqs = False
                elif move.startCol == 7: # Right rook
                    self.currentCastlingRight.wks = False
        elif move.pieceMoved == 'bR':
            if move.startRow == 0:
                if move.startCol == 0: # Left rook
                    self.currentCastlingRight.bqs = False
                elif move.startCol == 7: # Right rook
                    self.currentCastlingRight.bks = False

    # All moves considering checks
    def getValidMoves(self):
        # Debugging purpose
        '''
        for log in self.castleRightsLog:
            print(log.wks, log.wqs, log.bks, log.bqs, end=', ') 
        print()
        '''

        tempEnPassantPossible = self.enPassantPossible
        tempCastleRights = CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks, 
                                        self.currentCastlingRight.wqs, self.currentCastlingRight.bqs) # Copy the current castling rights
        moves = self.getAllPossibleMoves() # Generate all possible moves

        if self.whiteToMove:
            self.getCastleMoves(self.whiteKingLocation[0], self.whiteKingLocation[1], moves)
        else:
            self.getCastleMoves(self.blackKingLocation[0], self.blackKingLocation[1], moves)
        
        # For each move, make the move
        for i in range(len(moves)-1, -1, -1): # When removing an element from a list, go backwards through the list
            self.makeMove(moves[i])

            # For each opponent's moves, see if they attack your king
            self.whiteToMove = not self.whiteToMove

            # If they do attack your king, not a valid move
            if self.inCheck():
                moves.remove(moves[i])

            self.whiteToMove = not self.whiteToMove
            
            self.undoMove()

        if len(moves) == 0: #Either checkmate or stalemate
            if self.inCheck():
                self.checkMate = True
            else:
                self.staleMate = True
        else:
            self.checkMate = False
            self.staleMate = False

        self.enPassantPossible = tempEnPassantPossible
        self.currentCastlingRight = tempCastleRights
        return moves
    
    # Determine if the current player is in check
    def inCheck(self):
        if self.whiteToMove:
            return self.squareUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])
        else:
            return self.squareUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1])

    # Determine if the enemy can attack square r, c
    def squareUnderAttack(self, r, c):
        self.whiteToMove = not self.whiteToMove # Switch to opponent's turn
        oppMoves = self.getAllPossibleMoves() # Generate all opponent's moves
        self.whiteToMove = not self.whiteToMove # Switch turns back
        
        for move in oppMoves:
            if move.endRow == r and move.endCol == c: # Square is under attack
                return True
            
        return False

    # All moves without considering checks
    def getAllPossibleMoves(self):
        moves = []
        
        for r in range(len(self.board)): # Number of rows
            for c in range(len(self.board[r])): # Number of cols in given row
                turn = self.board[r][c][0]

                if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    piece = self.board[r][c][1]

                    self.moveFunctions[piece](r, c, moves) # Calls the appropriate move function based on piece type
        
        return moves

    # Get all the pawn moves for the pawn located at row, col and add these moves to the list
    def getPawnMoves(self, r, c, moves):
        if self.whiteToMove: # White pawn moves
            if self.board[r-1][c] == '--': # 1 Square pawn advance
                moves.append(Move((r, c), (r-1, c), self.board))

                if r == 6 and self.board[r-2][c] == '--': # 2 Square pawn advance
                    moves.append(Move((r, c), (r-2, c), self.board))

            if c-1 >= 0: # Captures to the left
                if self.board[r-1][c-1][0] == 'b': # Black piece to capture
                    moves.append(Move((r, c), (r-1, c-1), self.board))
                elif (r-1, c-1) == self.enPassantPossible:
                    moves.append(Move((r, c), (r-1, c-1), self.board, isEnPassantMove=True))

            if c+1 < len(self.board[0]): # Captures to the right
                if self.board[r-1][c+1][0] == 'b': # Black piece to capture
                    moves.append(Move((r, c), (r-1, c+1), self.board))
                elif (r-1, c+1) == self.enPassantPossible:
                    moves.append(Move((r, c), (r-1, c+1), self.board, isEnPassantMove=True))

        else: # Black pawn moves
            if self.board[r+1][c] == '--': # 1 Square pawn advance
                moves.append(Move((r, c), (r+1, c), self.board))

                if r == 1 and self.board[r+2][c] == '--': # 2 Square pawn advance
                    moves.append(Move((r, c), (r+2, c), self.board))

            if c-1 >= 0: # Captures to the left
                if self.board[r+1][c-1][0] == 'w': # White piece to capture
                    moves.append(Move((r, c), (r+1, c-1), self.board))
                elif (r+1, c-1) == self.enPassantPossible:
                    moves.append(Move((r, c), (r+1, c-1), self.board, isEnPassantMove=True))

            if c+1 < len(self.board[0]): # Captures to the right
                if self.board[r+1][c+1][0] == 'w': # White piece to capture
                    moves.append(Move((r, c), (r+1, c+1), self.board))
                elif (r+1, c+1) == self.enPassantPossible:
                    moves.append(Move((r, c), (r+1, c+1), self.board, isEnPassantMove=True))

        # Add pawn promotions later

    # Get all the bishop moves for the bishop located at row, col and add these moves to the list
    def getBishopMoves(self, r, c, moves):
        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))
        enemyColor = 'b' if self.whiteToMove else 'w'

        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i

                if 0 <= endRow < 8 and 0 <= endCol < 8: # On board
                    endPiece = self.board[endRow][endCol]
                    
                    if endPiece == '--': # Empty space valid
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    elif endPiece[0] == enemyColor: # Enemy valid piece
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                        break
                    else: # Friendly piece invalid
                        break
                else: # Off board
                    break

    # Get all the knight moves for the knight located at row, col and add these moves to the list
    def getKnightMoves(self, r, c, moves):
        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        allyColor = 'w' if self.whiteToMove else 'b'

        for m in knightMoves:
            endRow = r + m[0]
            endCol = c + m[1]

            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]

                if endPiece[0] != allyColor: # Not an ally piece (empty or enemy piece)
                    moves.append(Move((r, c), (endRow, endCol), self.board))

    # Get all the rook moves for the rook located at row, col and add these moves to the list
    def getRookMoves(self, r, c, moves):
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))
        enemyColor = 'b' if self.whiteToMove else 'w'

        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i

                if 0 <= endRow < 8 and 0 <= endCol < 8: # On board
                    endPiece = self.board[endRow][endCol]
                    
                    if endPiece == '--': # Empty space valid
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    elif endPiece[0] == enemyColor: # Enemy valid piece
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                        break
                    else: # Friendly piece invalid
                        break
                else: # Off board
                    break

    # Get all the queen moves for the queen located at row, col and add these moves to the list
    def getQueenMoves(self, r, c, moves):
        self.getRookMoves(r, c, moves)
        self.getBishopMoves(r, c, moves)

    # Get all the king moves for the king located at row, col and add these moves to the list
    def getKingMoves(self, r, c, moves):
        kingMoves = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1))
        allyColor = 'w' if self.whiteToMove else 'b'

        for i in range(8):
            endRow = r + kingMoves[i][0]
            endCol = c + kingMoves[i][1]

            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]

                if endPiece[0] != allyColor: # Not an ally piece (empty or enemy piece)
                    moves.append(Move((r, c), (endRow, endCol), self.board))

    # Generate all valid castle moves for the king at (r, c) and add them to the list of moves
    def getCastleMoves(self, r, c, moves):
        if self.squareUnderAttack(r, c):
            return # Can't castle while we are in check

        if (self.whiteToMove and self.currentCastlingRight.wks) or (not self.whiteToMove and self.currentCastlingRight.bks):
            self.getKingSideCastleMoves(r, c, moves)

        if (self.whiteToMove and self.currentCastlingRight.wqs) or (not self.whiteToMove and self.currentCastlingRight.bqs):
            self.getQueenSideCastleMoves(r, c, moves)

    def getKingSideCastleMoves(self, r, c, moves):
        if self.board[r][c+1] == '--' and self.board[r][c+2] == '--':
            if not self.squareUnderAttack(r, c+1) and not self.squareUnderAttack(r, c+2):
                moves.append(Move((r, c), (r, c+2), self.board, isCastleMove=True))

    def getQueenSideCastleMoves(self, r, c, moves):
        if self.board[r][c-1] == '--' and self.board[r][c-2] == '--' and self.board[r][c-3] == '--':
            if not self.squareUnderAttack(r, c-1) and not self.squareUnderAttack(r, c-2):
                moves.append(Move((r, c), (r, c-2), self.board, isCastleMove=True))

class CastleRights():
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs

class Move():
    # Maps keys to values
    ranksToRows = {'1':7, '2':6, '3':5, '4':4,
                    '5':3, '6':2, '7':1, '8':0}
    rowsToRanks = {v:k for k, v in ranksToRows.items()}
    filesToCols = {'a':0, 'b':1, 'c':2, 'd':3,
                    'e':4, 'f':5, 'g':6, 'h':7}
    colsToFiles = {v:k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board, isEnPassantMove=False, isCastleMove=False):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol
        self.isCastleMove = isCastleMove # Castle move
        self.isPawnPromotion = (self.pieceMoved == 'wP' and self.endRow == 0) or (self.pieceMoved and 'bP' and self.endRow == 7) # Pawn promotion
        # En Passant
        self.isEnPassantMove = isEnPassantMove

        if self.isEnPassantMove:
            self.pieceCaptured = 'wP' if self.pieceMoved == 'bP' else 'bP'

    # Overiding the equals method
    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    def getChessNotation(self):
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)

    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]