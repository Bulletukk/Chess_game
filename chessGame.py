from supportFunctions import *
import random

random.seed()

initialTotalPieceValue = 8*chessPieceValues[pawn] + 2*(chessPieceValues[rook]+chessPieceValues[knight]+chessPieceValues[bishop])+chessPieceValues[queen]
minMaxSearchLimit = 2

class chessGame:
    def __init__(self) -> None:
        self.edgeBorderWidth = 5
        self.tileBorderWidth = 3
        self.tilesideLength = 60
        self.pieceMargin = self.tilesideLength/8 #How far up in the tile the bottom of the chess piece should be.
        self.boardWidth = 8*self.tilesideLength + 9*self.tileBorderWidth + 2*self.edgeBorderWidth
        self.topRightCorner = (180,60)
        self.gameMode = gameMode.playAsWhite
        self.tiles = None
        self.turn = turn.white
        self.pieces = {"wp1": pawn("white"), "wp2": pawn("white"), "wp3": pawn("white"), "wp4": pawn("white"), "wp5": pawn("white"), "wp6": pawn("white"), "wp7": pawn("white"), "wp8": pawn("white"),
            "wr1": rook("white"), "wr2": rook("white"), "wk1": knight("white"), "wk2": knight("white"), "wb1": bishop("white"), "wb2": bishop("white"), "wq": queen("white"), "wking": king("white"),
            "bp1": pawn("black"), "bp2": pawn("black"), "bp3": pawn("black"), "bp4": pawn("black"), "bp5": pawn("black"), "bp6": pawn("black"), "bp7": pawn("black"), "bp8": pawn("black"),
            "br1": rook("black"), "br2": rook("black"), "bk1": knight("black"), "bk2": knight("black"), "bb1": bishop("black"), "bb2": bishop("black"), "bq": queen("black"), "bking": king("black")}
        self.caughtPieces = {"white":[],"black":[]}
        self.hoverPiece = None
        self.check = None
        self.gameSituation = gameSituation.start
        self.AIType = AITypes.randomAI
        self.menuChoice = {"BlackReplay":True,"WhiteReplay":True,"AIButtons":False} #More buttons will follow (choice of AI difficulty level).
        self.enPassant = (None,None) #Indicates pawn (chessPiece, [Position which it may be caught from]) which, for one move only, may be caught by pawn of opposing team.
        self.__layoutPieces()
        self.updateTiles()
    def __layoutPieces(self):
        self.pieces["wp1"].setPosition((0,6))
        self.pieces["wp2"].setPosition((1,6))
        self.pieces["wp3"].setPosition((2,6))
        self.pieces["wp4"].setPosition((3,6))
        self.pieces["wp5"].setPosition((4,6))
        self.pieces["wp6"].setPosition((5,6))
        self.pieces["wp7"].setPosition((6,6))
        self.pieces["wp8"].setPosition((7,6))
        self.pieces["wr1"].setPosition((0,7))
        self.pieces["wr2"].setPosition((7,7))
        self.pieces["wk1"].setPosition((1,7))
        self.pieces["wk2"].setPosition((6,7))
        self.pieces["wb1"].setPosition((2,7))
        self.pieces["wb2"].setPosition((5,7))
        self.pieces["wq"].setPosition((3,7))
        self.pieces["wking"].setPosition((4,7))

        self.pieces["bp1"].setPosition((0,1))
        self.pieces["bp2"].setPosition((1,1))
        self.pieces["bp3"].setPosition((2,1))
        self.pieces["bp4"].setPosition((3,1))
        self.pieces["bp5"].setPosition((4,1))
        self.pieces["bp6"].setPosition((5,1))
        self.pieces["bp7"].setPosition((6,1))
        self.pieces["bp8"].setPosition((7,1))
        self.pieces["br1"].setPosition((0,0))
        self.pieces["br2"].setPosition((7,0))
        self.pieces["bk1"].setPosition((1,0))
        self.pieces["bk2"].setPosition((6,0))
        self.pieces["bb1"].setPosition((2,0))
        self.pieces["bb2"].setPosition((5,0))
        self.pieces["bq"].setPosition((3,0))
        self.pieces["bking"].setPosition((4,0))
    def updateTiles(self):
        self.tiles = np.array([np.array([None for i in range(8)]) for j in range(8)])
        for piece in self.pieces:
            pos = self.pieces[piece].getPosition()
            if pos is not None:
                if self.tiles[pos[0],pos[1]] is not None:
                    raise ValueError("Two pieces have the same location")
                self.tiles[pos[0],pos[1]] = self.pieces[piece]

    def switchTurns(self) -> None:
        #If the en passantable pawn is of different colour than the current player (end-of-turn), after this turn it is no longer en passantable (ref. en passant rules). Hence it must be reset to None.
        if self.enPassant[0] is not None:
            if self.enPassant[0].getColour()!= turnToColour(self.turn):
                self.enPassant = (None,None)
        if self.turn==turn.white:
            self.turn=turn.black
        elif self.turn==turn.black:
            self.turn=turn.white

    def draw(self,screen) -> None:
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
            MehMessage = buttonFont.render('Meh', True, (255,255,255))
            MehMessageRect = MehMessage.get_rect()
            MehMessageRect.center = (216.25+103.325/2,348.5+63/2)
            screen.blit(MehMessage,MehMessageRect)
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
                self.AIType = AITypes.randomAI
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

    def placePiece(self,mCoord) -> None:
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
                    doAIMove(self) #This function also detects stalemate. Commenting out disables all AI (And stalemate, unfortunately, but deal with it).
            else:
                #Put piece back.
                self.hoverPiece = None
                self.updateTiles()
        elif location==None:
            self.hoverPiece = None
            self.updateTiles()
        elif self.hoverPiece!=None:
            raise ValueError
    
    def getMoveTypeInt(self,p: chessPiece, move: tuple) -> int:
        for potMove in p.getMoves():
            if potMove[0]==move[0] and potMove[1]==move[1]:
                return potMove[2]
        return 0

    def isLegalMove(self,p: chessPiece, location: tuple, checkCheckMate: bool=False, AICall: bool=False) -> bool:
        #Only checks for castling and en passant if this is an ordinary call of the legalmove function (not discovering checkmate), which means that checkCheckMate is set to False.
        #In the case of castling, moves the rook. Certain functionalities are also skipped if this is a call for finding an AI move.
        move = (location[0]-p.getPosition()[0],location[1]-p.getPosition()[1])
        n = self.getMoveTypeInt(p,move)
        if n==0:
            return False
        elif self.getTile(location)!=None:
            if self.getTile(location).getColour()==p.getColour():
                #Space occupied by piece of own colour, illegal move.
                return False
        potentialBoard = self.createPotentialBoard((p,p.getPosition(),location))
        if self.isKingThreatened(potentialBoard,p.getColour()):
            return False
        elif n==1:
            if self.getTile(location)==None:
                return True
            elif self.getTile(location).getColour()!=p.getColour():
                return True
        elif n==2:
            if self.getTile(location)==None:
                return True
        elif n==3:
            if self.enPassant[0]!=None:
                if location==self.enPassant[1] and p.getColour()!=self.enPassant[0].getColour():
                    enPassantPotentialBoard = self.createPotentialBoard((p,p.getPosition(),location),enPassantedPiece=self.enPassant[0])
                    if not self.isKingThreatened(enPassantPotentialBoard,p.getColour()):
                        #Valid en passant move. En passant will be performed (if not a checkcheckmate or an AI function call)
                        if not (checkCheckMate or AICall):
                            self.catchPiece(self.enPassant[0])
                        return True
            if self.getTile(location)==None:
                return False            
            elif self.getTile(location).getColour()!=p.getColour():
                return True
        elif n==4:
            if p.hasMoved==False and self.getTile(location)==None and self.getTile((int(location[0]-1/2*move[0]),int(location[1]-1/2*move[1])))==None:
                if not (checkCheckMate or AICall):
                    #Setting current piece as en passant piece.
                    self.enPassant = (p,(int(location[0]-1/2*move[0]),int(location[1]-1/2*move[1])))
                return True
        elif n==5:
            if isFreePath(self.tiles,p.getPosition(), location):
                if self.getTile(location)==None:
                    return True
                elif self.getTile(location).getColour()!=p.getColour():
                    return True
        elif n==6:
            if self.getTile(location) == None:
                return True
            elif self.getTile(location).getColour()!=p.getColour():
                return True
        elif not checkCheckMate and not self.check:
            #Checking for castling below here and moving the relevant rook if necessary:
            castlingStatus = (False,None)
            if n==7:
                if p.getColour()=="white":
                    if self.isCastlingLegal(self.pieces["wr1"]):
                        castlingStatus = (True,(self.pieces["wr1"],(3,7)))
                elif p.getColour()=="black":
                    if self.isCastlingLegal(self.pieces["br1"]):
                        castlingStatus = (True,(self.pieces["br1"],(3,0)))
            elif n==71:
                if p.getColour()=="white":
                    if self.isCastlingLegal(self.pieces["wr2"]):
                        castlingStatus = (True,(self.pieces["wr2"],(5,7)))
                elif p.getColour()=="black":
                    if self.isCastlingLegal(self.pieces["br2"]):
                        castlingStatus = (True,(self.pieces["br2"],(5,0)))
            if castlingStatus[0]==True:
                if not AICall:
                    castlingStatus[1][0].hasMoved = True
                    castlingStatus[1][0].setPosition(castlingStatus[1][1])
            return castlingStatus[0]
        return False
    
    def getTile(self,location: tuple):
        return self.tiles[location[0]][location[1]]

    def checkCheckSituation(self):
        self.check = None
        attackedPlayer = oppositeColour(turnToColour(self.turn))
        if self.isKingThreatened(self.tiles,attackedPlayer):
            self.check = colourToTurn(attackedPlayer)
            if self.discoverCheckMate(attackedPlayer):
                if attackedPlayer=="black":
                    self.gameSituation = gameSituation.whiteWon
                elif attackedPlayer=="white":
                    self.gameSituation = gameSituation.blackWon
                else:
                    raise ValueError
                self.menuChoice["BlackReplay"] = True
                self.menuChoice["WhiteReplay"] = True

    def staleMate(self):
        self.gameSituation = gameSituation.staleMate
        self.menuChoice["BlackReplay"] = True
        self.menuChoice["WhiteReplay"] = True
    
    def isKingThreatened(self,potentialBoard:np.array,kingColour:str) -> bool:
        #Check that none of the pieces on the board may catch the king:
        king = self.getKing(kingColour)
        kingPosition = findPosition(potentialBoard,king)
        if kingPosition == None:
            raise ValueError
        for x in range(len(potentialBoard)):
            for y in range(len(potentialBoard)):
                if potentialBoard[x,y] is not None:
                    piece = potentialBoard[x,y]
                    if piece.getColour() != kingColour:
                        move = (kingPosition[0]-x,kingPosition[1]-y)
                        n = self.getMoveTypeInt(piece,move)
                        if n in [1,3,6]:
                            return True
                        elif n==5:
                            if isFreePath(potentialBoard,(x,y),kingPosition):
                                return True
        return False
    
    def getKing(self,colour:str) -> chessPiece:
        if colour=="white":
            return self.pieces["wking"]
        else:
            return self.pieces["bking"]
        
    def createPotentialBoard(self,move:tuple,enPassantedPiece:chessPiece=None) -> np.array:
        p, fromPosition, toPosition = move
        potentialBoard = self.tiles.copy()
        if potentialBoard[fromPosition[0],fromPosition[1]]!=p and self.hoverPiece is None:
            raise ValueError
        potentialBoard[fromPosition[0],fromPosition[1]] = None
        potentialBoard[toPosition[0],toPosition[1]] = p
        if enPassantedPiece is not None:
            potentialBoard[enPassantedPiece.getPosition()[0],enPassantedPiece.getPosition()[1]] = None
        return potentialBoard
    
    def discoverCheckMate(self,attackedPlayer:str) -> bool:
        for index in self.pieces:
            piece = self.pieces[index]
            if piece.getPosition() is not None and piece.getColour()==attackedPlayer:
                for move in piece.getMoves():
                    newPos = (piece.getPosition()[0]+move[0],piece.getPosition()[1]+move[1])
                    if isLegalBoardCoordinate(newPos):
                        if self.isLegalMove(piece,newPos,checkCheckMate=True):
                            return False
        return True
    
    def isCastlingLegal(self,rookP:chessPiece) -> bool:
        castlingPlayer = rookP.getColour()
        if rookP.getColour()!=castlingPlayer:
            raise ValueError
        kingP = self.getKing(castlingPlayer)
        if not rookP.hasMoved and not kingP.hasMoved:
            kingPos = kingP.getPosition()
            posDiffX = rookP.getPosition()[0]-kingPos[0]
            dir = findDirection([posDiffX,0])
            freepath = True
            for i in range(1,abs(posDiffX)):
                if self.tiles[kingPos[0]+i*dir[0],kingPos[1]] is not None:
                    freepath = False
            if freepath:
                return True
        return False
    
    def convertPawnIfReached(self,p:chessPiece) -> None:
        hasReachedOtherEnd = False
        if p.getColour()=="white":
            if p.getPosition()[1]==0:
                hasReachedOtherEnd=True
        elif p.getColour()=="black":
            if p.getPosition()[1]==7:
                hasReachedOtherEnd=True
        if hasReachedOtherEnd:
            pawnIndex = None
            for index in self.pieces:
                if self.pieces[index]==p:
                    pawnIndex = index
            if pawnIndex==None:
                raise ValueError
            self.pieces[pawnIndex]=queen(p.getColour())
            self.pieces[pawnIndex].setPosition(p.getPosition())
            self.pieces[pawnIndex].hasMoved = True
            #NOTE:
            #Hoverpiece now points to the old pawn, but this doesn't matter as we're at the end of the turn.

    def catchPiece(self,p:chessPiece) -> None:
        p.hasMoved = True
        p.setPosition(None)
        self.caughtPieces[p.getColour()].append(p)

    def getPossibleMoves(self) -> tuple[list[chessPiece],list[tuple[chessPiece,tuple[int,int]]]]:
        moves = list()
        originalPositionPawns = list()
        for key in self.pieces:
            p = self.pieces[key]
            if type(p)==pawn and p.hasMoved==False:
                originalPositionPawns.append(p)
            if p.getColour()==turnToColour(self.turn) and p.getPosition() is not None:
                #Piece is of correct colour and not taken.
                for move in p.getMoves():
                    newLocation = (p.getPosition()[0]+move[0],p.getPosition()[1]+move[1])
                    if isLegalBoardCoordinate(newLocation):
                        if self.isLegalMove(p,newLocation,AICall=True):
                            moves.append((p,p.getPosition(),newLocation))
        return moves, originalPositionPawns

    def reset(self) -> None:
        self.pieces = {"wp1": pawn("white"), "wp2": pawn("white"), "wp3": pawn("white"), "wp4": pawn("white"), "wp5": pawn("white"), "wp6": pawn("white"), "wp7": pawn("white"), "wp8": pawn("white"),
            "wr1": rook("white"), "wr2": rook("white"), "wk1": knight("white"), "wk2": knight("white"), "wb1": bishop("white"), "wb2": bishop("white"), "wq": queen("white"), "wking": king("white"),
            "bp1": pawn("black"), "bp2": pawn("black"), "bp3": pawn("black"), "bp4": pawn("black"), "bp5": pawn("black"), "bp6": pawn("black"), "bp7": pawn("black"), "bp8": pawn("black"),
            "br1": rook("black"), "br2": rook("black"), "bk1": knight("black"), "bk2": knight("black"), "bb1": bishop("black"), "bb2": bishop("black"), "bq": queen("black"), "bking": king("black")}
        self.caughtPieces = {"white":[],"black":[]}
        self.hoverPiece = None
        self.check = None
        self.gameSituation = gameSituation.inGame
        self.turn = turn.white
        self.enPassant = (None,None)
        self.__layoutPieces()
        self.updateTiles()
        if self.gameMode == gameMode.playAsBlack:
            #Start with an AI move.
            doAIMove(self)

