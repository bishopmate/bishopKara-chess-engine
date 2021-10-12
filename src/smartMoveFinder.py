import random

pieceScore = {"K" : 200, "P" : 1, "B" : 3, "N" : 3, "R" : 5, "Q": 9} # Reference : https://en.wikipedia.org/wiki/Computer_chess#Leaf_evaluation
CHECKMATE = 1300
STALEMATE = 0


def findRandomMove(validMoves):
    return validMoves[random.randint(0 , len(validMoves) - 1)]


def findBestMove(gs, validMoves):
    turnMultiplier = 1 if gs.whiteToMove else -1
    opponentMinMaxScore = CHECKMATE
    bestPlayerMove = None 
    # mobilityWeight = 0.1 # Reference - https://www.chessprogramming.org/Evaluation
    random.shuffle(validMoves)
    for candidateMove in validMoves:
        gs.makeMove(candidateMove)
        opponentsMoves = gs.getValidMoves()
        opponentMaxScore = -CHECKMATE
        for opponentCandidateMove in opponentsMoves:
            gs.makeMove(opponentCandidateMove)
            # gs.whiteToMove = not gs.whiteToMove # comment if mobilityWeight is not needed
            if gs.checkmate:
                score = -turnMultiplier*CHECKMATE
            elif gs.stalemate:
                score = STALEMATE
            else:
                score = -turnMultiplier*(scoreBasedOnMaterial(gs.board)) # uncomment if mobilityWeight is not needed
                # score = turnMultiplier*(scoreBasedOnMaterial(gs.board) + mobilityWeight*len(gs.getValidMoves()))# comment if mobilityWeight is not needed
        
            # gs.whiteToMove = not gs.whiteToMove# comment if mobilityWeight is not needed
            if score > opponentMaxScore:
                opponentMaxScore = score
            gs.undoMove()
        
        if opponentMinMaxScore < opponentMaxScore : 
            opponentMinMaxScore = opponentMaxScore
            bestPlayerMove = candidateMove
        gs.undoMove()

    return bestPlayerMove


def scoreBasedOnMaterial(board):
    score = 0
    for row in board:
        for square in row:
            if square[0] == 'w':
                score += pieceScore[square[1]]
            elif square[0] == 'b':
                score -= pieceScore[square[1]]
    
    
    return score

            