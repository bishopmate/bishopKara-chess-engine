"""
    This is our main interaction file, which will be responsible for handling user Input and displaying the current GameState Object.
"""
import pygame as p

import chessEngine

WIDTH = HEIGHT = 840
DIMENSION = 8
SQUARE_SIZE = HEIGHT // DIMENSION
MAX_FPS = 18
IMAGES = {}

'''
    Initialising a global dictionary of images. It will be only called once initially to load the images of the pieces
'''


def loadImages():
    pieces = ["bp", "wp", "bR", "bN", "bB", "bQ", "bK", "wR", "wN", "wB", "wQ", "wK"]
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQUARE_SIZE, SQUARE_SIZE))


'''
    Main part of our code. Will handle the user input and graphics
'''


def main():
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = chessEngine.GameState()
    print(gs.board)
    loadImages()  # Only need to run this function once
    running = True
    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
        drawGameState(screen, gs)
        clock.tick(MAX_FPS)
        p.display.flip()


def drawGameState(screen, gs):
    drawBoard(screen)  # draw squares on the board
    # drawPieces(screen, gs.board)# draw pieces on a square


def drawBoard(screen):
    for x in range(8):
        for y in range(8):
            topLeftX = x * SQUARE_SIZE
            topLeftY = y * SQUARE_SIZE
            squareColor = "white"
            if (x + y) & 1:  # start from black
                squareColor = "grey"

            if squareColor == "grey":
                p.draw.rect(screen, squareColor, (topLeftX, topLeftY, SQUARE_SIZE, SQUARE_SIZE))


if __name__ == "__main__":
    main()
