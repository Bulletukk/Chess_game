import numpy as np
from enum import Enum

"""
MoveTypes (numbered in the chess piece classes' legalmoves functions):
1: Ordinary move: to empty tile, or to catch a piece of opposing team
2: Non-catch move: only to empty tile (only for pawns)
3: Only-catch move: only to catch a piece of opposing team (only for pawns)
4: Initial-only move: only if piece has never been moved before (only for pawns). Note that this is also a non-catch move.
5: Clear-path move: like 1) Ordinary move, except free path is also required
6: King-move: Must check (epic wordplay) that we don't move the king to a checkable location.
7: Castling move (king<->left rook): A king moves to the left in a castling move. Simulatenous rook movement required.
71: Castling move (king<->right rook): A king moves to the right in a castling move. Simultaneous rook movement required.
"""

class turn(Enum):
    white = 1
    black = 2

class chessPiece:
    def __init__(self, colour: turn, position):
        self._legalMoves = None #array of tuples containing (x-change, y-change, MoveType)
        self._colour = colour
        self._position = position #Position given in (0 to 7)^2.
        self._hasMoved = False
        self._value = None
    def setPosition(self, position):
        self._position = position
        if self._hasMoved==False:
            self._hasMoved = True
    def getPosition(self):
        return self._position
    def getColour(self):
        return self._colour
    def getMoves(self):
        return self._legalMoves
    def hasMoved(self):
        return self._hasMoved
    def getValue(self):
        return self._value
    def getMoveTypeInt(self,move: tuple):
        for legalMove in self._legalMoves:
            if move[0]==legalMove[0] and move[1]==legalMove[1]:
                return legalMove[2]
        return 0

class pawn(chessPiece):
    def __init__(self, colour: turn, position):
        super().__init__(colour,position)
        if self._colour==turn.white:
            self._legalMoves = [(0,-1,2), (1,-1,3), (-1,-1,3), (0,-2,4)]
        elif self._colour==turn.black:
            self._legalMoves = [(0,1,2), (1,1,3), (-1,1,3), (0,2,4)]
        self._value = 10
    def findPointsToDraw(self,s):
        return [(s[0]+15,s[1]),(s[0]+15,s[1]-7.5),(s[0]+7.5,s[1]-15),(s[0]+7.5,s[1]-35),(s[0]-7.5,s[1]-35),(s[0]-7.5,s[1]-15),(s[0]-15,s[1]-7.5),(s[0]-15,s[1])]
    def setPosition(self, position):
        if self._hasMoved == False:
            #This is the first move. Modify legalMoves (remove initial move)
            if self._colour==turn.white:
                self._legalMoves = [(0,-1,2), (1,-1,3), (-1,-1,3)]
            elif self._colour==turn.black:
                self._legalMoves = [(0,1,2), (1,1,3), (-1,1,3)]
            self._hasMoved = True
        self._position = position

class rook(chessPiece):
    def __init__(self, colour: turn, position):
        super().__init__(colour,position)
        self._legalMoves = [(0,-1,1),(-1,0,1),(0,1,1),(1,0,1)]
        for i in range(2,8):
            self._legalMoves.append((0,-i,5))
            self._legalMoves.append((-i,0,5))
            self._legalMoves.append((0,i,5))
            self._legalMoves.append((i,0,5))
        self._value = 30
    def findPointsToDraw(self,s):
        return [(s[0]+15,s[1]),(s[0]+15,s[1]-7.5),(s[0]+7.5,s[1]-15),(s[0]+7.5,s[1]-30),(s[0]+12,s[1]-30),(s[0]+12,s[1]-42.5),(s[0]-12,s[1]-42.5),(s[0]-12,s[1]-30),(s[0]-7.5,s[1]-30),(s[0]-7.5,s[1]-15),(s[0]-15,s[1]-7.5),(s[0]-15,s[1])]

