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
        

    """
        Takes a move and executes it (will not work for castling , pawn promotion , en-passant)
    """
    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.movesLog.append(move) # log the move so it can be used to undo if needed
        self.whiteToMove = not self.whiteToMove # opposite player's turn


    """
        Undo the last move
    """
    def undoMove(self):
        if len(self.movesLog) != 0: #there should be some move
            move = self.movesLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove


    """
        All moves with checking
    """
    def getValidMoves(self):
        return self.getAllPossibleMoves() # just for now


    """
        All moves without checking
    """
    def getAllPossibleMoves(self):
        moves = []
        for row in range(len(self.board)):
            for col in range(len(self.board[row])):
                turn = self.board[row][col][0]
                if (turn == 'b' and not self.whiteToMove) or (turn == 'w' and self.whiteToMove):
                    piece = self.board[row][col][1]
                    self.moveFunctions[piece](row,col,moves)
        return moves


    """
        Get all the possible moves for pawn (from row , col)
    """
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
            


    """
        Get all the possible moves for rook 
    """
    def getRookMoves(self , row , col ,moves):
        pass

    """
        Get all the possible moves for knight 
    """
    def getKnightMoves(self , row , col ,moves):
        pass

    """
        Get all the possible moves for bishop 
    """
    def getBishopMoves(self , row , col ,moves):
        pass
        
    """
        Get all the possible moves for queen 
    """
    def getQueenMoves(self , row , col ,moves):
        pass
    

    """
        Get all the possible moves for king 
    """
    def getKingMoves(self , row , col ,moves):
        pass
    
    
        

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