#Implementation of chess AI below here.
def doAIMove(c:chessGame) -> None:
    moves, originalPositionPawns = c.getPossibleMoves()
    if len(moves)==0:
        c.staleMate()
        return
    if c.AIType==AITypes.randomAI:
        p,oldLocation,newLocation = RandomMove(moves)
    elif c.AIType==AITypes.mediumAI:
        p,oldLocation,newLocation = BasicEvaluationMove(c,moves)
    elif c.AIType==AITypes.hardAI:
        p,oldLocation,newLocation = MinMaxSearchMove(c,moves,originalPositionPawns) #Change this!!!
    elif c.AIType==AITypes.dementedAI:
        p,oldLocation,newLocation = DementedAIMove(moves)
    c.isLegalMove(p,newLocation) #Perform normal call of IsLegalMove in order to do castling and en passant if necessary.
    if c.getTile(newLocation) is not None:
        c.catchPiece(c.getTile(newLocation))
    p.hasMoved = True
    p.setPosition(newLocation)
    if type(p)==pawn:
        c.convertPawnIfReached(p)
    c.updateTiles()
    c.checkCheckSituation()
    if not (c.gameSituation==gameSituation.blackWon or c.gameSituation==gameSituation.whiteWon):
        c.switchTurns()
        if len(c.getPossibleMoves()[0])==0:
            c.staleMate()

