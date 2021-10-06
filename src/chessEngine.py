"""
    This class will be responsible for storing all the information about the current state of the chess game.
    It will also generate all the valid moves from the current state.
    It will also contain a log of all the moves played till the current state.
"""
class GameState():
    def __init__(self):
        # The chessboard is an 8 by 8 2D list, each element of the list has 2 characters
        # A sqaure with a chess piece on it is represented by a string of two alphabets while an empty square with no piece is represented by the string "--"
        # The first character of a chess piece represents the color of the piece 'w' - white, 'b' - black
        # And the second character represents the type of the piece 'p' - pawn, 'R' - rook, 'N' - Knight, 'B' - Bishop 'Q' - Queen, 'K' - King
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
        ]
        self.moveFunctions = {'P' : self.getPawnMoves, 'R' : self.getRookMoves, 'N' : self.getKnightMoves,
         'B' : self.getBishopMoves, 'Q' : self.getQueenMoves, 'K' : self.getKingMoves}
        self.whiteToMove = True
        self.movesLog = []
        self.whiteKingLocation = (7,4)
        self.blackKingLocation = (0,4)
        self.checkMate = False
        self.staleMate = False

    '''
        Takes a move and executes it (will not work for castling , pawn promotion , en-passant)
    '''
    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.movesLog.append(move) # log the move so it can be used to undo if needed
        self.whiteToMove = not self.whiteToMove # opposite player's turn
        if move.pieceMoved == "wK":
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == "bK":
            self.blackKingLocation = (move.endRow, move.endCol)

    '''
        Undo the last move
    '''
    def undoMove(self):
        if len(self.movesLog) != 0: #there should be some move
            move = self.movesLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove
            if move.pieceMoved == "wK":
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == "bK":
                self.blackKingLocation = (move.startRow, move.startCol)

    '''
        All moves considering checks(King Under Attack)
    '''
    def getValidMoves(self):
        # 1) generate all possible moves
        moves = self.getAllPossibleMoves() # just for now
        # 2) make the move
        for i in range(len(moves)-1, -1, -1):
            self.makeMove(moves[i])
            # 3) generate all opponent's moves
            # 4) for each of your opponent's moves, see if they attack your king
            self.whiteToMove = not self.whiteToMove
            if self.inCheck():
                moves.remove(moves[i]) # if the current player's king is still under attack then remove this move
            self.whiteToMove = not self.whiteToMove
            self.undoMove()
        
        if len(moves) == 0: # either in checkmate or stalemate
            if self.inCheck():
                self.checkMate = True
            else:
                self.staleMate = True
        else:
            # Just in case we undo after a checkmate/stalemate make it false explicitly to avoid any leaks by undo
            self.checkMate = False
            self.staleMate = False

        return moves
    
    '''
        Determine if the current player is in check
    '''

    def inCheck(self):
        if self.whiteToMove:
            return self.squareUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])
        else:
            return self.squareUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1])

    '''
        Determine if the enemy can attack the square(row, col)
    '''

    def squareUnderAttack(self, row, col):
        self.whiteToMove = not self.whiteToMove # switch to opponent's point of view
        oppMoves = self.getAllPossibleMoves()
        self.whiteToMove = not self.whiteToMove # switch back to original turn
        for move in oppMoves:
            if move.endRow == row and move.endCol == col: # square is under attack
                return True
        return False

    '''
        All moves without considering checks(King Under Attack)
    '''
    def getAllPossibleMoves(self):
        moves = []
        for row in range(len(self.board)):
            for col in range(len(self.board[row])):
                turn = self.board[row][col][0]
                if (turn == 'b' and not self.whiteToMove) or (turn == 'w' and self.whiteToMove):
                    piece = self.board[row][col][1]
                    self.moveFunctions[piece](row,col,moves)
        return moves


    '''
        Get all the possible moves for pawn (from row , col)
    '''
    def getPawnMoves(self , row , col , moves):
        if self.whiteToMove:
            if row-1 >=0 and self.board[row-1][col] == "--": # If the white pawn can be advanced one square
                moves.append(Move((row, col), (row-1, col), self.board))
                if row == 6 and self.board[row-2][col] == "--": # If the white pawn can advance 2 squares on initial move
                    moves.append(Move((row, col), (row-2, col), self.board))
            
            # Capturing moves by capturing pieces of opposite color
            if col-1 >=0 and self.board[row-1][col-1] != "--" and self.board[row-1][col-1][0] == 'b': # left diagonal move
                moves.append(Move((row, col), (row-1, col-1), self.board))
            if col+1 < 8 and self.board[row-1][col+1] != "--" and self.board[row-1][col+1][0] == 'b':  # right diagonal move
                moves.append(Move((row, col), (row-1, col+1), self.board))
                 
        else:
            if row+1 < 8 and self.board[row+1][col] == "--": # If the pawn can be advanced one square
                moves.append(Move((row, col), (row+1, col), self.board))
                if row == 1 and self.board[row+2][col] == "--": # If the black pawn can be advanced 2 squares on the initial move
                    moves.append(Move((row, col), (row+2, col), self.board))
            
            # Capturing moves by capturing pieces of opposite color
            if col-1 >=0 and self.board[row+1][col-1] != "--" and self.board[row+1][col-1][0] == 'w': # right diagonal move
                moves.append(Move((row, col), (row+1, col-1), self.board))
            if col+1 < 8 and self.board[row+1][col+1] != "--" and self.board[row+1][col+1][0] == 'w':  # left diagonal move
                moves.append(Move((row, col), (row+1, col+1), self.board))
            
        # add pawn promotion

    '''
        Get all the possible moves for rook 
    '''
    def getRookMoves(self , row , col ,moves):
        directions = [(-1,0) , (1,0) , (0,-1) , (0,1)]
        enemyColor = 'b' if self.whiteToMove else 'w'
        for d in directions:
            for i in range(1,8):
                endRow = row + d[0]*i
                endCol = col + d[1]*i
                if endRow>=0 and endRow<8 and endCol>=0 and endCol<8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece == '--':
                        moves.append(Move((row,col) , (endRow , endCol) , self.board))
                    elif endPiece[0] == enemyColor:   # if we capture then we need to break 
                        moves.append(Move((row,col) , (endRow , endCol) , self.board))
                        break
                    else: # if our piece is there then also we need to break
                        break
                else:
                    break


    '''
        Get all the possible moves for knight 
    '''
    def getKnightMoves(self , row , col ,moves):
        knightMoves = [(-2,-1) , (-2,1) , (2,-1) , (2,1) , (1,2) , (1,-2) , (-1,2) , (-1,-2)]
        ourColor = 'w' if self.whiteToMove else 'b'
        for m in knightMoves:
            endRow = row + m[0]
            endCol = col + m[1]
            if endRow>=0 and endRow<8 and endCol>=0 and endCol<8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != ourColor:
                    moves.append(Move((row,col) , (endRow , endCol) , self.board))


    '''
        Get all the possible moves for bishop 
    '''
    def getBishopMoves(self , row , col ,moves):
        directions = [(-1,-1) , (1,1) , (1,-1) , (-1,1)]  # just a diagonal
        enemyColor = 'b' if self.whiteToMove else 'w'
        for d in directions:
            for i in range(1,8):
                endRow = row + d[0]*i
                endCol = col + d[1]*i
                if endRow>=0 and endRow<8 and endCol>=0 and endCol<8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece == '--':
                        moves.append(Move((row,col) , (endRow , endCol) , self.board))
                    elif endPiece[0] == enemyColor:   # if we capture then we need to break 
                        moves.append(Move((row,col) , (endRow , endCol) , self.board))
                        break
                    else: # if our piece is there then also we need to break
                        break
                else:
                    break
        

    '''
        Get all the possible moves for queen 
    '''
    def getQueenMoves(self , row , col ,moves):
        self.getBishopMoves(row,col,moves)
        self.getRookMoves(row,col,moves)


    '''
        Get all the possible moves for king 
    '''
    def getKingMoves(self , row , col ,moves):
        kingMoves = [(-1,0) , (0,-1) , (1,0) , (0,1) , (-1,1) , (-1,-1) , (1,-1) , (1,1)]
        ourColor = 'w' if self.whiteToMove else 'b'
        for m in kingMoves:
            endRow = row + m[0]
            endCol = col + m[1]
            if endRow>=0 and endRow<8 and endCol>=0 and endCol<8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != ourColor:
                    moves.append(Move((row,col) , (endRow , endCol) , self.board))
    
    
        

class Move():

    # Mapping to map row and column to rank and file respectively
    ranksToRows = {"8" : 0, "7" : 1, "6" : 2, "5" : 3, "4" : 4, "3" : 5, "2" : 6, "1" : 7}
    rowsToRanks = {rows : ranks for ranks, rows in ranksToRows.items()}

    filesToCols = {"a" : 0, "b" : 1, "c" : 2, "d" : 3, "e" : 4, "f" : 5, "g" : 6, "h" : 7}
    colsToFiles = {cols : files for files, cols in filesToCols.items()}


    def __init__(self, startSquare, endSquare, board):
        self.startRow = startSquare[0]
        self.startCol = startSquare[1]
        self.endRow = endSquare[0]
        self.endCol = endSquare[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol

    """
        overriding the equals method
    """
    def __eq__(self, o: object) -> bool:
        if isinstance(o , Move):
            return self.moveID == o.moveID
        return False

    def getChessNotation(self):
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)

    def getRankFile(self, row, col):
        return self.colsToFiles[col] + self.rowsToRanks[row]
