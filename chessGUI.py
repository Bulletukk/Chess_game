import chessPiece, chessBoard, chessAI
import pygame
from enum import Enum

class menuSituation(Enum):
    pickSide = 1
    pickOpponentDifficulty = 2

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
    
def oppositeColour(colour:str):
    if colour=="white":
        return "black"
    else:
        return "white"

class chessGUI:
    def __init__(self):
        self._edgeBorderWidth = 5
        self._tileBorderWidth = 3
        self._tilesideLength = 60
        self._pieceMargin = self._tilesideLength/8 #How far up in the tile the bottom of the chess piece should be.
        self._boardWidth = 8*self._tilesideLength + 9*self._tileBorderWidth + 2*self._edgeBorderWidth
        self._topRightCorner = (180,60)
        self._screen = pygame.display.set_mode((881,637))
        self._menuChoice = menuSituation.pickSide
        self._hoverPiece = None
        self._hoverPieceOriginalLocation = None

    def getHoverPiece(self):
        return self._hoverPiece
    
    def getMenuChoice(self):
        return self._menuChoice

    def draw(self,board,gameSituation,caughtPieces,gameMode,mCoord):
        if gameSituation==None:
            raise ValueError
        self._screen.fill("grey")
        #Set background colour. Dark red if we're in check.
        if board.getCheckSituation()==True:
            rectColor = "darkred"
        else:
            rectColor = "black"
        #Draw board
        pygame.draw.rect(self._screen,rectColor,pygame.Rect(self._topRightCorner[0],self._topRightCorner[1],self._boardWidth,self._boardWidth))
        for i in range(8):
            for j in range(8):
                if (9*i+j)%2==0:
                    color = "lightgreen"
                else:
                    color = "darkgreen"
                pygame.draw.rect(self._screen,color,pygame.Rect(self._topRightCorner[0]+self._edgeBorderWidth+self._tileBorderWidth+i*(self._tilesideLength+self._tileBorderWidth),self._topRightCorner[1]+self._edgeBorderWidth+self._tileBorderWidth+j*(self._tilesideLength+self._tileBorderWidth),self._tilesideLength,self._tilesideLength))
        for x in range(8):
            for y in range(8):
                t = board.getTiles()[x][y]
                if t is not None:
                    s = self.pieceLocationToPoint((x,y),gameMode)
                    pygame.draw.polygon(self._screen,oppositeColour(turnToColour(t.getColour())),shiftPoints(t.findPointsToDraw(s),s))
                    pygame.draw.polygon(self._screen,turnToColour(t.getColour()),t.findPointsToDraw(s))
        #Draw white taken pieces.
        for i in range(len(caughtPieces[chessPiece.turn.white])):
            (x,y)=(i%2,int(i/2))
            s = (self._topRightCorner[0]-2*60+x*60, self._topRightCorner[1]+(1+y)*60-self._pieceMargin)
            p = caughtPieces[chessPiece.turn.white][i]
            pygame.draw.polygon(self._screen,"black",shiftPoints(p.findPointsToDraw(s),s))
            pygame.draw.polygon(self._screen,"white",p.findPointsToDraw(s))
        #Draw black taken pieces.
        for i in range(len(caughtPieces[chessPiece.turn.black])):
            (x,y)=(i%2,int(i/2))
            s = (881-2*60+x*60, self._topRightCorner[1]+(1+y)*60-self._pieceMargin)
            p = caughtPieces[chessPiece.turn.black][i]
            pygame.draw.polygon(self._screen,"white",shiftPoints(p.findPointsToDraw(s),s))
            pygame.draw.polygon(self._screen,"black",p.findPointsToDraw(s))
        if gameSituation != chessBoard.gameSituation.inGame:
            self.drawMenu(gameSituation)
        if self._hoverPiece is not None:
            pygame.draw.polygon(self._screen,oppositeColour(turnToColour(self._hoverPiece.getColour())),shiftPoints(self._hoverPiece.findPointsToDraw((mCoord[0],mCoord[1]+18)),(mCoord[0],mCoord[1]+18)))
            pygame.draw.polygon(self._screen,turnToColour(self._hoverPiece.getColour()),self._hoverPiece.findPointsToDraw((mCoord[0],mCoord[1]+18)))

    def drawMenu(self,gameSituation):
        font = pygame.font.Font('freesansbold.ttf', 32)
        if self._menuChoice == menuSituation.pickOpponentDifficulty:
            uppermessage = font.render('Chess game', True, (0,0,0))
            lowermessage = font.render('Pick opponent level', True, (0,0,0))
        else:
            if gameSituation==chessBoard.gameSituation.start:
                uppermessage = font.render('Chess game', True, (0,0,0))
                lowermessage = font.render('Pick sides', True, (0,0,0))
            elif gameSituation==chessBoard.gameSituation.whiteWon:
                uppermessage = font.render('Checkmate', True, (0,0,0))
                lowermessage = font.render('White won', True, (0,0,0))
            elif gameSituation==chessBoard.gameSituation.blackWon:
                uppermessage = font.render('Checkmate', True, (0,0,0))
                lowermessage = font.render('Black won', True, (0,0,0))
            elif gameSituation==chessBoard.gameSituation.staleMate:
                uppermessage = font.render('Stalemate', True, (0,0,0))
                lowermessage = font.render('No-one won', True, (0,0,0))
            else:
                raise ValueError
        uppertextRect = uppermessage.get_rect()
        lowertextRect = lowermessage.get_rect()
        uppertextRect.center = (self._topRightCorner[0]+0.5*self._boardWidth,self._topRightCorner[1]+0.4*self._boardWidth)
        lowertextRect.center = (self._topRightCorner[0]+0.5*self._boardWidth,self._topRightCorner[1]+0.5*self._boardWidth)

        pygame.draw.rect(self._screen,"black",pygame.Rect(self._topRightCorner[0]+0.04*self._boardWidth,self._topRightCorner[1]+0.29*self._boardWidth,0.92*self._boardWidth,0.42*self._boardWidth))
        pygame.draw.rect(self._screen,"white",pygame.Rect(self._topRightCorner[0]+0.05*self._boardWidth,self._topRightCorner[1]+0.3*self._boardWidth,0.9*self._boardWidth,0.4*self._boardWidth))
        self._screen.blit(uppermessage,uppertextRect)
        self._screen.blit(lowermessage,lowertextRect)
        buttonFont = pygame.font.Font('freesansbold.ttf', 20)
        if self._menuChoice==menuSituation.pickSide:
            pygame.draw.rect(self._screen,"black",pygame.Rect(438.5-5-3.4*63,348.5,3.4*63,63),border_radius=5)
            pygame.draw.rect(self._screen,"white",pygame.Rect(438.5-5-3.4*63+3,348.5+3,3.4*63-6,63-6),border_radius=5)
            if gameSituation==chessBoard.gameSituation.start:
                blackMessage = buttonFont.render('Play as white', True, (0,0,0))
            else:
                blackMessage = buttonFont.render('Replay as white', True, (0,0,0))
            blackMessageRect = blackMessage.get_rect()
            blackMessageRect.center = (438.5-5-1/2*3.4*63,348.5+63/2)
            self._screen.blit(blackMessage,blackMessageRect)

            pygame.draw.rect(self._screen,"black",pygame.Rect(438.5+5,348.5,3.4*63,63),border_radius=5)
            if gameSituation==chessBoard.gameSituation.start:
                whiteMessage = buttonFont.render('Play as black', True, (255,255,255))
            else:
                whiteMessage = buttonFont.render('Replay as black', True, (255,255,255))
            whiteMessageRect = whiteMessage.get_rect()
            whiteMessageRect.center = (438.5+5+1/2*3.4*63,348.5+63/2)
            self._screen.blit(whiteMessage,whiteMessageRect)
        if self._menuChoice==menuSituation.pickOpponentDifficulty:
            pygame.draw.rect(self._screen,"darkblue",pygame.Rect(216.25,348.5,103.325,63),border_radius=5)
            easyMessage = buttonFont.render('Easy', True, (255,255,255))
            easyMessageRect = easyMessage.get_rect()
            easyMessageRect.center = (216.25+103.325/2,348.5+63/2)
            self._screen.blit(easyMessage,easyMessageRect)
            pygame.draw.rect(self._screen,"lightblue",pygame.Rect(329.975,348.5,103.325,63),border_radius=5)
            mediumMessage = buttonFont.render('Medium', True, (255,255,255))
            mediumMessageRect = mediumMessage.get_rect()
            mediumMessageRect.center = (329.975+103.325/2,348.5+63/2)
            self._screen.blit(mediumMessage,mediumMessageRect)
            pygame.draw.rect(self._screen,"darkblue",pygame.Rect(443.7,348.5,103.325,63),border_radius=5)
            hardMessage = buttonFont.render('Hard', True, (255,255,255))
            hardMessageRect = hardMessage.get_rect()
            hardMessageRect.center = (443.7+103.325/2,348.5+63/2)
            self._screen.blit(hardMessage,hardMessageRect)
            pygame.draw.rect(self._screen,"lightblue",pygame.Rect(557.425,348.5,103.325,63),border_radius=5)
            shuffleMessage = buttonFont.render('Shuffle', True, (255,255,255))
            shuffleMessageRect = shuffleMessage.get_rect()
            shuffleMessageRect.center = (557.425+103.325/2,348.5+63/2)
            self._screen.blit(shuffleMessage,shuffleMessageRect)

    def pieceLocationToPoint(self,pieceLocation,gameMode):
        #Returns the bottom centre point of the piece. Inverts location if gamemode is black.
        if gameMode==chessBoard.gameMode.playAsBlack:
            pieceLocation = (7-pieceLocation[0],7-pieceLocation[1])
        return (self._topRightCorner[0]+self._edgeBorderWidth+(1/2+pieceLocation[0])*self._tileBorderWidth+(1/2+pieceLocation[0])*self._tilesideLength, self._topRightCorner[1]+self._edgeBorderWidth+(1+pieceLocation[1])*(self._tileBorderWidth+self._tilesideLength)-self._pieceMargin)
            
    def pointToPieceLocation(self,point,gameMode):
        if gameMode==chessBoard.gameMode.playAsWhite:
            return (int((point[0] - self._topRightCorner[0] - self._edgeBorderWidth)/(self._tileBorderWidth+self._tilesideLength)), int((point[1] - self._topRightCorner[1] - self._edgeBorderWidth)/(self._tileBorderWidth+self._tilesideLength)))
        else:
            return (7-int((point[0] - self._topRightCorner[0] - self._edgeBorderWidth)/(self._tileBorderWidth+self._tilesideLength)), 7-int((point[1] - self._topRightCorner[1] - self._edgeBorderWidth)/(self._tileBorderWidth+self._tilesideLength)))
        
    def chooseFromMenu(self,mCoord):
        if self._menuChoice==menuSituation.pickSide:
            if mCoord[0]>438.5-5-3.4*63 and mCoord[0]<438.5-5 and mCoord[1]>348.5 and mCoord[1]<348.5+63:
                self._menuChoice = menuSituation.pickOpponentDifficulty
                return chessBoard.gameMode.playAsWhite
            elif mCoord[0]>438.5+5 and mCoord[0]<438.5+5+3.4*63 and mCoord[1]>348.5 and mCoord[1]<348.5+63:
                self._menuChoice = menuSituation.pickOpponentDifficulty
                return chessBoard.gameMode.playAsBlack
        elif self._menuChoice==menuSituation.pickOpponentDifficulty:
            AItype = None
            if mCoord[0]>216.25 and mCoord[0]<319.575 and mCoord[1]>348.5 and mCoord[1]<411.5:
                AItype = chessAI.AITypes.easyAI
            elif mCoord[0]>329.975 and mCoord[0]<433.3 and mCoord[1]>348.5 and mCoord[1]<411.5:
                AItype = chessAI.AITypes.mediumAI
            elif mCoord[0]>443.7 and mCoord[0]<547.025 and mCoord[1]>348.5 and mCoord[1]<411.5:
                AItype = chessAI.AITypes.hardAI
            elif mCoord[0]>557.425 and mCoord[0]<660.75 and mCoord[1]>348.5 and mCoord[1]<411.5:
                AItype = chessAI.AITypes.dementedAI
            if AItype!=None:
                self._menuChoice = menuSituation.pickSide
                return AItype
        return None

    def pickUpPiece(self,board:chessBoard.chessBoard,gameMode,mCoord):
        location = self.pointToPieceLocation(mCoord,gameMode)
        if location is not None:
            piece = board.getTiles()[location[0]][location[1]]
            #Check if the piece has the correct colour:
            if piece is not None:
                if piece.getColour()==board.getTurn():
                    board.hidePiece(location)
                    self._hoverPiece = piece
                    self._hoverPieceOriginalLocation = location

    def placePiece(self,board:chessBoard.chessBoard,gameMode,mCoord):
        #Initially puts piece back, then moves it if the board coordinate is valid.
        board.showPiece(self._hoverPiece,self._hoverPieceOriginalLocation)
        shouldDoAIMove = False
        location = self.pointToPieceLocation(mCoord,gameMode)
        situation = chessBoard.gameSituation.inGame
        addedCaughtPieces = list()
        if location != None:
            moves = None
            for possibleMoves in board.getLegalMoves(mustControlIfKingChecked=True):
                if (self._hoverPieceOriginalLocation,location) == possibleMoves[0]:
                    moves = possibleMoves
                    break
            if moves is not None:
                addedCaughtPieces, situation = board.makeMoves(moves,mustCheckCheckSituation=True)
                if situation==chessBoard.gameSituation.inGame:
                    shouldDoAIMove = True
        self._hoverPiece = None
        self._hoverPieceOriginalLocation = None
        return addedCaughtPieces, situation, shouldDoAIMove