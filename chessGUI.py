import chessPiece, chessBoard
import pygame

def shiftPoints(pointsToDraw: list, bottomCentre: tuple):
    shiftedPoints = []
    for point in pointsToDraw:
        shiftedPoints.append((point[0] + 0.02*(point[0]-bottomCentre[0]), point[1] + 0.02*(point[1]-bottomCentre[1])))
    return shiftedPoints

def turnToColour(t:chessBoard.turn):
    if t==chessBoard.turn.white:
        return "white"
    else:
        return "black"
    
class chessGUI:
    def __init__(self):
        self._edgeBorderWidth = 5
        self._tileBorderWidth = 3
        self._tilesideLength = 60
        self._pieceMargin = self.tilesideLength/8 #How far up in the tile the bottom of the chess piece should be.
        self._boardWidth = 8*self.tilesideLength + 9*self.tileBorderWidth + 2*self.edgeBorderWidth
        self._topRightCorner = (180,60)
        pygame.init()
        screen = pygame.display.set_mode((881,637))

        self._menuChoice = {"BlackReplay":True,"WhiteReplay":True,"AIButtons":False}

    def draw(self,gameSituation) -> None:
        #Set background colour. Dark red if we're in check.
        if self.check != None:
            rectColor = "darkred"
        else:
            rectColor = "black"
        #Draw board
        pygame.draw.rect(screen,rectColor,pygame.Rect(self.topRightCorner[0],self.topRightCorner[1],self.boardWidth,self.boardWidth))
        for i in range(8):
            for j in range(8):
                if (9*i+j)%2==0:
                    color = "lightgreen"
                else:
                    color = "darkgreen"
                pygame.draw.rect(screen,color,pygame.Rect(self.topRightCorner[0]+self.edgeBorderWidth+self.tileBorderWidth+i*(self.tilesideLength+self.tileBorderWidth),self.topRightCorner[1]+self.edgeBorderWidth+self.tileBorderWidth+j*(self.tilesideLength+self.tileBorderWidth),self.tilesideLength,self.tilesideLength))
        for line in self.tiles:
            for t in line:
                if t is not None:
                    s = self.pieceLocationToPoint(t.getPosition())
                    pygame.draw.polygon(screen,oppositeColour(t.getColour()),shiftPoints(t.pointsToDraw(s),s))
                    pygame.draw.polygon(screen,t.getColour(),t.pointsToDraw(s))
        #Draw white taken pieces.
        for i in range(len(self.caughtPieces["white"])):
            (x,y)=(i%2,int(i/2))
            s = (self.topRightCorner[0]-2*60+x*60, self.topRightCorner[1]+(1+y)*60-self.pieceMargin)
            p = self.caughtPieces["white"][i]
            pygame.draw.polygon(screen,oppositeColour(p.getColour()),shiftPoints(p.pointsToDraw(s),s))
            pygame.draw.polygon(screen,p.getColour(),p.pointsToDraw(s))
        #Draw black taken pieces.
        for i in range(len(self.caughtPieces["black"])):
            (x,y)=(i%2,int(i/2))
            s = (881-2*60+x*60, self.topRightCorner[1]+(1+y)*60-self.pieceMargin)
            p = self.caughtPieces["black"][i]
            pygame.draw.polygon(screen,oppositeColour(p.getColour()),shiftPoints(p.pointsToDraw(s),s))
            pygame.draw.polygon(screen,p.getColour(),p.pointsToDraw(s))
        if self.gameSituation != gameSituation.inGame:
            self.drawMenu(screen)
        
    def drawMenu(self,screen):
        font = pygame.font.Font('freesansbold.ttf', 32)
        if self.menuChoice["AIButtons"]==True:
            uppermessage = font.render('Chess game', True, (0,0,0))
            lowermessage = font.render('Pick opponent level', True, (0,0,0))
        elif self.gameSituation==gameSituation.start:
            uppermessage = font.render('Chess game', True, (0,0,0))
            lowermessage = font.render('Pick sides', True, (0,0,0))            
        elif self.gameSituation==gameSituation.whiteWon:
            uppermessage = font.render('Checkmate', True, (0,0,0))
            lowermessage = font.render('White won', True, (0,0,0))
        elif self.gameSituation==gameSituation.blackWon:
            uppermessage = font.render('Checkmate', True, (0,0,0))
            lowermessage = font.render('Black won', True, (0,0,0))
        elif self.gameSituation==gameSituation.staleMate:
            uppermessage = font.render('Stalemate', True, (0,0,0))
            lowermessage = font.render('No-one won', True, (0,0,0))
        uppertextRect = uppermessage.get_rect()
        lowertextRect = lowermessage.get_rect()
        uppertextRect.center = (self.topRightCorner[0]+0.5*self.boardWidth,self.topRightCorner[1]+0.4*self.boardWidth)
        lowertextRect.center = (self.topRightCorner[0]+0.5*self.boardWidth,self.topRightCorner[1]+0.5*self.boardWidth)

        pygame.draw.rect(screen,"black",pygame.Rect(self.topRightCorner[0]+0.04*self.boardWidth,self.topRightCorner[1]+0.29*self.boardWidth,0.92*self.boardWidth,0.42*self.boardWidth))
        pygame.draw.rect(screen,"white",pygame.Rect(self.topRightCorner[0]+0.05*self.boardWidth,self.topRightCorner[1]+0.3*self.boardWidth,0.9*self.boardWidth,0.4*self.boardWidth))
        screen.blit(uppermessage,uppertextRect)
        screen.blit(lowermessage,lowertextRect)
        buttonFont = pygame.font.Font('freesansbold.ttf', 20)
        if self.menuChoice["WhiteReplay"]==True:
            pygame.draw.rect(screen,"black",pygame.Rect(438.5-5-3.4*63,348.5,3.4*63,63),border_radius=5)
            pygame.draw.rect(screen,"white",pygame.Rect(438.5-5-3.4*63+3,348.5+3,3.4*63-6,63-6),border_radius=5)
            if self.gameSituation==gameSituation.start:
                blackMessage = buttonFont.render('Play as white', True, (0,0,0))
            else:
                blackMessage = buttonFont.render('Replay as white', True, (0,0,0))
            blackMessageRect = blackMessage.get_rect()
            blackMessageRect.center = (438.5-5-1/2*3.4*63,348.5+63/2)
            screen.blit(blackMessage,blackMessageRect)
        if self.menuChoice["BlackReplay"]==True:
            pygame.draw.rect(screen,"black",pygame.Rect(438.5+5,348.5,3.4*63,63),border_radius=5)
            if self.gameSituation==gameSituation.start:
                whiteMessage = buttonFont.render('Play as black', True, (255,255,255))
            else:
                whiteMessage = buttonFont.render('Replay as black', True, (255,255,255))
            whiteMessageRect = whiteMessage.get_rect()
            whiteMessageRect.center = (438.5+5+1/2*3.4*63,348.5+63/2)
            screen.blit(whiteMessage,whiteMessageRect)
        if self.menuChoice["AIButtons"]==True:
            pygame.draw.rect(screen,"darkblue",pygame.Rect(216.25,348.5,103.325,63),border_radius=5)
            easyMessage = buttonFont.render('Easy', True, (255,255,255))
            easyMessageRect = easyMessage.get_rect()
            easyMessageRect.center = (216.25+103.325/2,348.5+63/2)
            screen.blit(easyMessage,easyMessageRect)
            pygame.draw.rect(screen,"lightblue",pygame.Rect(329.975,348.5,103.325,63),border_radius=5)
            mediumMessage = buttonFont.render('Medium', True, (255,255,255))
            mediumMessageRect = mediumMessage.get_rect()
            mediumMessageRect.center = (329.975+103.325/2,348.5+63/2)
            screen.blit(mediumMessage,mediumMessageRect)
            pygame.draw.rect(screen,"darkblue",pygame.Rect(443.7,348.5,103.325,63),border_radius=5)
            hardMessage = buttonFont.render('Hard', True, (255,255,255))
            hardMessageRect = hardMessage.get_rect()
            hardMessageRect.center = (443.7+103.325/2,348.5+63/2)
            screen.blit(hardMessage,hardMessageRect)
            pygame.draw.rect(screen,"lightblue",pygame.Rect(557.425,348.5,103.325,63),border_radius=5)
            shuffleMessage = buttonFont.render('Shuffle', True, (255,255,255))
            shuffleMessageRect = shuffleMessage.get_rect()
            shuffleMessageRect.center = (557.425+103.325/2,348.5+63/2)
            screen.blit(shuffleMessage,shuffleMessageRect)

    def pieceLocationToPoint(self,pieceLocation) -> tuple:
        #Returns the bottom centre point of the piece.
        if self.gameMode==gameMode.playAsWhite:
            return (self.topRightCorner[0]+self.edgeBorderWidth+(1/2+pieceLocation[0])*self.tileBorderWidth+(1/2+pieceLocation[0])*self.tilesideLength, self.topRightCorner[1]+self.edgeBorderWidth+(1+pieceLocation[1])*(self.tileBorderWidth+self.tilesideLength)-self.pieceMargin)
        elif self.gameMode==gameMode.playAsBlack:
            pieceLocation = (7-pieceLocation[0],7-pieceLocation[1])
            return (self.topRightCorner[0]+self.edgeBorderWidth+(1/2+pieceLocation[0])*self.tileBorderWidth+(1/2+pieceLocation[0])*self.tilesideLength, self.topRightCorner[1]+self.edgeBorderWidth+(1+pieceLocation[1])*(self.tileBorderWidth+self.tilesideLength)-self.pieceMargin)
        else:
            raise ValueError
            
    def pointToPieceLocation(self,point) -> tuple:
        #Takes in any position within the tile, gives out the chess position (7x7)
        if point[0]>=self.topRightCorner[0]+self.edgeBorderWidth and point[0]<=self.topRightCorner[0]+self.edgeBorderWidth+8*(self.tileBorderWidth+self.tilesideLength) and point[1]>=self.topRightCorner[1]+self.edgeBorderWidth and point[1]<=self.topRightCorner[1]+self.edgeBorderWidth+8*(self.tileBorderWidth+self.tilesideLength):
            if self.gameMode==gameMode.playAsWhite:
                return (int((point[0] - self.topRightCorner[0] - self.edgeBorderWidth)/(self.tileBorderWidth+self.tilesideLength)), int((point[1] - self.topRightCorner[1] - self.edgeBorderWidth)/(self.tileBorderWidth+self.tilesideLength)))
            elif self.gameMode==gameMode.playAsBlack:
                return (7-int((point[0] - self.topRightCorner[0] - self.edgeBorderWidth)/(self.tileBorderWidth+self.tilesideLength)), 7-int((point[1] - self.topRightCorner[1] - self.edgeBorderWidth)/(self.tileBorderWidth+self.tilesideLength)))
            else:
                raise ValueError
        else:
            return None

    def pickUpPiece(self,mCoord) -> None:
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
    
    def chooseFromMenu(self,mCoord) -> None:
        if self.menuChoice["WhiteReplay"]==True:
            if mCoord[0]>438.5-5-3.4*63 and mCoord[0]<438.5-5 and mCoord[1]>348.5 and mCoord[1]<348.5+63:
                self.menuChoice["BlackReplay"]=False #Remove buttons.
                self.menuChoice["WhiteReplay"]=False
                self.gameMode = gameMode.playAsWhite
                self.menuChoice["AIButtons"]=True
                return
        if self.menuChoice["BlackReplay"]==True:
            if mCoord[0]>438.5+5 and mCoord[0]<438.5+5+3.4*63 and mCoord[1]>348.5 and mCoord[1]<348.5+63:
                self.menuChoice["BlackReplay"]=False #Remove buttons.
                self.menuChoice["WhiteReplay"]=False
                self.gameMode = gameMode.playAsBlack
                self.menuChoice["AIButtons"]=True
                return
        if self.menuChoice["AIButtons"]==True:
            if mCoord[0]>216.25 and mCoord[0]<216.25+103.325 and mCoord[1]>348.5 and mCoord[1]<348.5+63:
                self.menuChoice["AIButtons"]=False
                self.AIType = AITypes.easyAI
                self.reset()
            elif mCoord[0]>329.975 and mCoord[0]<329.975+103.325 and mCoord[1]>348.5 and mCoord[1]<348.5+63:
                self.menuChoice["AIButtons"]=False
                self.AIType = AITypes.mediumAI
                self.reset()
            elif mCoord[0]>443.7 and mCoord[0]<443.7+103.325 and mCoord[1]>348.5 and mCoord[1]<348.5+63:
                self.menuChoice["AIButtons"]=False
                self.AIType = AITypes.hardAI
                self.reset()
            elif mCoord[0]>557.425 and mCoord[0]<557.425+103.325 and mCoord[1]>348.5 and mCoord[1]<348.5+63:
                self.menuChoice["AIButtons"]=False
                self.AIType = AITypes.dementedAI
                self.reset()