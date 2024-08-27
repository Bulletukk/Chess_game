import chessBoard, chessGUI, chessAI
import pygame

class chessGame:
    def __init__(self):
        self.hoverPiece = None
        self.gameSituation = chessBoard.gameSituation.start
        self.AIType = None
        self.updateTiles()
        self.shouldDoAIMove = False

    def runGame(self):
        pygame.init()
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

    def pickUpPiece(self,mCoord):
        location = self.pointToPieceLocation(mCoord)
        if location is not None:
            if self.hoverPiece != None:
                raise ValueError("Tried to pick up a piece when already holding a piece")
            piece = self.tiles[location[0]][location[1]]
            #Check if the piece has the correct colour:
            if piece is not None:
                if piece.getColour()==turnToColour(self.turn):
                    self.tiles[location[0]][location[1]] = None #Remove piece from board.
                    #Note that the piece still has the board location saved.
                    self.hoverPiece = piece

    def placePiece(self,mCoord):
        location = self.pointToPieceLocation(mCoord)
        if location is not None and self.hoverPiece!=None:
            if self.isLegalMove(self.hoverPiece,location):
                #If the place is occupied, remove piece at receiving location.
                if self.getTile(location) is not None:
                    self.catchPiece(self.getTile(location))
                #Move hoverPiece
                self.hoverPiece.hasMoved = True
                self.hoverPiece.setPosition(location)
                #If hoverpiece is a pawn that has reached the other side of the board, it will be converted to a queen.
                if type(self.hoverPiece)==pawn:
                    self.convertPawnIfReached(self.hoverPiece)
                self.updateTiles()
                self.checkCheckSituation() #Check must be checked before hoverpiece is reset.
                self.hoverPiece = None
                if not (self.gameSituation==gameSituation.blackWon or self.gameSituation==gameSituation.whiteWon):
                    self.switchTurns()
                    self.shouldDoAIMove = True
            else:
                #Put piece back.
                self.hoverPiece = None
                self.updateTiles()
        elif location==None:
            self.hoverPiece = None
            self.updateTiles()
        elif self.hoverPiece!=None:
            raise ValueError