class knight(chessPiece):
    def __init__(self, colour: turn, position):
        super().__init__(colour,position)
        self._legalMoves = [(-1,-2,1),(-2,-1,1),(-2,1,1),(-1,2,1),(1,2,1),(2,1,1),(2,-1,1),(1,-2,1)]
        self._value = 40
    def findPointsToDraw(self,s):
        return [(s[0]+15,s[1]),(s[0]+15,s[1]-7),(s[0]+10,s[1]-7),(s[0]+20,s[1]-25),(s[0]+17,s[1]-35),(s[0]+8,s[1]-40),(s[0]-5,s[1]-42),(s[0]-20,s[1]-25),(s[0],s[1]-30),(s[0],s[1]-25),(s[0]-7,s[1]-15),(s[0]-10,s[1]-7),(s[0]-15,s[1]-7),(s[0]-15,s[1])]

class bishop(chessPiece):
    def __init__(self, colour: turn, position):
        super().__init__(colour,position)
        self._legalMoves = [(-1,-1,1),(-1,1,1),(1,1,1),(1,-1,1)]
        for i in range(2,8):
            self._legalMoves.append((-i,-i,5))
            self._legalMoves.append((-i,i,5))
            self._legalMoves.append((i,i,5))
            self._legalMoves.append((i,-i,5))
        self._value = 40
    def findPointsToDraw(self,s):
        return [(s[0]+15,s[1]),(s[0]+15,s[1]-7),(s[0]+10,s[1]-7),(s[0]+13,s[1]-23),(s[0]+12,s[1]-34),(s[0]+5,s[1]-42),(s[0],s[1]-25),(s[0]-5,s[1]-42),(s[0]-12,s[1]-34),(s[0]-13,s[1]-23),(s[0]-10,s[1]-7),(s[0]-15,s[1]-7),(s[0]-15,s[1])]

class queen(chessPiece):
    def __init__(self, colour: turn, position):
        super().__init__(colour,position)
        self._legalMoves = [(0,-1,1),(-1,0,1),(0,1,1),(1,0,1),(-1,-1,1),(-1,1,1),(1,1,1),(1,-1,1)]
        for i in range(2,8):
            self._legalMoves.append((0,-i,5))
            self._legalMoves.append((-i,0,5))
            self._legalMoves.append((0,i,5))
            self._legalMoves.append((i,0,5))
            self._legalMoves.append((-i,-i,5))
            self._legalMoves.append((-i,i,5))
            self._legalMoves.append((i,i,5))
            self._legalMoves.append((i,-i,5))
        self._value = 100
    def findPointsToDraw(self,s):
        return [(s[0]+15,s[1]),(s[0]+15,s[1]-7),(s[0]+10,s[1]-7),(s[0]+23,s[1]-35),(s[0]+10,s[1]-26),(s[0]+5,s[1]-42),(s[0],s[1]-28),(s[0]-5,s[1]-42),(s[0]-10,s[1]-26),(s[0]-23,s[1]-35),(s[0]-10,s[1]-7),(s[0]-15,s[1]-7),(s[0]-15,s[1])]
    
class king(chessPiece):
    def __init__(self, colour: turn, position):
        super().__init__(colour,position)
        self._legalMoves = [(0,-1,6),(-1,-1,6),(-1,0,6),(-1,1,6),(0,1,6),(1,1,6),(1,0,6),(1,-1,6),(2,0,71),(-2,0,7)]
        self._value = 200
    def findPointsToDraw(self,s):
        return [(s[0]+15,s[1]),(s[0]+15,s[1]-7),(s[0]+10,s[1]-7),(s[0]+18,s[1]-23),(s[0]+20,s[1]-30),(s[0]+18,s[1]-33),(s[0]+15,s[1]-35),(s[0]+3.5,s[1]-30),(s[0]+1.5,s[1]-35),(s[0]+4.6,s[1]-36),(s[0]+4.6,s[1]-38),(s[0]+1.5,s[1]-38),(s[0]-1.5,s[1]-42),(s[0]+1.5,s[1]-42),(s[0]-1.5,s[1]-38),(s[0]-4.6,s[1]-38),(s[0]-4.6,s[1]-36),(s[0]-1.5,s[1]-35),(s[0]-3.5,s[1]-30),(s[0]-15,s[1]-35),(s[0]-18,s[1]-33),(s[0]-20,s[1]-30),(s[0]-18,s[1]-23),(s[0]-10,s[1]-7),(s[0]-15,s[1]-7),(s[0]-15,s[1])]