def RandomMove(moves: list[tuple[chessPiece,tuple[int,int]]]):
    #Picks a random move.
    return moves[random.randint(0,len(moves)-1)]

def BasicEvaluationMove(c:chessGame, moves: list[tuple[chessPiece,tuple[int,int]]]):
    #Picks the highest evaluated possible move.
    random.shuffle(moves)
    highestEval = 0
    bestMove = None
    for move in moves:
        currentEval = BoardEval(c.createPotentialBoard(move),c.turn)
        if currentEval > highestEval:
            highestEval = currentEval
            bestMove = move
    return bestMove
    
def MinMaxSearchMove(c:chessGame, moves:list[tuple[chessPiece,tuple[int,int]]],originalPositionPawns:list[chessPiece]):
    #Performs minmax search down to the globally defined search limit.
    maxVal, bestMove = float('-inf'), None
    random.shuffle(moves)
    for move in moves:
        potentialBoard,pawns = createBoard(c.tiles,move,originalPositionPawns)
        newVal = minMaxValue(potentialBoard,pawns,oppositeTurn(c.turn),1)
        if newVal>maxVal:
            maxVal = newVal
            bestMove = move
    #Way to improve this AI: reduce runtime by not using getPossibleMoves in doAIMove, and increase search depth.
    return bestMove

