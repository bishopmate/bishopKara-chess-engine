"""
    This class will be responsible for storing all the information about the current state of the chess game.
    It will also generate all the valid moves from the current state.
    It will also contain a log of all the moves played till the current state.
"""
from typing import Counter


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
        self.inCheck = False
        self.pins = []
        self.checks = []
        self.enPassantPossible = () # coordinates of the square where en passant capture is possible
        self.checkmate = False   
        self.stalemate = False
        self.currCastlingRight = castleRights(True , True , True , True)
        self.castlingRightLog = [castleRights(self.currCastlingRight.wks , self.currCastlingRight.bks,
                                              self.currCastlingRight.wqs , self.currCastlingRight.bqs)]


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
        
        # if Pawn Promotion is happening
        if move.isPawnPromotion:
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + "Q"

        # enpassant move
        if move.isEnPassantMove:
            self.board[move.startRow][move.endCol] = "--"

        # updating enPassantPossible
        if move.pieceMoved[1] == 'P' and abs(move.startRow-move.endRow) == 2:# only on 2 square advances
            self.enPassantPossible = ((move.startRow+move.endRow//2), move.startCol)
        else : # this makes sure that only one enpassant is possible at a time and that too immediately after a 2 square advance
            self.enPassantPossible = ()
        

        # castling
        if move.isCastleMove:
            if move.endCol - move.startCol == 2:
                self.board[move.endRow][move.endCol - 1] =  self.board[move.endRow][move.endCol + 1]
                self.board[move.endRow][move.endCol + 1] = '--'
            else:
                self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 2]
                self.board[move.endRow][move.endCol - 2] = '--'

        # update castling Rights - whenever it is a rook or kings move
        self.updateCastleRights(move)
        self.castlingRightLog.append(castleRights(self.currCastlingRight.wks , self.currCastlingRight.bks,
                                              self.currCastlingRight.wqs , self.currCastlingRight.bqs))

    """
        update the castle rights given a move
    """
    def updateCastleRights(self , move):
        if move.pieceMoved == 'bK':
            self.currCastlingRight.bqs = False
            self.currCastlingRight.bks = False
        elif move.pieceMoved == 'wK':
            self.currCastlingRight.wks = False
            self.currCastlingRight.wqs = False
        elif move.pieceMoved == 'wR':
            if move.startRow == 7:
                if move.startCol == 0: # left rook
                    self.currCastlingRight.wqs = False
                elif move.startCol == 7: # right rook
                    self.currCastlingRight.wks = False
        elif move.pieceMoved == 'bR':
            if move.startRow == 0:
                if move.startCol == 0: # left rook
                    self.currCastlingRight.bqs = False
                elif move.startCol == 7: # right rook
                    self.currCastlingRight.bks = False

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

            # undo enPassant
            if move.isEnPassantMove:
                self.board[move.endRow][move.endCol] = "--"
                self.board[move.startRow][move.endCol] = move.pieceCaptured
                self.enPassantPossible = (move.endRow, move.endCol)
            
            # undo 2 square advance
            if move.pieceMoved[1] == 'P' and abs(move.startRow - move.endRow) == 2:
                self.enPassantPossible = ()

            # undo castling
            self.castlingRightLog.pop()
            self.currCastlingRight = self.castlingRightLog[-1]
            
            if move.isCastleMove:
                if move.endCol - move.startCol == 2 :
                    self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 1]
                    self.board[move.endRow][move.endCol - 1] = '--'
                else:
                    self.board[move.endRow][move.endCol - 2] = self.board[move.endRow][move.endCol + 1]
                    self.board[move.endRow][move.endCol + 1] = '--'

            self.checkmate = False
            self.stalemate = False

    '''
        All moves considering checks(King Under Attack)
    '''
    def getValidMoves(self):
        tempEnPassantPossible = self.enPassantPossible
        tempCastleRights = castleRights(self.currCastlingRight.wks , self.currCastlingRight.bks,
                                        self.currCastlingRight.wqs , self.currCastlingRight.bqs)
        moves = []
        self.inCheck , self.pins , self.checks = self.checkForPinsAndChecks()
        if self.whiteToMove:
            kingRow = self.whiteKingLocation[0]
            kingCol = self.whiteKingLocation[1]
        else:
            kingRow = self.blackKingLocation[0]
            kingCol = self.blackKingLocation[1]
        
        if self.inCheck:
            if len(self.checks) == 1: # only 1 check -> block check or move kings
                moves = self.getAllPossibleMoves()
                if self.whiteToMove:
                    self.getCastleMoves(self.whiteKingLocation[0] , self.whiteKingLocation[1] , moves)  
                else:
                    self.getCastleMoves(self.blackKingLocation[0] , self.blackKingLocation[1] , moves)
                # to block one of piece should be between kings and enemy's piece
                check = self.checks[0]
                checkRow = check[0]
                checkCol = check[1]
                pieceChecking = self.board[checkRow][checkCol]
                validSquares = [] # block where piece can move
                if pieceChecking == 'N': # if it's knight we must capture knight
                    validSquares = [(checkRow , checkCol)]
                else:
                    for i in range(1,8):
                        validSquare = (kingRow + check[2]*i , kingCol + check[3]*i)
                        validSquares.append(validSquare)
                        if validSquare[0] == checkRow and validSquare[1] == checkCol:
                            break
                # get rid of the moves that don't block check or move king
                for i in range(len(moves)-1 , -1 , -1):
                    if moves[i].pieceMoved[1] != 'K':
                        if not (moves[i].endRow , moves[i].endCol) in validSquares:
                            moves.remove(moves[i])
            else: # double checks
                self.getKingMoves(kingRow , kingCol , moves)
        else: # no checks means all are valid
            moves = self.getAllPossibleMoves()
            if self.whiteToMove:
                self.getCastleMoves(self.whiteKingLocation[0] , self.whiteKingLocation[1] , moves)  
            else:
                self.getCastleMoves(self.blackKingLocation[0] , self.blackKingLocation[1] , moves)
        self.enPassantPossible = tempEnPassantPossible
        self.currCastlingRight = tempCastleRights
        if len(moves) == 0:
            if self.inCheck:
                self.checkmate = True
            else:
                self.stalemate = True

        return moves


    # Naive Algorithm
    # def getValidMoves(self):
    #     # 1) generate all possible moves
    #     moves = self.getAllPossibleMoves() # just for now
    #     # 2) make the move
    #     for i in range(len(moves)-1, -1, -1):
    #         self.makeMove(moves[i])
    #         # 3) generate all opponent's moves
    #         # 4) for each of your opponent's moves, see if they attack your king
    #         self.whiteToMove = not self.whiteToMove
    #         if self.inCheck():
    #             moves.remove(moves[i]) # if the current player's king is still under attack then remove this move
    #         self.whiteToMove = not self.whiteToMove
    #         self.undoMove()
        
    #     if len(moves) == 0: # either in checkmate or stalemate
    #         if self.inCheck():
    #             self.checkMate = True
    #         else:
    #             self.staleMate = True
    #     else:
    #         # Just in case we undo after a checkmate/stalemate make it false explicitly to avoid any leaks by undo
    #         self.checkMate = False
    #         self.staleMate = False

    #     return moves
    
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
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1 , -1 , -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piecePinned = True
                pinDirection = (self.pins[i][2] , self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        if self.whiteToMove:
            if row-1 >=0 and self.board[row-1][col] == "--": # If the white pawn can be advanced one square
                if not piecePinned or pinDirection == (-1,0):
                    moves.append(Move((row, col), (row-1, col), self.board))
                    if row == 6 and self.board[row-2][col] == "--": # If the white pawn can advance 2 squares on initial move
                        moves.append(Move((row, col), (row-2, col), self.board))
            
            # Capturing moves by capturing pieces of opposite color
            if col-1 >=0 and self.board[row-1][col-1][0] == 'b': # left diagonal move
                if not piecePinned or pinDirection == (-1,-1):
                    moves.append(Move((row, col), (row-1, col-1), self.board))
            elif (row-1, col-1) == self.enPassantPossible:
                moves.append(Move((row, col), (row-1, col-1), self.board, isEnPassantMove = True))


            if col+1 < 8 and self.board[row-1][col+1][0] == 'b':  # right diagonal move
                if not piecePinned or pinDirection == (-1,1):
                    moves.append(Move((row, col), (row-1, col+1), self.board))
            elif (row-1, col+1) == self.enPassantPossible:
                moves.append(Move((row, col), (row-1, col+1), self.board, isEnPassantMove = True))
                 
        else: # black pawn moves
            if row+1 < 8 and self.board[row+1][col] == "--": # If the pawn can be advanced one square
                if not piecePinned or pinDirection == (1,0):
                    moves.append(Move((row, col), (row+1, col), self.board))
                    if row == 1 and self.board[row+2][col] == "--": # If the black pawn can be advanced 2 squares on the initial move
                        moves.append(Move((row, col), (row+2, col), self.board))
            
            # Capturing moves by capturing pieces of opposite color
            if col-1 >=0 and self.board[row+1][col-1][0] == 'w': # right diagonal move
                if not piecePinned or pinDirection == (1,-1):
                    moves.append(Move((row, col), (row+1, col-1), self.board))
            elif (row+1, col-1) == self.enPassantPossible:
                moves.append(Move((row, col), (row+1, col-1), self.board, isEnPassantMove = True))

            if col+1 < 8 and self.board[row+1][col+1][0] == 'w':  # left diagonal move
                if not piecePinned or pinDirection == (1,1):
                    moves.append(Move((row, col), (row+1, col+1), self.board))
            elif (row+1, col+1) == self.enPassantPossible:
                moves.append(Move((row, col), (row+1, col+1), self.board, isEnPassantMove = True))
            
        # add pawn promotion

    '''
        Get all the possible moves for rook 
    '''
    def getRookMoves(self , row , col ,moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1 , -1 , -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piecePinned = True
                pinDirection = (self.pins[i][2] , self.pins[i][3])
                if self.board[row][col][1] != 'Q': # can't remove Queen
                    self.pins.remove(self.pins[i])
                break

        directions = [(-1,0) , (1,0) , (0,-1) , (0,1)]
        enemyColor = 'b' if self.whiteToMove else 'w'
        for d in directions:
            for i in range(1,8):
                endRow = row + d[0]*i
                endCol = col + d[1]*i
                if endRow>=0 and endRow<8 and endCol>=0 and endCol<8:
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0] , -d[1]):
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
        piecePinned = False
        for i in range(len(self.pins) - 1 , -1 , -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piecePinned = True
                self.pins.remove(self.pins[i])
                break

        knightMoves = [(-2,-1) , (-2,1) , (2,-1) , (2,1) , (1,2) , (1,-2) , (-1,2) , (-1,-2)]
        ourColor = 'w' if self.whiteToMove else 'b'
        for m in knightMoves:
            endRow = row + m[0]
            endCol = col + m[1]
            if endRow>=0 and endRow<8 and endCol>=0 and endCol<8:
                if not piecePinned:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] != ourColor:
                        moves.append(Move((row,col) , (endRow , endCol) , self.board))


    '''
        Get all the possible moves for bishop 
    '''
    def getBishopMoves(self , row , col ,moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1 , -1 , -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piecePinned = True
                pinDirection = (self.pins[i][2] , self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        directions = [(-1,-1) , (-1,1) , (1,-1) , (1,1)]  # just a diagonal
        enemyColor = 'b' if self.whiteToMove else 'w'
        for d in directions:
            for i in range(1,8):
                endRow = row + d[0]*i
                endCol = col + d[1]*i
                if endRow>=0 and endRow<8 and endCol>=0 and endCol<8:
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0] , -d[1]):
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
    def getQueenMoves(self , row , col ,moves):# queen's moves are a combination of bishop's and rook's moves
        # rook type moves
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1 , -1 , -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piecePinned = True
                pinDirection = (self.pins[i][2] , self.pins[i][3])
                if self.board[row][col][1] != 'Q': # can't remove Queen
                    self.pins.remove(self.pins[i])
                break

        directions = [(-1,0) , (1,0) , (0,-1) , (0,1)]
        enemyColor = 'b' if self.whiteToMove else 'w'
        for d in directions:
            for i in range(1,8):
                endRow = row + d[0]*i
                endCol = col + d[1]*i
                if endRow>=0 and endRow<8 and endCol>=0 and endCol<8:
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0] , -d[1]):
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
        for i in range(len(self.pins) - 1 , -1 , -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piecePinned = True
                pinDirection = (self.pins[i][2] , self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
        
        # bishop type moves
        directions = [(-1,-1) , (-1,1) , (1,-1) , (1,1)]  # just a diagonal
        enemyColor = 'b' if self.whiteToMove else 'w'
        for d in directions:
            for i in range(1,8):
                endRow = row + d[0]*i
                endCol = col + d[1]*i
                if endRow>=0 and endRow<8 and endCol>=0 and endCol<8:
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0] , -d[1]):
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
        Get all the possible moves for king 
    '''
    def getKingMoves(self , row , col ,moves):
        rowMoves = [-1,-1,-1,0,0,1,1,1]
        colMoves = [-1,0,1,-1,1,-1,0,1]
        ourColor = 'w' if self.whiteToMove else 'b'
        for m in range(8):
            endRow = row + rowMoves[m]
            endCol = col + colMoves[m]
            if endRow>=0 and endRow<8 and endCol>=0 and endCol<8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != ourColor: # not our piece

                    #place the king on the square and check if it would receive a check
                    if ourColor == 'w':
                        self.whiteKingLocation = (endRow , endCol)
                    else:
                        self.blackKingLocation = (endRow , endCol)
                    inCheck , pins , checks = self.checkForPinsAndChecks()

                    if not inCheck:
                        moves.append(Move((row,col) , (endRow , endCol) , self.board))

                    # placing king back on it's location
                    if ourColor == 'w':
                        self.whiteKingLocation = (row , col)
                    else:
                        self.blackKingLocation = (row , col)    

    
    """
        Generate all possible castle moves for king
    """
    def getCastleMoves(self , row , col , moves):
        if self.squareUnderAttack(row , col , ):
            return # can't castle
        if (self.whiteToMove and self.currCastlingRight.wks) or (not self.whiteToMove and self.currCastlingRight.bks):
            self.getKingSideCastleMoves(row , col , moves)
        
        if (self.whiteToMove and self.currCastlingRight.wqs) or (not self.whiteToMove and self.currCastlingRight.bqs):
            self.getQueenSideCastleMoves(row , col , moves)
    
    def getKingSideCastleMoves(self , row , col , moves):
        if self.board[row][col+1] == '--' and self.board[row][col+2] == '--':
            if not self.squareUnderAttack(row , col + 1) and not self.squareUnderAttack(row , col+2):
                moves.append(Move((row , col) , (row , col + 2) , self.board , isCastleMove = True))

    def getQueenSideCastleMoves(self , row , col , moves):
        if self.board[row][col-1] == '--' and self.board[row][col-2] == '--' and self.board[row][col-3]:
            if not self.squareUnderAttack(row , col - 1) and not self.squareUnderAttack(row , col - 2):
                moves.append(Move((row , col) , (row , col - 2) , self.board , isCastleMove = True))


    
    def checkForPinsAndChecks(self):
        pins = []
        checks = []
        inCheck = False
        if self.whiteToMove:
            enemyColor = 'b'
            ourColor = 'w'
            startRow = self.whiteKingLocation[0]
            startCol = self.whiteKingLocation[1]
        else:
            enemyColor = 'w'
            ourColor = 'b'
            startRow = self.blackKingLocation[0]
            startCol = self.blackKingLocation[1]
        
        directions = [(-1,0) , (0,-1) , (1,0) , (0,1) , (-1,-1) , (-1,1) , (1,-1) , (1,1)]
        for j in range(len(directions)):
            d = directions[j]
            possiblePin = ()
            for i in range(1,8):
                endRow = startRow + d[0]*i
                endCol = startCol + d[1]*i
                if endRow>=0 and endRow<8 and endCol>=0 and endCol<8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] == ourColor and endPiece[1] != 'K':
                        if possiblePin == (): # 1st pin
                            possiblePin = (endRow , endCol , d[0] , d[1])
                        else: # 2nd our piece then 1st one can not be pin
                            break
                    elif endPiece[0] == enemyColor:
                        type = endPiece[1]
                        # 5 possibilities
                        # 1 rook : orthogonally away from king 
                        # 2 bishop : diagonally away
                        # 3 pawn : 1 square diagonally away
                        # 4 queen : any direction
                        # 5 king : 1 square away in any direction
                        if (0<=j<=3 and type == 'R') or (4<=j<=7 and type == 'B') or (i == 1  and type == 'P' and ((enemyColor == 'b' and 4<=j<=5) or (enemyColor == 'w' and 6<=j<=7))) or (type == 'Q') or (i==1 and type == 'K'):
                            if possiblePin == ():
                                inCheck = True
                                checks.append((endRow , endCol , d[0] , d[1]))
                                break
                            else: # if it's pins
                                pins.append(possiblePin)
                                break
                        else:
                            break 
                else: #off-board
                    break
        #check for knight moves
        knightMoves = [(-2,-1) , (-2 , 1) , (2,-1) , (2,1) , (-1,2) , (1,2) ,(1,-2) , (-1,-2)]
        for m in knightMoves:
            endRow = startRow + m[0]
            endCol = startCol + m[1]
            if endRow>=0 and endRow<8 and endCol>=0 and endCol<8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] == enemyColor and endPiece[1] == 'N':
                    inCheck = True
                    checks.append((endRow ,endCol , m[0] , m[1]))
        return inCheck , pins , checks
    
class castleRights():
    def __init__(self, wks , bks , wqs , bqs) -> None:
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs
    

class Move():

    # Mapping to map row and column to rank and file respectively
    ranksToRows = {"8" : 0, "7" : 1, "6" : 2, "5" : 3, "4" : 4, "3" : 5, "2" : 6, "1" : 7}
    rowsToRanks = {rows : ranks for ranks, rows in ranksToRows.items()}

    filesToCols = {"a" : 0, "b" : 1, "c" : 2, "d" : 3, "e" : 4, "f" : 5, "g" : 6, "h" : 7}
    colsToFiles = {cols : files for files, cols in filesToCols.items()}


    def __init__(self, startSquare, endSquare, board, isEnPassantMove = False , isCastleMove = False):
        self.startRow = startSquare[0]
        self.startCol = startSquare[1]
        self.endRow = endSquare[0]
        self.endCol = endSquare[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        
        self.isPawnPromotion = (self.pieceMoved == "wP" and self.endRow == 0) or (self.pieceMoved == "bP" and self.endRow == 7)
        
        self.isCastleMove = isCastleMove

        self.isEnPassantMove = isEnPassantMove
        if self.isEnPassantMove:
            self.pieceCaptured = "wP" if self.pieceMoved == "bP" else "bP"

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
