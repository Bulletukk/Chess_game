import chessPiece, chessBoard
from enum import Enum
import random

random.seed()

initialTotalPieceValue = 400
minMaxSearchLimit = 2
alphaBetaSearchLimit = 10

class AITypes(Enum):
    easyAI = 1
    mediumAI = 2
    hardAI = 3
    dementedAI = 4

def doAIMove(c:chessBoard.chessBoard,AIType):
    moves = c.getLegalMoves(mustControlIfKingChecked=True)
    if AIType==AITypes.easyAI:
        move = BasicEvaluationMove(c,moves)
    else:
        #elif AIType==AITypes.mediumAI:
        move = MinMaxSearchMove(c,moves)
    #elif AIType==AITypes.hardAI:
    #    move = AlphaBetaSearchMove(c,moves)
    #elif AIType==AITypes.dementedAI:
    #    move = DementedAIMove(c,moves)
    addedCaughtPieces, situation = c.makeMoves(move,mustCheckCheckSituation=True)
    shouldDoAIMove = False
    return addedCaughtPieces, situation, shouldDoAIMove

def BasicEvaluationMove(c:chessBoard.chessBoard,moves:list):
    #Picks the highest evaluated possible move.
    random.shuffle(moves)
    highestEval = 0
    bestMove = None
    for move in moves:
        currentEval = BoardEval(c,c.getTurn())
        if currentEval > highestEval:
            highestEval = currentEval
            bestMove = move
    return bestMove
    
def MinMaxSearchMove(c:chessBoard.chessBoard,moves:list):
    #Performs minmax search down to the globally defined search limit.
    maxVal, bestMove = float('-inf'), None
    random.shuffle(moves)
    for move in moves:
        potentialSuccessor = c.generateSuccessor(move)
        newVal = minMaxValue(c,c.getTurn(),depth=1)
        if newVal>maxVal:
            maxVal = newVal
            bestMove = move
    print(maxVal,bestMove)
    return bestMove
"""
def AlphaBetaSearchMove(c:chessGame, moves:list[tuple[chessPiece,tuple[int,int]]],originalPositionPawns:list[chessPiece]) -> tuple[chessPiece,tuple[int,int]]:
    #Performs alpha beta search down to the globally defined alpha beta search limit.
    alpha, beta = float('-inf'), float('inf')
    maxVal, bestMove = float('-inf'), None
    random.shuffle(moves)
    for move in moves:
        potentialBoard,pawns = createBoard(c.tiles,move,originalPositionPawns)
        newVal = alphaBetaMinValue(potentialBoard,pawns,c.turn,1,alpha,beta)
        if newVal>maxVal:
            maxVal = newVal
            bestMove = move
        if maxVal >= beta:
            return maxVal
        alpha = max(alpha,maxVal)
    return bestMove

def DementedAIMove(c:chessGame, moves: list[tuple[chessPiece,tuple[int,int]]], originalPositionPawns:list):
    functionNo = random.randint(0,3)
    if functionNo==0:
        return RandomMove(moves)
    elif functionNo==1:
        return BasicEvaluationMove(c,moves)
    elif functionNo==2:
        return MinMaxSearchMove(c,moves,originalPositionPawns)
    else:
        return AlphaBetaSearchMove(c,moves,originalPositionPawns)
"""
def minMaxValue(board:chessBoard.chessBoard,player:chessPiece.turn,depth:int):
    if depth >= minMaxSearchLimit:
        return BoardEval(board,player)
    if depth%2==1:
        #Looking at a potential opponent's turn. Find minimum value:
        moves = board.getLegalMoves(mustControlIfKingChecked=False)
        random.shuffle(moves)
        minVal = float('inf')
        for move in moves:
            potentialBoard = board.generateSuccessor(move)
            newVal = minMaxValue(potentialBoard,player,depth+1)
            minVal = min(minVal,newVal)
        return minVal
    else:
        #Looking at own turn. Find maximum value:
        moves = board.getLegalMoves(mustControlIfKingChecked=False)
        random.shuffle(moves)
        maxVal = float('-inf')
        for move in moves:
            potentialBoard = board.generateSuccessor(move)
            newVal = minMaxValue(potentialBoard,player,depth+1)
            maxVal = max(minVal,newVal)
        return maxVal
