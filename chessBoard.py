from chessPiece import *
from enum import Enum
import copy

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
    def __init__(self,mode:gameMode,turn:turn):
        self._mode = mode
        self._turn = turn
        self._tiles = [[None for i in range(8)] for j in range(8)]
        self._pieces = {"wp1": pawn(turn.white,(0,6)), "wp2": pawn(turn.white,(1,6)), "wp3": pawn(turn.white,(2,6)), "wp4": pawn(turn.white,(3,6)), "wp5": pawn(turn.white,(4,6)), "wp6": pawn(turn.white,(5,6)), "wp7": pawn(turn.white,(6,6)), "wp8": pawn(turn.white,(7,6)),
            "wr1": rook(turn.white,(0,7)), "wr2": rook(turn.white,(7,7)), "wk1": knight(turn.white,(1,7)), "wk2": knight(turn.white,(6,7)), "wb1": bishop(turn.white,(2,7)), "wb2": bishop(turn.white,(5,7)), "wq": queen(turn.white,(3,7)), "wking": king(turn.white,(4,7)),
            "bp1": pawn(turn.black,(0,1)), "bp2": pawn(turn.black,(1,1)), "bp3": pawn(turn.black,(2,1)), "bp4": pawn(turn.black,(3,1)), "bp5": pawn(turn.black,(4,1)), "bp6": pawn(turn.black,(5,1)), "bp7": pawn(turn.black,(6,1)), "bp8": pawn(turn.black,(7,1)),
            "br1": rook(turn.black,(0,0)), "br2": rook(turn.black,(7,0)), "bk1": knight(turn.black,(1,0)), "bk2": knight(turn.black,(6,0)), "bb1": bishop(turn.black,(2,0)), "bb2": bishop(turn.black,(5,0)), "bq": queen(turn.black,(3,0)), "bking": king(turn.black,(4,0))}
        self._check = False
        self._enPassant = None #Indicates pawn (chessPiece, [Position which it may be caught from]) which, for one move only, may be caught by pawn of opposing team.
        self.__setTiles()

    def __setTiles(self):
        for index in self._pieces:
            p = self._pieces[index]
            self._tiles[p.getPosition()[0]][p.getPosition()[1]] = p

    def getCheckSituation(self):
        return self._check
    
    def getTiles(self):
        return self._tiles
    
    def getGamemode(self):
        return self._mode
    
    def getTurn(self):
        return self._turn
    
    def hidePiece(self,location):
        self._tiles[location[0]][location[1]] = None

    def showPiece(self,piece):
        self._tiles[piece.getPosition()[0]][piece.getPosition()[1]] = piece

    def makeMoves(self,movesInTurn,mustCheckCheckSituation:bool):
        #Moves is a list of moves (each move being a tuple with from coordinate and to coordinate)
        #MovesInTurn is a list of moves to be done in this turn, normally just one move, but two when castling/en passant is being done.
        self._enPassant = None
        situation = gameSituation.inGame
        caughtPieces = list()
        for move in movesInTurn:
            fromPosition, toPosition = move
            if toPosition == None:
                p = self._tiles[fromPosition[0]][fromPosition[1]]
                self._tiles[fromPosition[0]][fromPosition[1]] = None
                p.setPosition(None)
                caughtPieces.append(p)
            else:
                if self._tiles[toPosition[0]][toPosition[1]]!=None and mustCheckCheckSituation==True:
                    caughtPiece = self._tiles[toPosition[0]][toPosition[1]]
                    self._tiles[toPosition[0]][toPosition[1]] = None
                    caughtPiece.setPosition(None)
                    caughtPieces.append(caughtPiece)
                p = self._tiles[fromPosition[0]][fromPosition[1]]
                self._tiles[fromPosition[0]][fromPosition[1]] = None
                self._tiles[toPosition[0]][toPosition[1]] = p
                if type(p)==pawn and p.hasMoved()==False and mustCheckCheckSituation==True:
                    #Set piece as en passantable.
                    if p.getColour()==turn.white and toPosition[1]==4:
                        self._enPassant=(p,(toPosition[0],5))
                    elif p.getColour()==turn.black and toPosition[1]==3:
                        self._enPassant=(p,(toPosition[0],2))
                p.setPosition(toPosition)
        if mustCheckCheckSituation:
            situation = self.checkCheckSituation()
        if self._turn==turn.white:
            self._turn=turn.black
        else:
            self._turn=turn.white
        self.convertPawnsIfReached()
        return caughtPieces, situation

    def generateSuccessor(self,movesInTurn):
        successor = copy.deepcopy(self) #TODO: Create own copy function that only copies tiles array (everything else is just a copy of pointers). Though new queens are created (consider dropping pawn/queen conversion and find some way to avoid making millions of piece copies
        successor.makeMoves(movesInTurn,mustCheckCheckSituation=False)
        return successor

    def getLegalMoves(self,currentTurn:turn,inCheck:bool,mustControlIfKingChecked:bool):
        #Previously called isLegalMove.
        #If checked, castling and en passant are disabled (illegal moves).
        moves = list()
        for x in range(len(self._tiles)):
            for y in range(len(self._tiles[0])):
                if self._tiles[x][y]!=None:
                    piece = self._tiles[x][y]
                    if piece.getColour()==currentTurn:
                        for xmove,ymove,moveInt in piece.getMoves():
                            oldPos = (x,y)
                            newPos = (x+xmove,y+ymove)
                            if isValidBoardCoordinate(newPos):
                                isValidMove = False
                                companionMove = None
                                if self._tiles[newPos[0]][newPos[1]]==None:
                                    if moveInt in [1,2,4,6]:
                                        isValidMove = True
                                    elif moveInt==3 and self._enPassant != None:
                                        if newPos==self._enPassant[1]:
                                            companionMove = (self._enPassant[0].getPosition(),None)
                                            isValidMove = True
                                    elif moveInt==5:
                                        if self.isFreePath(oldPos,newPos):
                                            isValidMove = True
                                    elif moveInt==7 and not inCheck:
                                        if self.isCastlingLegal("left"):
                                            companionMove = self.getRookCastlingMove(currentTurn,"left")
                                            isValidMove = True
                                    elif moveInt==71 and not inCheck:
                                        if self.isCastlingLegal("right"):
                                            companionMove = self.getRookCastlingMove(currentTurn,"right")
                                            isValidMove = True
                                else: #Space is occupied
                                    if self._tiles[newPos[0]][newPos[1]].getColour()==oppositeTurn(currentTurn):
                                        if moveInt in [1,3,6]:
                                            isValidMove = True
                                        elif moveInt==5:
                                            if self.isFreePath(oldPos,newPos):
                                                isValidMove = True
                                if isValidMove:
                                    potentialMovesInTurn = [(oldPos,newPos)]
                                    if companionMove:
                                        potentialMovesInTurn.append(companionMove)
                                    if mustControlIfKingChecked:
                                        potentialSuccessor = self.generateSuccessor(potentialMovesInTurn)
                                        if not potentialSuccessor.isKingThreatened(currentTurn):
                                            moves.append(potentialMovesInTurn)
                                    else:
                                        moves.append(potentialMovesInTurn)
        return moves

    def checkCheckSituation(self):
        self._check = False
        attackedPlayer = oppositeTurn(self._turn)
        if self.isKingThreatened(attackedPlayer):
            self._check = True
            if self.discoverCheckMate(attackedPlayer)==True:
                if attackedPlayer==turn.black:
                    return gameSituation.whiteWon
                else:
                    return gameSituation.blackWon
        return gameSituation.inGame
    
    def isKingThreatened(self,kingColour:turn):
        #Check that none of the pieces on the board may catch the king:
        king = self.getKing(kingColour)
        kingPosition = king.getPosition()
        for x in range(len(self._tiles)):
            for y in range(len(self._tiles[0])):
                if self._tiles[x][y] is not None:
                    piece = self._tiles[x][y]
                    if piece.getColour()==oppositeTurn(kingColour):
                        move = (kingPosition[0]-x,kingPosition[1]-y)
                        n = piece.getMoveTypeInt(move)
                        if n in [1,3,6]:
                            return True
                        elif n==5:
                            if self.isFreePath((x,y),kingPosition):
                                return True
        return False

    def discoverCheckMate(self,attackedPlayer:turn):
        if len(self.getLegalMoves(oppositeTurn(self._turn),inCheck=True,mustControlIfKingChecked=True))==0:
            return True
        else:
            return False
    
    def isCastlingLegal(self,side:str) -> bool:
        castlingKing, castlingRook = None, None
        if self._turn==turn.white:
            castlingKing = self._pieces["wking"]
            if side=="left":
                castlingRook = self._pieces["wr1"]
            else:
                castlingRook = self._pieces["wr2"]
        else:
            castlingKing = self._pieces["bking"]
            if side=="left":
                castlingRook = self._pieces["br1"]
            else:
                castlingRook = self._pieces["br2"]
        if castlingRook.hasMoved() or castlingKing.hasMoved():
            return False
        else:
            kingPos = castlingKing.getPosition()
            posDiffX = castlingRook.getPosition()[0]-kingPos[0]
            dir = findDirection([posDiffX,0])
            freepath = True
            for i in range(1,abs(posDiffX)):
                if self._tiles[kingPos[0]+i*dir[0]][kingPos[1]] is not None:
                    freepath = False
            if freepath:
                return True
        return False
    
    def convertPawnsIfReached(self) -> None:
        if self._turn==turn.white:
            endPawnPosition=0
            pawnIndices = ["wp1","wp2","wp3","wp4","wp5","wp6","wp7","wp8"]
        else:
            endPawnPosition=7
            pawnIndices = ["bp1","bp2","bp3","bp4","bp5","bp6","bp7","bp8"]
        for index in pawnIndices:
            if self._pieces[index].getPosition() is not None:
                if self._pieces[index].getPosition()[1]==endPawnPosition:
                    pos = self._pieces[index].getPosition()
                    self._pieces[index] = queen(self._turn,None)
                    self._pieces[index].setPosition(pos)
                    self._tiles[pos[0]][pos[1]]=self._pieces[index]

    def getKing(self,colour:turn):
        if colour==turn.white:
            return self._pieces["wking"]
        else:
            return self._pieces["bking"]

    def getRookCastlingMove(self,colour,direction):
        #Returns the "from" and "to" position.
        if direction=="left":
            if colour==turn.white:
                return ((0,7),(3,7))
            else:
                return ((0,0),(3,0))
        else:
            if colour==turn.white:
                return ((7,7),(5,7))
            else:
                return ((7,0),(5,0))

    def isFreePath(self,location1:tuple,location2:tuple):
        move = (location2[0]-location1[0],location2[1]-location1[1])
        dir = findDirection(move)
        for i in range(1,max(abs(move[0]),abs(move[1]))):
            if self._tiles[int(location1[0]+i*dir[0])][int(location1[1]+i*dir[1])] != None:
                return False
        return True

#TODO:
# -Control what happens at checkmate, fix restart menu.
# -Change cursor when over a piece that may be moved.
# -Significantly simplify member variables in chessBoard class, so generatesuccessor becomes significantly more efficient. (As similar to the old createpotentialboard as possible)
# -Update AI functions.