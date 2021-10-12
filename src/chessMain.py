"""
    This is our main interaction file, which will be responsible for handling user Input and displaying the current GameState Object.
"""

import pygame as pg
import math
from pygame.constants import KEYDOWN
import chessEngine
import smartMoveFinder

WIDTH = HEIGHT = 512
DIMENSION = 8
SQUARE_SIZE = HEIGHT // DIMENSION
MAX_FPS = 28 # we'll use it for animation
IMAGES = {}

"""
    Initialize global dictionary of images. called only once
"""
def loadImages():
    pieces = ['wQ' , 'wK' , 'wP' , 'wR' , 'wN' , 'wB' , 'bQ' , 'bK' , 'bP' , 'bR' , 'bN' , 'bB']
    for piece in pieces:
        IMAGES[piece] = pg.transform.scale(pg.image.load(f"./images/{piece}.png") , (SQUARE_SIZE , SQUARE_SIZE))

    # now we can access any image like IMAGES['wP']



"""
    The main driver for our code. this will update user input and also changes graphics
"""
def main():
    pg.init()
    screen = pg.display.set_mode((WIDTH , HEIGHT))
    clock = pg.time.Clock()
    screen.fill(pg.Color('white'))

    gs = chessEngine.GameState()
    loadImages()

    validMoves = gs.getValidMoves()
    moveMade = False # Flag variable for when move is made
    animate = False # Flag variable for when we want to animate

    squareSelected = () # no squares selected initially and keeptracks of the last clicked
    playerClicks = [] # keeptracks of player's click [(6,4) , (4,4)] -> move piece from (6,4) to (4,4)
    running = True
    gameOver = False
    playerOne = True # if a human is playing white,then this will be true and if AI is playing then this will be False
    playerTwo = False # same as above but for Black
    while running:

        humanTurn = (gs.whiteToMove and playerOne) or (not gs.whiteToMove and playerTwo)

        for e in pg.event.get():
            if e.type == pg.QUIT:
                running = False
            elif e.type == pg.MOUSEBUTTONDOWN:  #mouse handler
                if not gameOver and humanTurn:
                    location = pg.mouse.get_pos() # returns a tuple (x,y) of mouse coordinates
                    col = location[0]//SQUARE_SIZE
                    row = location[1]//SQUARE_SIZE
                    if squareSelected == (row, col): # same square has been clicked twice, then we deselect the click
                        squareSelected = ()
                        playerClicks = []
                    else: # different square selected than the first click
                        squareSelected = (row, col)
                        playerClicks.append(squareSelected)
                    
                    if  len(playerClicks) == 2:# user wants to move a piece or 2nd click
                        move = chessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                        print(move.getChessNotation())
                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                gs.makeMove(validMoves[i])
                                moveMade = True
                                animate = True
                                # reset user clicks
                                squareSelected = ()
                                playerClicks = []
                                break
                        
                        if not moveMade:
                            playerClicks = [squareSelected]
            elif e.type == pg.KEYDOWN:    #keyboard handler
                if e.key == pg.K_z:  # control + z then undo move
                    gs.undoMove()
                    gs.undoMove() # comment this line for 2 player game, uncomment for player vs AI
                    moveMade = True
                    animate = False
                    gameOver = False
                elif e.key == pg.K_r: # reset the board when 'r' is pressed
                    gs = chessEngine.GameState()
                    validMoves = gs.getValidMoves()
                    squareSelected = ()
                    playerClicks = []
                    moveMade = False
                    animate = False
                    gameOver = False

        # AI Move finder 
        if not gameOver and not humanTurn:
            AIMove = smartMoveFinder.findBestMoveMinMax(gs, validMoves)
            if AIMove is None:
                AIMove = smartMoveFinder.findRandomMove(validMoves)
            gs.makeMove(AIMove)
            moveMade = True
            animate = True


        if moveMade:
            if(animate):
                animateMove(gs.movesLog[-1], screen, gs.board, clock)
            validMoves = gs.getValidMoves()
            animate = False
            moveMade = False

        drawGameState(screen , gs, validMoves, squareSelected)

        if gs.checkmate:
            gameOver = True
            if gs.whiteToMove:
                drawText(screen, "Black wins by checkmate")
            else:
                drawText(screen, "White wins by checkmate")
        elif gs.stalemate:
            gameOver = True
            drawText(screen, "Stalemate")

        clock.tick(MAX_FPS)
        pg.display.flip()



