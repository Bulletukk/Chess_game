import chessPiece, chessBoard
from enum import Enum
import random

random.seed()

initialTotalPieceValue = 400
minMaxSearchLimit = 2
alphaBetaSearchLimit = 3

class AITypes(Enum):
    easyAI = 1
    mediumAI = 2
    hardAI = 3
    dementedAI = 4

def doAIMove(c:chessBoard.chessBoard,AIType):
    moves = c.getLegalMoves(mustControlIfKingChecked=True)
    if AIType==AITypes.easyAI:
        move = BasicEvaluationMove(c,moves)
    elif AIType==AITypes.mediumAI:
        move = MinMaxSearchMove(c,moves)
    elif AIType==AITypes.hardAI:
        move = AlphaBetaSearchMove(c,moves)
    elif AIType==AITypes.dementedAI:
        move = DementedAIMove(c,moves)
    addedCaughtPieces, situation = c.makeMoves(move,mustCheckCheckSituation=True)
    shouldDoAIMove = False
    return addedCaughtPieces, situation, shouldDoAIMove

def BasicEvaluationMove(c:chessBoard.chessBoard,moves:list):
    #Picks the highest evaluated possible move.
    random.shuffle(moves)
    highestEval = 0
    bestMove = None
    for move in moves:
        potentialSuccessor = c.generateSuccessor(move)
        currentEval = BoardEval(potentialSuccessor,c.getTurn())
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
        newVal = minMaxValue(potentialSuccessor,c.getTurn(),depth=1)
        if newVal>maxVal:
            maxVal = newVal
            bestMove = move
    return bestMove

def AlphaBetaSearchMove(c:chessBoard.chessBoard, moves:list):
    #Performs alpha beta search down to the globally defined alpha beta search limit.
    alpha, beta = float('-inf'), float('inf')
    maxVal, bestMove = float('-inf'), None
    random.shuffle(moves)
    for move in moves:
        potentialSuccessor = c.generateSuccessor(move)
        newVal = alphaBetaMinValue(potentialSuccessor,c.getTurn(),alpha,beta,depth=1)
        if newVal>maxVal:
            maxVal = newVal
            bestMove = move
        if maxVal >= beta:
            return bestMove
        alpha = max(alpha,maxVal)
    return bestMove

def DementedAIMove(c:chessBoard.chessBoard, moves:list):
    functionNo = random.randint(0,2)
    if functionNo==0:
        return BasicEvaluationMove(c,moves)
    elif functionNo==1:
        return MinMaxSearchMove(c,moves)
    else:
        return AlphaBetaSearchMove(c,moves)

def minMaxValue(board:chessBoard.chessBoard,player:chessPiece.turn,depth:int):
    if depth >= minMaxSearchLimit:
        return BoardEval(board,player)
    moves = board.getLegalMoves(mustControlIfKingChecked=False)
    random.shuffle(moves)
    if depth%2==1:
        #Looking at a potential opponent's turn. Find minimum value:
        minVal = float('inf')
        for move in moves:
            potentialBoard = board.generateSuccessor(move)
            newVal = minMaxValue(potentialBoard,player,depth+1)
            minVal = min(minVal,newVal)
        return minVal
    else:
        #Looking at own turn. Find maximum value:
        maxVal = float('-inf')
        for move in moves:
            potentialBoard = board.generateSuccessor(move)
            newVal = minMaxValue(potentialBoard,player,depth+1)
            maxVal = max(maxVal,newVal)
        return maxVal

def alphaBetaMaxValue(board:chessBoard.chessBoard,player:chessPiece.turn,alpha,beta,depth:int):
    if depth >= alphaBetaSearchLimit:
        return BoardEval(board,player)
    moves = board.getLegalMoves(mustControlIfKingChecked=False)
    random.shuffle(moves)
    maxVal = float('-inf')
    for move in moves:
        potentialBoard = board.generateSuccessor(move)
        newVal = alphaBetaMinValue(potentialBoard,player,alpha,beta,depth+1)
        maxVal = max(newVal,maxVal)
        if maxVal >= beta:
            return maxVal
        alpha = max(alpha,newVal)
    return maxVal

def alphaBetaMinValue(board:chessBoard.chessBoard,player:chessPiece.turn,alpha,beta,depth:int):
    if depth >= alphaBetaSearchLimit:
        return BoardEval(board,player)
    moves = board.getLegalMoves(mustControlIfKingChecked=False)
    random.shuffle(moves)
    minVal = float('inf')
    returnVal = float('inf')
    for move in moves:
        potentialBoard = board.generateSuccessor(move)
        newVal = alphaBetaMaxValue(potentialBoard,player,alpha,beta,depth+1)
        minVal = min(newVal,minVal)
        returnVal = min(newVal,minVal+1500)
        if minVal <= alpha:
            return minVal
        beta = min(beta,newVal)
    return returnVal

def BoardEval(potentialBoard:chessBoard.chessBoard,player:chessPiece.turn,printValues=False) -> int:
    #Note to self: Consider having this function also find potential moves.
    standingPiecesWeighting = 50 #Own remaining pieces. #Set to zero for the time being, as we only do one (own) turn.
    takenPiecesWeighting = 16 #Opponent taken pieces.
    ownThreatenedPiecesWeighting = 20
    opponentThreatenedPiecesWeighting = 10
    ownCoveredPiecesWeighting = 4 #Own covered pieces: when their position can be reached by another piece of same colour, so they are "protected".

    standingPiecesScore = 0
    takenPiecesScore = initialTotalPieceValue
    ownThreatenedPiecesScore = 0 #Will be <=0.
    opponentThreatenedPiecesScore = 0
    ownCoveredPiecesScore = 0
    ownCoveredPieces = set()
    for x in range(8):
        for y in range(8):
            piece = potentialBoard.getTiles()[x][y]
            if piece is not None:
                if type(piece) != chessPiece.king:
                    if piece.getColour()==player:
                        standingPiecesScore += piece.getValue()
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
    if printValues==True:
        print("standingPiecesWeighting*standingPiecesScore", standingPiecesWeighting*standingPiecesScore)
        print("takenPiecesWeighting*takenPiecesScore", takenPiecesWeighting*takenPiecesScore)
        print("ownThreatenedPiecesWeighting*ownThreatenedPiecesScore", ownThreatenedPiecesWeighting*ownThreatenedPiecesScore)
        print("opponentThreatenedPiecesWeighting*opponentThreatenedPiecesScore", opponentThreatenedPiecesWeighting*opponentThreatenedPiecesScore)
        print("ownCoveredPiecesWeighting*ownCoveredPiecesScore", ownCoveredPiecesWeighting*ownCoveredPiecesScore)
    return standingPiecesWeighting*standingPiecesScore+takenPiecesWeighting*takenPiecesScore+ownThreatenedPiecesWeighting*ownThreatenedPiecesScore+opponentThreatenedPiecesWeighting*opponentThreatenedPiecesScore+ownCoveredPiecesWeighting*ownCoveredPiecesScore