def DementedAIMove(c:chessGame, moves: list[tuple[chessPiece,tuple[int,int]]]):
    functionNo = random.randint(0,1)
    if functionNo==0:
        return RandomMove(moves)
    else:
        return BasicEvaluationMove(c,moves)

def BoardEval(potentialBoard: np.array,currentTurn:turn) -> int:
    #Note to self: Consider having this function also find potential moves.
    standingPiecesWeighting = 0 #Own remaining pieces. #Set to zero for the time being, as we only do one (own) turn.
    takenPiecesWeighting = 40 #Opponent taken pieces.
    ownThreatenedPiecesWeighting = 30
    opponentThreatenedPiecesWeighting = 10
    ownCoveredPiecesWeighting = 20 #Own covered pieces: when their position can be reached by another piece of same colour, so they are "protected".

    standingPiecesScore = 0
    takenPiecesScore = initialTotalPieceValue
    ownThreatenedPiecesScore = 0 #Will be <=0.
    opponentThreatenedPiecesScore = 0
    ownCoveredPiecesScore = 0
    ownCoveredPieces = set()
    ownKingTaken = True
    opponentKingTaken = True
    for x in range(len(potentialBoard)):
        for y in range(len(potentialBoard)):
            piece = potentialBoard[x,y]
            if piece is not None:
                if piece.getColour()==turnToColour(currentTurn):
                    if type(piece) is king:
                        ownKingTaken = False
                    else:
                        standingPiecesScore += chessPieceValues[type(piece)]
                else:
                    if type(piece) is king:
                        opponentKingTaken = False
                    else:
                        takenPiecesScore -= chessPieceValues[type(piece)]
                for xmove,ymove,moveInt in piece.getMoves():
                    mayCatch = False
                    newPos = (x+xmove,y+ymove)
                    if isLegalBoardCoordinate(newPos):
                        if moveInt in [1,3,6]:
                            mayCatch = True
                        elif moveInt==5:
                            if isFreePath(potentialBoard,(x,y),newPos):
                                mayCatch = True
                        if mayCatch:
                            threatenedPiece = potentialBoard[newPos[0],newPos[1]]
                            if threatenedPiece is not None:
                                if piece.getColour()==turnToColour(currentTurn):
                                    if threatenedPiece.getColour()==piece.getColour(): #Own piece protects own piece.
                                        ownCoveredPieces.add(threatenedPiece)
                                    else: #Own piece may catch opponent piece.
                                        opponentThreatenedPiecesScore += chessPieceValues[type(threatenedPiece)]
                                else:
                                    if threatenedPiece.getColour()!=piece.getColour(): #Opponent piece may catch own piece.
                                        ownThreatenedPiecesScore -= chessPieceValues[type(threatenedPiece)]
    for piece in ownCoveredPieces:
        if type(piece) is not king:
            ownCoveredPiecesScore += chessPieceValues[type(piece)]
    
    if ownKingTaken:
        return -100000000
    elif opponentKingTaken:
        return 100000000
    else:
        return standingPiecesWeighting*standingPiecesScore+takenPiecesWeighting*takenPiecesScore+ownThreatenedPiecesWeighting*ownThreatenedPiecesScore+opponentThreatenedPiecesWeighting*opponentThreatenedPiecesScore+ownCoveredPiecesWeighting*ownCoveredPiecesScore
    
