import chessPiece,chessBoard, chessGUI, chessAI
import pygame

class chessGame:
    def __init__(self):
        self._gameSituation = chessBoard.gameSituation.start
        self._AIType = chessAI.AITypes.easyAI
        self._caughtPieces = {chessPiece.turn.white:[],chessPiece.turn.black:[]}
        self._GUI = chessGUI.chessGUI()
        self._chessBoard = chessBoard.chessBoard()
        self._gameMode = chessBoard.gameMode.playAsWhite

    def runGame(self):
        pygame.init()
        running = True
        mouseButtonPressed = False
        waitbeforeAIMove = 50
        shouldDoAIMove = False
        while running:
            mCoord = pygame.mouse.get_pos() #Mouse position in Pygame coordinates
            pygame.mouse.set_cursor(self._GUI.chooseCursorType(mCoord,self._chessBoard,self._gameSituation,mouseButtonPressed,self._gameMode))
            self._GUI.draw(self._chessBoard,self._gameSituation,self._caughtPieces,self._gameMode,mCoord)
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN and not mouseButtonPressed and self._gameSituation==chessBoard.gameSituation.inGame:
                    mouseButtonPressed = True
                    self._GUI.pickUpPiece(self._chessBoard,self._gameMode,mCoord)
                elif event.type == pygame.MOUSEBUTTONUP and mouseButtonPressed and self._gameSituation==chessBoard.gameSituation.inGame:
                    mouseButtonPressed = False
                    if self._GUI.getHoverPiece() is not None:
                        addedCaughtPieces, situation, shouldDoAIMove = self._GUI.placePiece(self._chessBoard,self._gameMode,mCoord)
                        if type(situation)==chessBoard.gameSituation:
                            self._gameSituation = situation
                        self.addCaughtPieces(addedCaughtPieces)
                elif event.type == pygame.MOUSEBUTTONDOWN and not mouseButtonPressed and self._gameSituation!=chessBoard.gameSituation.inGame:
                    mouseButtonPressed = True
                    self.modifyGame(self._GUI.chooseFromMenu(mCoord))
                elif event.type == pygame.MOUSEBUTTONUP and mouseButtonPressed and self._gameSituation!=chessBoard.gameSituation.inGame:
                    #No action.
                    mouseButtonPressed = False
                elif event.type == pygame.QUIT:
                    #Red X button pressed, exit game.
                    running = False
            """
            if shouldDoAIMove:
            waitbeforeAIMove -= 1
            if waitbeforeAIMove<=0:
                doAIMove(c) #Commenting out disables all AI.
                waitbeforeAIMove = 100
            """
            pygame.display.flip()
        pygame.quit()

    def modifyGame(self,choice):
        if choice==None:
            pass
        else:
            if choice==chessBoard.gameMode.playAsWhite:
                #Resetting game, playing as white.
                self._chessBoard = chessBoard.chessBoard()
                self._caughtPieces = {chessPiece.turn.white:[],chessPiece.turn.black:[]}
                self._gameMode = chessBoard.gameMode.playAsWhite
            elif choice==chessBoard.gameMode.playAsBlack:
                #Resettting game, playing as black.
                self._chessBoard = chessBoard.chessBoard()
                self._caughtPieces = {chessPiece.turn.white:[],chessPiece.turn.black:[]}
                self._gameMode = chessBoard.gameMode.playAsBlack
            else:
                if type(choice)!=chessAI.AITypes:
                    raise ValueError
                self._AIType = choice
                self._gameSituation = chessBoard.gameSituation.inGame

    def addCaughtPieces(self,addedCaughtPieces):
        for p in addedCaughtPieces:
            self._caughtPieces[p.getColour()].append(p)