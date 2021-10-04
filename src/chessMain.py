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

# all folders are inside this PATH so write like: {PATH}src/chessEngine.py
PATH = "C:/Users/RAHUL/Desktop/Rahul/VSCode/.vscode/project/chess_engine/bishopKara-chess-engine/"

"""
    Initialize global dictionary of images. called only once
"""

def loadImages():
    pieces = ['wQ' , 'wK' , 'wP' , 'wR' , 'wN' , 'wB' , 'bQ' , 'bK' , 'bP' , 'bR' , 'bN' , 'bB']

    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load(f"{PATH}images/{piece}.png") , (SQUARE_SIZE , SQUARE_SIZE))

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

    running = True
    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
        drawGameState(screen , gs)
        clock.tick(MAX_FPS)
        p.display.flip()


"""
    Responsible for graphics of current game state
"""

def drawGameState(screen , gs):
    drawBoard(screen) #draw sqaures on the board
    #add suggestion or highlighting (later)
    drawPieces(screen , gs.board) #draw pieces on top of that squares


def drawBoard(screen):
    colors = [p.Color('white') , p.Color('gray')]

    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[(r+c)%2]
            p.draw.rect(screen , color , p.Rect(c*SQUARE_SIZE , r*SQUARE_SIZE , SQUARE_SIZE , SQUARE_SIZE))

def drawPieces(screen , board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--": # not piece then draw
                screen.blit(IMAGES[piece] , p.Rect(c*SQUARE_SIZE , r*SQUARE_SIZE , SQUARE_SIZE , SQUARE_SIZE))

if __name__ == "__main__":
    main()