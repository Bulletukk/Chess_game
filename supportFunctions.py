from chessPieces import *
from enum import Enum

#Rules determining drawing of pieces:
def oppositeColour(colour: str):
    if colour=="black":
        return "white"
    elif colour=="white":
        return "black"

def shiftPoints(pointsToDraw: list, bottomCentre: tuple):
    shiftedPoints = []
    for point in pointsToDraw:
        shiftedPoints.append((point[0] + 0.02*(point[0]-bottomCentre[0]), point[1] + 0.02*(point[1]-bottomCentre[1])))
    return shiftedPoints

#Functions for rules on the board:
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

def isFreePath(tiles:np.array,location1:tuple,location2:tuple) -> bool:
    move = (location2[0]-location1[0],location2[1]-location1[1])
    dir = findDirection(move)
    for i in range(1,max(abs(move[0]),abs(move[1]))):
        if tiles[int(location1[0]+i*dir[0]),int(location1[1]+i*dir[1])] != None:
            return False
    return True

def isLegalBoardCoordinate(location: tuple) -> bool:
    if location[0] >= 0 and location[0] < 8 and location[1] >= 0 and location[1] < 8:
        return True
    else:
        return False
    
class gameMode(Enum):
    playAsWhite = 1
    playAsBlack = 2
    def toColour(self):
        if self==gameMode.playAsWhite:
            return "white"
        elif self==gameMode.playAsBlack:
            return "black"
        else:
            raise ValueError

class gameSituation(Enum):
    start = 1
    inGame = 2
    whiteWon = 3
    blackWon = 4
    staleMate = 5

class turn(Enum):
    white = 1
    black = 2

class AITypes(Enum):
    easyAI = 1
    mediumAI = 2
    hardAI = 3
    dementedAI = 4

def turnToColour(t:turn):
    if t==turn.white:
        return "white"
    elif t==turn.black:
        return "black"
    else:
        raise ValueError
    
def colourToTurn(colour:str):
    if colour=="white":
        return turn.white
    elif colour=="black":
        return turn.black
    else:
        raise ValueError

def findPosition(tiles:np.array,p:chessPiece) -> tuple:
    for x in range(len(tiles)):
        for y in range(len(tiles)):
            if tiles[x,y]==p:
                return (x,y)
    return None

def oppositeTurn(turn):
    if turn==turn.white:
        return turn.black
    elif turn==turn.black:
        return turn.white

chessPieceValues = {
    pawn:10,
    rook:30,
    knight:40,
    bishop:40,
    queen:100,
    king:200
}