"""
    Responsible for graphics of current game state
"""
def drawGameState(screen , gs, validMoves, squareSelected):
    drawBoard(screen) #draw squares on the board
    highlightSquares(screen, gs, validMoves, squareSelected)
    drawPieces(screen , gs.board) #draw pieces on top of that squares



def drawBoard(screen):
    global colors
    colors = [pg.Color('white') , pg.Color('gray')]
    for row in range(DIMENSION):
        for col in range(DIMENSION):
            color = colors[(row+col)%2]# sum of the row number and column number in all white squares is even
            pg.draw.rect(screen , color , pg.Rect(col*SQUARE_SIZE , row*SQUARE_SIZE , SQUARE_SIZE , SQUARE_SIZE))



def drawPieces(screen , board):
    for row in range(DIMENSION):
        for col in range(DIMENSION):
            piece = board[row][col]
            if piece != "--": # not empty square then draw the piece
                screen.blit(IMAGES[piece] , pg.Rect(col*SQUARE_SIZE , row*SQUARE_SIZE , SQUARE_SIZE , SQUARE_SIZE))

'''
    Highlight the selected piece and it's valid moves
'''
def highlightSquares(screen, gs, validMoves, squareSelected):
    if squareSelected != ():
        row, col = squareSelected
        if gs.board[row][col][0] == ('w' if gs.whiteToMove else 'b'): # square selected is of the same color whose turn is there
            # highlight the selected square
            surface = pg.Surface((SQUARE_SIZE, SQUARE_SIZE))
            surface.set_alpha(100) # transparency value 0(transparent) to 255(opaque)
            surface.fill(pg.Color('blue'))
            screen.blit(surface, (col*SQUARE_SIZE, row*SQUARE_SIZE))
            # highlighting the valid moves from that piece
            surface.fill(pg.Color("yellow"))
            for move in validMoves:
                if move.startRow == row and move.startCol == col:
                    screen.blit(surface, (move.endCol*SQUARE_SIZE, move.endRow*SQUARE_SIZE))

            

'''
    Animating a move
'''

def animateMove(move, screen, board, clock):
    global colors
    coordinates = [] # list of coordinates that the animation will go through
    deltaRow = move.endRow - move.startRow
    deltaCol = move.endCol - move.startCol
    framesPerSquareMove = 13
    frameCount = math.isqrt((deltaRow * deltaRow) + (deltaCol*deltaCol)) * framesPerSquareMove
    for frame in range(frameCount+1):
        row, col = ((move.startRow + deltaRow*frame/frameCount, move.startCol + deltaCol*frame/frameCount))
        drawBoard(screen)
        drawPieces(screen, board)
        # Make it seem like the piece is not at endSquare by superimposing on it it's square Color 
        color = colors[(move.endRow+move.endCol)%2]
        endSquare = pg.Rect(move.endCol*SQUARE_SIZE, move.endRow*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
        pg.draw.rect(screen, color, endSquare)
        # Draw captured piece too on the square 
        if move.pieceCaptured != "--":
            screen.blit(IMAGES[move.pieceCaptured], endSquare)
        # draw the moving piece
        screen.blit(IMAGES[move.pieceMoved], pg.Rect(col*SQUARE_SIZE, row*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
        pg.display.flip()
        clock.tick(80)

def drawText(screen, text):
    font = pg.font.SysFont("arial", 36, True, False)
    textObject = font.render(text, 0, pg.Color("red"))
    textLocation = pg.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH/2 - textObject.get_width()/2, HEIGHT/2 - textObject.get_height()/2)
    screen.blit(textObject, textLocation)

if __name__ == "__main__":
    main()