"""
def alphaBetaMaxValue(potentialBoard:np.array,originalPositionPawns,turn:turn,depth:int,alpha,beta):
    if depth >= minMaxSearchLimit:
        return BoardEval(potentialBoard,turn)
    moves = getLegalActions(potentialBoard,originalPositionPawns,turn)
    random.shuffle(moves)
    maxVal = float('-inf') 
    for move in moves:
        board, pawns = createBoard(potentialBoard,move,originalPositionPawns)
        newVal = alphaBetaMinValue(board,pawns,turn,depth+1,alpha,beta)
        maxVal = max(maxVal,newVal)
        if maxVal >= beta:
            return maxVal
        alpha = max(alpha,maxVal)
    return maxVal

def alphaBetaMinValue(potentialBoard:np.array,originalPositionPawns,turn:turn,depth:int,alpha,beta):
    if depth >= minMaxSearchLimit:
        return BoardEval(potentialBoard,turn)
    moves = getLegalActions(potentialBoard,originalPositionPawns,oppositeTurn(turn))
    random.shuffle(moves)
    minVal = float('inf')
    for move in moves:
        board, pawns = createBoard(potentialBoard,move,originalPositionPawns)
        newVal = alphaBetaMaxValue(board,pawns,turn,depth+1,alpha,beta)
        minVal = min(minVal,newVal)
        if minVal <= alpha:
            return minVal
        alpha = min(beta,minVal)
    return minVal"""

def BoardEval(potentialBoard:chessBoard.chessBoard,player:chessPiece.turn) -> int:
    #Note to self: Consider having this function also find potential moves.
    standingPiecesWeighting = 45 #Own remaining pieces. #Set to zero for the time being, as we only do one (own) turn.
    takenPiecesWeighting = 35 #Opponent taken pieces.
    ownThreatenedPiecesWeighting = 6
    opponentThreatenedPiecesWeighting = 4
    ownCoveredPiecesWeighting = 4 #Own covered pieces: when their position can be reached by another piece of same colour, so they are "protected".
    pawnAdvancementWeighting = 6 #How far the pawns have come on the board.

    standingPiecesScore = 0
    takenPiecesScore = initialTotalPieceValue
    ownThreatenedPiecesScore = 0 #Will be <=0.
    opponentThreatenedPiecesScore = 0
    ownCoveredPiecesScore = 0
    ownCoveredPieces = set()
    ownKingTaken = True
    opponentKingTaken = True
    pawnAdvancementScore = 0
    for x in range(8):
        for y in range(8):
            piece = potentialBoard.getTiles()[x][y]
            if piece is not None:
                if piece.getColour()==player:
                    if type(piece) == chessPiece.king:
                        ownKingTaken = False
                    else:
                        standingPiecesScore += piece.getValue()
                        if type(piece) == chessPiece.pawn:
                            if player==chessPiece.turn.white:
                                pawnAdvancementScore += piece.getValue()*(6 - y)
                            else:
                                pawnAdvancementScore += piece.getValue()*(y - 1)
                else:
                    if type(piece) is chessPiece.king:
                        opponentKingTaken = False
                    else:
                        takenPiecesScore -= piece.getValue()
                hasMoved = potentialBoard.pieceHasMoved(piece)
                for xmove,ymove,moveInt in piece.getMoves(hasMoved):
                    mayCatch = False
                    newPos = (x+xmove,y+ymove)
                    if chessBoard.isValidBoardCoordinate(newPos):
                        if moveInt in [1,3,6]:
                            mayCatch = True
                        elif moveInt==5:
                            if potentialBoard.isFreePath((x,y),newPos):
                                mayCatch = True
                        if mayCatch:
                            threatenedPiece = potentialBoard.getTiles()[newPos[0]][newPos[1]]
                            if threatenedPiece is not None:
                                if piece.getColour()==player:
                                    if threatenedPiece.getColour()==piece.getColour(): #Own piece protects own piece.
                                        ownCoveredPieces.add(threatenedPiece)
                                    else: #Own piece may catch opponent piece.
                                        opponentThreatenedPiecesScore += threatenedPiece.getValue()
                                else:
                                    if threatenedPiece.getColour()==chessBoard.oppositeTurn(piece.getColour()): #Opponent piece may catch own piece.
                                        ownThreatenedPiecesScore -= threatenedPiece.getValue()
    for piece in ownCoveredPieces:
        if type(piece) != chessPiece.king:
            ownCoveredPiecesScore += piece.getValue()
    if ownKingTaken:
        return -100000000
    elif opponentKingTaken:
        return 100000000
    else:
        return standingPiecesWeighting*standingPiecesScore+takenPiecesWeighting*takenPiecesScore+ownThreatenedPiecesWeighting*ownThreatenedPiecesScore+opponentThreatenedPiecesWeighting*opponentThreatenedPiecesScore+ownCoveredPiecesWeighting*ownCoveredPiecesScore+pawnAdvancementWeighting*pawnAdvancementScore