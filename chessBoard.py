from chessPiece import *
from enum import Enum

class gameSituation(Enum):
    start = 1
    inGame = 2
    whiteWon = 3
    blackWon = 4
    staleMate = 5

class gameMode(Enum):
    playAsWhite = 1
    playAsBlack = 2

def oppositeTurn(turn):
    if turn==turn.white:
        return turn.black
    elif turn==turn.black:
        return turn.white

def findDirection(move: list) -> tuple:
    if move[0]!=0:
        if move[1]!=0:
            return (int(move[0]/abs(move[0])),int(move[1]/abs(move[1])))
        else:
            return (int(move[0]/abs(move[0])),0)
    else:
        if move[1]!=0:
            return (0,int(move[1]/abs(move[1])))
        else:
            return (0,0)
        
def isValidBoardCoordinate(location: tuple):
    if location[0] >= 0 and location[0] < 8 and location[1] >= 0 and location[1] < 8:
        return True
    else:
        return False

class chessBoard:
    #stuff here.
    def __init__(self,mode:gameMode,turn:turn):
        self._mode = mode
        self._turn = turn
        self._tiles = [[None for i in range(8)] for j in range(8)]
        self._pieces = {"wp1": pawn(turn.white,(0,6)), "wp2": pawn(turn.white,(1,6)), "wp3": pawn(turn.white,(2,6)), "wp4": pawn(turn.white,(3,6)), "wp5": pawn(turn.white,(4,6)), "wp6": pawn(turn.white,(5,6)), "wp7": pawn(turn.white,(6,6)), "wp8": pawn(turn.white,(7,6)),
            "wr1": rook(turn.white,(0,7)), "wr2": rook(turn.white,(7,7)), "wk1": knight(turn.white,(1,7)), "wk2": knight(turn.white,(6,7)), "wb1": bishop(turn.white,(2,7)), "wb2": bishop(turn.white,(5,7)), "wq": queen(turn.white,(3,7)), "wking": king(turn.white,(4,7)),
            "bp1": pawn(turn.black,(0,1)), "bp2": pawn(turn.black,(1,1)), "bp3": pawn(turn.black,(2,1)), "bp4": pawn(turn.black,(3,1)), "bp5": pawn(turn.black,(4,1)), "bp6": pawn(turn.black,(5,1)), "bp7": pawn(turn.black,(6,1)), "bp8": pawn(turn.black,(7,1)),
            "br1": rook(turn.black,(0,0)), "br2": rook(turn.black,(7,0)), "bk1": knight(turn.black,(1,0)), "bk2": knight(turn.black,(6,0)), "bb1": bishop(turn.black,(2,0)), "bb2": bishop(turn.black,(5,0)), "bq": queen(turn.black,(3,0)), "bking": king(turn.black,(4,0))}
        self._caughtPieces = {turn.white:[],turn.black:[]}
        self._check = None
        self.enPassant = (None,None) #Indicates pawn (chessPiece, [Position which it may be caught from]) which, for one move only, may be caught by pawn of opposing team.

    def createPotentialBoard(self,move:tuple,enPassantedPiece:chessPiece=None):
        #Replace with generate successor function.
        p, fromPosition, toPosition = move
        potentialBoard = self.tiles.copy()
        if potentialBoard[fromPosition[0],fromPosition[1]]!=p and self.hoverPiece is None:
            raise ValueError
        potentialBoard[fromPosition[0],fromPosition[1]] = None
        potentialBoard[toPosition[0],toPosition[1]] = p
        if enPassantedPiece is not None:
            potentialBoard[enPassantedPiece.getPosition()[0],enPassantedPiece.getPosition()[1]] = None
        return potentialBoard
    
    def getPossibleMoves(self) -> tuple[list[chessPiece],list[tuple[chessPiece,tuple[int,int]]]]:
        #TODO: Merge into getLegalMoves functions.
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
                    if isValidBoardCoordinate(newLocation):
                        if self.isLegalMove(p,newLocation,AICall=True):
                            moves.append((p,p.getPosition(),newLocation))
        return moves, originalPositionPawns

    def getLegalMoves(self,mustCheckCheckMate: bool) -> bool:
        #Previously called isLegalMove.
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

    def discoverCheckMate(self,attackedPlayer:str) -> bool:
        for index in self.pieces:
            piece = self.pieces[index]
            if piece.getPosition() is not None and piece.getColour()==attackedPlayer:
                for move in piece.getMoves():
                    newPos = (piece.getPosition()[0]+move[0],piece.getPosition()[1]+move[1])
                    if isValidBoardCoordinate(newPos):
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
        #TODO: Simplify. Just check all end tiles to see if they contain pawns.
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
    
    def getKing(self,colour:str):
        if colour=="white":
            return self.pieces["wking"]
        else:
            return self.pieces["bking"]

    def isFreePath(self,location1:tuple,location2:tuple):
        move = (location2[0]-location1[0],location2[1]-location1[1])
        dir = findDirection(move)
        for i in range(1,max(abs(move[0]),abs(move[1]))):
            if self._tiles[int(location1[0]+i*dir[0]),int(location1[1]+i*dir[1])] != None:
                return False
        return True

    def switchTurns(self):
        #If the en passantable pawn is of different colour than the current player (end-of-turn), after this turn it is no longer en passantable (ref. en passant rules). Hence it must be reset to None.
        if self.enPassant[0] is not None:
            if self.enPassant[0].getColour()!= self.turn:
                self.enPassant = (None,None)
        if self.turn==turn.white:
            self.turn=turn.black
        elif self.turn==turn.black:
            self.turn=turn.white