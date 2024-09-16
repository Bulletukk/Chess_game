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

startPositions = {"wp1":(0,6), "wp2":(1,6), "wp3":(2,6), "wp4":(3,6), "wp5":(4,6), "wp6":(5,6), "wp7":(6,6), "wp8":(7,6), "wr1":(0,7), "wr2":(7,7), "wk1":(1,7), "wk2":(6,7), "wb1":(2,7), "wb2":(5,7), "wq":(3,7), "wking":(4,7), "bp1":(0,1), "bp2":(1,1), "bp3":(2,1), "bp4":(3,1), "bp5":(4,1), "bp6":(5,1), "bp7":(6,1), "bp8": (7,1), "br1":(0,0), "br2":(7,0), "bk1":(1,0), "bk2":(6,0), "bb1": (2,0), "bb2":(5,0), "bq":(3,0), "bking":(4,0)}

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
    def __init__(self,t:turn=turn.white,pieces:dict=None,tiles:list=None,unmovedPawnsKingsAndRooks:dict=None):
        self._turn = t
        self._pieces = pieces
        self._tiles = tiles
        self._unMovedPawnsKingsAndRooks = unmovedPawnsKingsAndRooks
        if pieces==None:
            self._pieces = {"wp1": pawn(turn.white), "wp2": pawn(turn.white), "wp3": pawn(turn.white), "wp4": pawn(turn.white), "wp5": pawn(turn.white), "wp6": pawn(turn.white), "wp7": pawn(turn.white), "wp8": pawn(turn.white),
                "wr1": rook(turn.white), "wr2": rook(turn.white), "wk1": knight(turn.white), "wk2": knight(turn.white), "wb1": bishop(turn.white), "wb2": bishop(turn.white), "wq": queen(turn.white), "wking": king(turn.white),
                "bp1": pawn(turn.black), "bp2": pawn(turn.black), "bp3": pawn(turn.black), "bp4": pawn(turn.black), "bp5": pawn(turn.black), "bp6": pawn(turn.black), "bp7": pawn(turn.black), "bp8": pawn(turn.black),
                "br1": rook(turn.black), "br2": rook(turn.black), "bk1": knight(turn.black), "bk2": knight(turn.black), "bb1": bishop(turn.black), "bb2": bishop(turn.black), "bq": queen(turn.black), "bking": king(turn.black)}
        if tiles==None:
            self._tiles = [[None for i in range(8)] for j in range(8)]
            self.__setTiles()
        if unmovedPawnsKingsAndRooks==None:
            self._unMovedPawnsKingsAndRooks = {self._pieces[index] for index in ["wp1","wp2","wp3","wp4","wp5","wp6","wp7","wp8","wr1","wr2","wking","bp1","bp2","bp3","bp4","bp5","bp6","bp7","bp8","br1","br2","bking"]}
        self._check = False
        self._enPassant = None #Indicates pawn (chessPiece, [Board position], [Position which it may be caught from]) which, for one move only, may be caught by pawn of opposing team.
    
    def copy(self):
        #Only actually (shallow) copies the tiles array and the set of unmoved pieces. No pieces or the "pieces" array are actually copied, but point to the original data.
        newTiles = list()
        for column in self._tiles:
            copiedColumn = column.copy()
            newTiles.append(copiedColumn)
        newUnmovedPawnsKingsAndRooks = self._unMovedPawnsKingsAndRooks.copy()
        return chessBoard(self._turn,self._pieces,newTiles,newUnmovedPawnsKingsAndRooks)

    def __setTiles(self):
        for index in self._pieces:
            p = self._pieces[index]
            self._tiles[startPositions[index][0]][startPositions[index][1]] = p

    def getCheckSituation(self):
        return self._check
    
    def getTiles(self):
        return self._tiles
    
    def getTurn(self):
        return self._turn
    
    def hidePiece(self,location):
        self._tiles[location[0]][location[1]] = None

    def showPiece(self,piece,location):
        self._tiles[location[0]][location[1]] = piece

    def pieceHasMoved(self,piece):
        return piece not in self._unMovedPawnsKingsAndRooks

    def setPieceAsMoved(self,piece):
        if piece in self._unMovedPawnsKingsAndRooks:
            self._unMovedPawnsKingsAndRooks.remove(piece)

    def findPosition(self,piece):
        for x in range(8):
            for y in range(8):
                if self._tiles[x][y] == piece:
                    return (x,y)
        return None

    def makeMoves(self,movesInTurn,mustCheckCheckSituation:bool):
        #Moves is a list of moves (each move being a tuple with from coordinate and to coordinate)
        #MovesInTurn is a list of moves to be done in this turn, normally just one move, but two when castling/en passant is being done.
        self._enPassant = None
        situation = gameSituation.inGame
        caughtPieces = list()
        for move in movesInTurn:
            fromPosition, toPosition = move
            if toPosition == None:
                #This code is only called upon during en passant.
                p = self._tiles[fromPosition[0]][fromPosition[1]]
                self._tiles[fromPosition[0]][fromPosition[1]] = None
                self.setPieceAsMoved(p)
                caughtPieces.append(p)
            else:
                if self._tiles[toPosition[0]][toPosition[1]]!=None and mustCheckCheckSituation==True:
                    caughtPiece = self._tiles[toPosition[0]][toPosition[1]]
                    self._tiles[toPosition[0]][toPosition[1]] = None
                    caughtPieces.append(caughtPiece)
                    self.setPieceAsMoved(caughtPiece)
                p = self._tiles[fromPosition[0]][fromPosition[1]]
                self._tiles[fromPosition[0]][fromPosition[1]] = None
                self._tiles[toPosition[0]][toPosition[1]] = p
                if type(p)==pawn and self.pieceHasMoved(p)==False and mustCheckCheckSituation==True:
                    #Set piece as en passantable.
                    if p.getColour()==turn.white and toPosition[1]==4:
                        self._enPassant=(p,toPosition,(toPosition[0],5))
                    elif p.getColour()==turn.black and toPosition[1]==3:
                        self._enPassant=(p,toPosition,(toPosition[0],2))
                self.setPieceAsMoved(p)
        if mustCheckCheckSituation:
            self.__convertPawnsIfReached()
        if self._turn==turn.white:
            self._turn=turn.black
        else:
            self._turn=turn.white
        if mustCheckCheckSituation:
            situation = self.checkCheckSituation()
        return caughtPieces, situation

    def generateSuccessor(self,movesInTurn):
        successor = self.copy()
        successor.makeMoves(movesInTurn,mustCheckCheckSituation=False)
        return successor

    def getLegalMoves(self,mustControlIfKingChecked:bool):
        if mustControlIfKingChecked and not self._check:
            enableCastling = True #Castling is enabled if not in check and we're not finding legal moves in AI adversarial search at depth>1.
        else:
            enableCastling = False
        moves = list()
        for x in range(8):
            for y in range(8):
                if self._tiles[x][y]!=None:
                    piece = self._tiles[x][y]
                    if piece.getColour()==self._turn:
                        for xmove,ymove,moveInt in piece.getMoves(self.pieceHasMoved(piece)):
                            oldPos = (x,y)
                            newPos = (x+xmove,y+ymove)
                            if isValidBoardCoordinate(newPos):
                                isValidMove = False
                                companionMove = None
                                if self._tiles[newPos[0]][newPos[1]]==None:
                                    if moveInt in [1,2,4,6]:
                                        isValidMove = True
                                    elif moveInt==3 and self._enPassant != None:
                                        if newPos==self._enPassant[2]:
                                            companionMove = (self._enPassant[1],None)
                                            isValidMove = True
                                    elif moveInt==5:
                                        if self.isFreePath(oldPos,newPos):
                                            isValidMove = True
                                    elif moveInt==7 and enableCastling==True:
                                        if self.isCastlingLegal("left"):
                                            companionMove = self.getRookCastlingMove(self._turn,"left")
                                            isValidMove = True
                                    elif moveInt==71 and enableCastling==True:
                                        if self.isCastlingLegal("right"):
                                            companionMove = self.getRookCastlingMove(self._turn,"right")
                                            isValidMove = True
                                else: #Space is occupied
                                    if self._tiles[newPos[0]][newPos[1]].getColour()==oppositeTurn(self._turn):
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
                                        if not potentialSuccessor.isKingThreatened():
                                            moves.append(potentialMovesInTurn)
                                    else:
                                        moves.append(potentialMovesInTurn)
        return moves

    def checkCheckSituation(self):
        self._check = False
        if self.isKingThreatened():
            self._check = True
        if len(self.getLegalMoves(mustControlIfKingChecked=True))==0:
            #There are no legal moves for the coming turn. -> Game over.
            if self._check==True:
                if self._turn==turn.black:
                    return gameSituation.whiteWon
                else:
                    return gameSituation.blackWon
            else:
                #Not in check, but no legal moves, so we have stalemate.
                return gameSituation.staleMate
        return gameSituation.inGame
    
    def isKingThreatened(self):
        #Check that none of the pieces on the board may catch the king:
        king = self.getKing()
        kingPosition = self.findPosition(king)
        for x in range(8):
            for y in range(8):
                if self._tiles[x][y] is not None:
                    piece = self._tiles[x][y]
                    if piece.getColour()==oppositeTurn(self._turn):
                        move = (kingPosition[0]-x,kingPosition[1]-y)
                        n = piece.getMoveTypeInt(move)
                        if n in [1,3,6]:
                            return True
                        elif n==5:
                            if self.isFreePath((x,y),kingPosition):
                                return True
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
        if self.pieceHasMoved(castlingRook) or self.pieceHasMoved(castlingKing):
            return False
        else:
            kingPos = self.findPosition(castlingKing)
            posDiffX = self.findPosition(castlingRook)[0]-kingPos[0]
            dir = findDirection([posDiffX,0])
            freepath = True
            for i in range(1,abs(posDiffX)):
                if self._tiles[kingPos[0]+i*dir[0]][kingPos[1]] is not None:
                    freepath = False
            if freepath:
                return True
        return False
    
    def __convertPawnsIfReached(self) -> None:
        if self._turn==turn.white:
            endPawnPosition=0
            pawnIndices = ["wp1","wp2","wp3","wp4","wp5","wp6","wp7","wp8"]
        else:
            endPawnPosition=7
            pawnIndices = ["bp1","bp2","bp3","bp4","bp5","bp6","bp7","bp8"]
        for x in range(8):
            piece = self._tiles[x][endPawnPosition]
            for index in pawnIndices:
                if self._pieces[index] == piece:
                    #Convert pawn to queen.
                    self._pieces[index] = queen(self._turn)
                    self._tiles[x][endPawnPosition]=self._pieces[index]
                    break

    def getKing(self):
        if self._turn==turn.white:
            return self._pieces["wking"]
        else:
            return self._pieces["bking"]

    def getRookCastlingMove(self,direction):
        #Returns the "from" and "to" position.
        if direction=="left":
            if self._turn==turn.white:
                return ((0,7),(3,7))
            else:
                return ((0,0),(3,0))
        else:
            if self._turn==turn.white:
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