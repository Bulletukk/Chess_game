from chessGame import *

def main():
    pygame.init()
    c = chessGame()
    screen = pygame.display.set_mode((881,637))
    running = True
    mouseButtonPressed = False
    waitbeforeAIMove = 50
    while running:
        mCoord = pygame.mouse.get_pos() #Mouse position in Pygame coordinates
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN and not mouseButtonPressed and c.gameSituation==gameSituation.inGame:
                mouseButtonPressed = True
                c.pickUpPiece(mCoord)
            elif event.type == pygame.MOUSEBUTTONUP and mouseButtonPressed and c.gameSituation==gameSituation.inGame:
                mouseButtonPressed = False
                if c.hoverPiece is not None:
                    c.placePiece(mCoord)
            elif event.type == pygame.MOUSEBUTTONDOWN and not mouseButtonPressed and c.gameSituation!=gameSituation.inGame:
                mouseButtonPressed = True
                c.chooseFromMenu(mCoord)
            elif event.type == pygame.MOUSEBUTTONUP and mouseButtonPressed and c.gameSituation!=gameSituation.inGame:
                #No action.
                mouseButtonPressed = False
            elif event.type == pygame.QUIT:
                #Red X button pressed, exit game.
                running = False
        if c.shouldDoAIMove:
            waitbeforeAIMove -= 1
            if waitbeforeAIMove<=0:
                doAIMove(c) #Commenting out disables all AI.
                waitbeforeAIMove = 100
        screen.fill("grey")
        c.draw(screen)
        if c.hoverPiece is not None:
            pygame.draw.polygon(screen,oppositeColour(c.hoverPiece.getColour()),shiftPoints(c.hoverPiece.pointsToDraw((mCoord[0],mCoord[1]+18)),(mCoord[0],mCoord[1]+18)))
            pygame.draw.polygon(screen,c.hoverPiece.getColour(),c.hoverPiece.pointsToDraw((mCoord[0],mCoord[1]+18)))
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()