def getLegalActions(potentialBoard,originalPositionPawns,turn) -> list[tuple[chessPiece,tuple[int,int]]]:
    #Returns legal moves on a potential board for a given player.
    #Note: Some inaccuracy is allowed, as check and checkmate will be picked up in the adversarial search. This function returns some illegal moves and there are some legal moves (like en passant and castling) that it fails to pick up.
    moves = list()
    for x in range(len(potentialBoard)):
        for y in range(len(potentialBoard)):
            if potentialBoard[x,y]!=None:
                piece = potentialBoard[x,y]
                if piece.getColour()==turnToColour(turn):
                    for xmove,ymove,moveInt in piece.getMoves():
                        oldPos = (x,y)
                        newPos = (x+xmove,y+ymove)
                        if isLegalBoardCoordinate(newPos):
                            if potentialBoard[x+xmove,y+ymove] is None:
                                if moveInt in [1,2,6]:
                                    moves.append((piece,oldPos,newPos))
                                elif moveInt==4:
                                    if piece in originalPositionPawns:
                                        moves.append((piece,oldPos,newPos))
                                elif moveInt==5:
                                    if isFreePath(potentialBoard,(x,y),newPos):
                                        moves.append((piece,oldPos,newPos))
                            else:
                                if potentialBoard[x+xmove,y+ymove].getColour()==oppositeColour(turnToColour(turn)):
                                    if moveInt in [1,3,6]:
                                        moves.append((piece,oldPos,newPos))
                                    elif moveInt==5:
                                        if isFreePath(potentialBoard,(x,y),newPos):
                                            moves.append((piece,oldPos,newPos))
    return moves

