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

def doAIMove(c:chessBoard.chessBoard):
    moves = c.getLegalMoves(mustControlIfKingChecked=True)
    

    moves, originalPositionPawns = c.getPossibleMoves()
    if len(moves)==0:
        c.staleMate()
        return
    if c.AIType==AITypes.easyAI:
        p,oldLocation,newLocation = BasicEvaluationMove(c,moves)
    elif c.AIType==AITypes.mediumAI:
        p,oldLocation,newLocation = MinMaxSearchMove(c,moves,originalPositionPawns)
    elif c.AIType==AITypes.hardAI:
        p,oldLocation,newLocation = AlphaBetaSearchMove(c,moves,originalPositionPawns)
    elif c.AIType==AITypes.dementedAI:
        p,oldLocation,newLocation = DementedAIMove(c,moves,originalPositionPawns)
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
    c.shouldDoAIMove = False

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
    
def MinMaxSearchMove(c:chessGame, moves:list[tuple[chessPiece,tuple[int,int]]],originalPositionPawns:list[chessPiece]) -> tuple[chessPiece,tuple[int,int]]:
    #Performs minmax search down to the globally defined search limit.
    maxVal, bestMove = float('-inf'), None
    random.shuffle(moves)
    for move in moves:
        potentialBoard,pawns = createBoard(c.tiles,move,originalPositionPawns)
        newVal = minMaxValue(potentialBoard,pawns,c.turn,1)
        if newVal>maxVal:
            maxVal = newVal
            bestMove = move
    return bestMove

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

def BoardEval(potentialBoard: np.array,currentTurn:turn) -> int:
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
    for x in range(len(potentialBoard)):
        for y in range(len(potentialBoard)):
            piece = potentialBoard[x,y]
            if piece is not None:
                if piece.getColour()==turnToColour(currentTurn):
                    if type(piece) is king:
                        ownKingTaken = False
                    else:
                        standingPiecesScore += chessPieceValues[type(piece)]
                        if type(piece) == pawn:
                            if currentTurn==turn.white:
                                pawnAdvancementScore += chessPieceValues[pawn]*(6 - y)
                            else:
                                pawnAdvancementScore += chessPieceValues[pawn]*(y - 1)
                else:
                    if type(piece) is king:
                        opponentKingTaken = False
                    else:
                        takenPiecesScore -= chessPieceValues[type(piece)]
                for xmove,ymove,moveInt in piece.getMoves():
                    mayCatch = False
                    newPos = (x+xmove,y+ymove)
                    if isValidBoardCoordinate(newPos):
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
        return standingPiecesWeighting*standingPiecesScore+takenPiecesWeighting*takenPiecesScore+ownThreatenedPiecesWeighting*ownThreatenedPiecesScore+opponentThreatenedPiecesWeighting*opponentThreatenedPiecesScore+ownCoveredPiecesWeighting*ownCoveredPiecesScore+pawnAdvancementWeighting*pawnAdvancementScore

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
    if depth >= minMaxSearchLimit:
        return BoardEval(potentialBoard,turn)
    if depth%2==1:
        #Looking at a potential opponent's turn. Find minimum value:
        moves = getLegalActions(potentialBoard,originalPositionPawns,oppositeTurn(turn))
        random.shuffle(moves)
        minVal = float('inf')
        for move in moves:
            board, pawns = createBoard(potentialBoard,move,originalPositionPawns)
            newVal = minMaxValue(board,pawns,turn,depth+1)
            minVal = min(minVal,newVal)
        return minVal
    else:
        #Find maximum value:
        moves = getLegalActions(potentialBoard,originalPositionPawns,turn)
        random.shuffle(moves)
        maxVal = float('-inf')
        for move in moves:
            board, pawns = createBoard(potentialBoard,move,originalPositionPawns)
            newVal = minMaxValue(board,pawns,turn,depth+1)
            maxVal = max(maxVal,newVal)
        return maxVal
    
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