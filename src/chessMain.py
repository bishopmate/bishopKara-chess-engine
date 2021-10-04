"""
    This is our main interaction file, which will be responsible for handling user Input and displaying the current GameState Object.
"""

import pygame as p
import chessEngine

WIDTH = HEIGHT = 512
DIMENSION = 8
SQUARE_SIZE = HEIGHT // DIMENSION
MAX_FPS = 18 # we'll use it for animation
IMAGES = {}

"""
    Initialize global dictionary of images. called only once
"""
def loadImages():
    pieces = ['wQ' , 'wK' , 'wP' , 'wR' , 'wN' , 'wB' , 'bQ' , 'bK' , 'bP' , 'bR' , 'bN' , 'bB']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load(f"./images/{piece}.png") , (SQUARE_SIZE , SQUARE_SIZE))

    # now we can access any image like IMAGES['wP']



"""
    The main driver for our code. this will update user input and also changes graphics
"""
def main():
    p.init()
    screen = p.display.set_mode((WIDTH , HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color('white'))

    gs = chessEngine.GameState()
    loadImages()
    squareSelected = ()
    playerClicks = []
    running = True
    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            elif e.type == p.MOUSEBUTTONDOWN:
                location = p.mouse.get_pos() # returns a tuple (x,y) of mouse coordinates
                col = location[0]//SQUARE_SIZE
                row = location[1]//SQUARE_SIZE
                if squareSelected == (row, col): # same square has been clicked twice, then we deselect the click
                    squareSelected = ()
                    playerClicks = []
                else: # different square selected than the first click
                    squareSelected = (row, col)
                    playerClicks.append(squareSelected)
                
                if  len(playerClicks) == 2:# user wants to move a piece
                    move = chessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                    print(move.getChessNotation())
                    gs.makeMove(move)
                    # reset user clicks
                    squareSelected = ()
                    playerClicks = []

        drawGameState(screen , gs)
        clock.tick(MAX_FPS)
        p.display.flip()



"""
    Responsible for graphics of current game state
"""
def drawGameState(screen , gs):
    drawBoard(screen) #draw squares on the board
    #add suggestion or highlighting (later)
    drawPieces(screen , gs.board) #draw pieces on top of that squares



def drawBoard(screen):
    colors = [p.Color('white') , p.Color('gray')]
    for row in range(DIMENSION):
        for col in range(DIMENSION):
            color = colors[(row+col)%2]# sum of the row number and column number in all white squares is even
            p.draw.rect(screen , color , p.Rect(col*SQUARE_SIZE , row*SQUARE_SIZE , SQUARE_SIZE , SQUARE_SIZE))



def drawPieces(screen , board):
    for row in range(DIMENSION):
        for col in range(DIMENSION):
            piece = board[row][col]
            if piece != "--": # not empty square then draw the piece
                screen.blit(IMAGES[piece] , p.Rect(col*SQUARE_SIZE , row*SQUARE_SIZE , SQUARE_SIZE , SQUARE_SIZE))





if __name__ == "__main__":
    main()