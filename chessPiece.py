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
    #Note: This enum class is used both to denote the turn, and the colour of the pieces.
    white = 1
    black = 2

class chessPiece:
    def __init__(self, colour: turn):
        self._colour = colour
        self._value = None
        self._moves = None
    def getColour(self):
        return self._colour
    def getValue(self):
        return self._value
    def getMoves(self,hasMoved:bool):
        return self._legalMoves
    def getMoveTypeInt(self,move: tuple):
        for legalMove in self._legalMoves:
            if move[0]==legalMove[0] and move[1]==legalMove[1]:
                return legalMove[2]
        return 0

class pawn(chessPiece):
    def __init__(self, colour: turn):
        super().__init__(colour)
        self._value = 10
        if self._colour==turn.white:
            self._legalMoves = [(0,-1,2), (1,-1,3), (-1,-1,3)]
        else:
            self._legalMoves = [(0,1,2), (1,1,3), (-1,1,3)]
    def getMoves(self,hasMoved:bool):
        if hasMoved:
            return self._legalMoves
        else:
            if self._colour==turn.white:
                return [(0,-1,2), (1,-1,3), (-1,-1,3), (0,-2,4)]
            else:
                return [(0,1,2), (1,1,3), (-1,1,3), (0,2,4)]
    def findPointsToDraw(self,s):
        return [(s[0]+15,s[1]),(s[0]+15,s[1]-7.5),(s[0]+7.5,s[1]-15),(s[0]+7.5,s[1]-35),(s[0]-7.5,s[1]-35),(s[0]-7.5,s[1]-15),(s[0]-15,s[1]-7.5),(s[0]-15,s[1])]

class rook(chessPiece):
    def __init__(self, colour: turn):
        super().__init__(colour)
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
    def __init__(self, colour: turn):
        super().__init__(colour)
        self._legalMoves = [(-1,-2,1),(-2,-1,1),(-2,1,1),(-1,2,1),(1,2,1),(2,1,1),(2,-1,1),(1,-2,1)]
        self._value = 40
    def findPointsToDraw(self,s):
        return [(s[0]+15,s[1]),(s[0]+15,s[1]-7),(s[0]+10,s[1]-7),(s[0]+20,s[1]-25),(s[0]+17,s[1]-35),(s[0]+8,s[1]-40),(s[0]-5,s[1]-42),(s[0]-20,s[1]-25),(s[0],s[1]-30),(s[0],s[1]-25),(s[0]-7,s[1]-15),(s[0]-10,s[1]-7),(s[0]-15,s[1]-7),(s[0]-15,s[1])]

class bishop(chessPiece):
    def __init__(self, colour: turn):
        super().__init__(colour)
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
    def __init__(self, colour: turn):
        super().__init__(colour)
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
    def __init__(self, colour: turn):
        super().__init__(colour)
        self._legalMoves = [(0,-1,6),(-1,-1,6),(-1,0,6),(-1,1,6),(0,1,6),(1,1,6),(1,0,6),(1,-1,6),(2,0,71),(-2,0,7)]
        self._value = 200
    def findPointsToDraw(self,s):
        return [(s[0]+15,s[1]),(s[0]+15,s[1]-7),(s[0]+10,s[1]-7),(s[0]+18,s[1]-23),(s[0]+20,s[1]-30),(s[0]+18,s[1]-33),(s[0]+15,s[1]-35),(s[0]+3.5,s[1]-30),(s[0]+1.5,s[1]-35),(s[0]+4.6,s[1]-36),(s[0]+4.6,s[1]-38),(s[0]+1.5,s[1]-38),(s[0]-1.5,s[1]-42),(s[0]+1.5,s[1]-42),(s[0]-1.5,s[1]-38),(s[0]-4.6,s[1]-38),(s[0]-4.6,s[1]-36),(s[0]-1.5,s[1]-35),(s[0]-3.5,s[1]-30),(s[0]-15,s[1]-35),(s[0]-18,s[1]-33),(s[0]-20,s[1]-30),(s[0]-18,s[1]-23),(s[0]-10,s[1]-7),(s[0]-15,s[1]-7),(s[0]-15,s[1])]