def createBoard(board,move,originalPositionPawns):
    newBoard = board.copy()
    pawns = originalPositionPawns.copy()
    p, fromPosition, toPosition = move
    if newBoard[fromPosition[0],fromPosition[1]]!=p:
        raise ValueError
    if p in pawns:
        pawns.remove(p)
    newBoard[fromPosition[0],fromPosition[1]] = None
    newBoard[toPosition[0],toPosition[1]] = p
    return newBoard, pawns

def minMaxValue(potentialBoard:np.array,originalPositionPawns,turn:turn,depth:int):
    if depth == minMaxSearchLimit:
        return BoardEval(potentialBoard,turn)
    elif depth%2==1:
        #Find minimum value:
        moves = getLegalActions(potentialBoard,originalPositionPawns,turn)
        random.shuffle(moves)
        minVal = float('inf')
        for move in moves:
            board, pawns = createBoard(potentialBoard,move,originalPositionPawns)
            newVal = minMaxValue(board,pawns,oppositeTurn(turn),depth+1)
            minVal = min(minVal,newVal)
        return minVal
    else:
        #Find maximum value:
        moves = getLegalActions(potentialBoard,originalPositionPawns,turn)
        random.shuffle(moves)
        maxVal = float('-inf')
        for move in moves:
            board, pawns = createBoard(potentialBoard,move,originalPositionPawns)
            newVal = minMaxValue(board,pawns,oppositeTurn(turn),depth+1)
            maxVal = max(maxVal,newVal)
        return maxVal