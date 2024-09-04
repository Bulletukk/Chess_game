import chessPiece,chessBoard, chessGUI, chessAI
import pygame

class chessGame:
    def __init__(self):
        self._gameSituation = chessBoard.gameSituation.start
        self._AIType = chessAI.AITypes.easyAI
        self._caughtPieces = {chessPiece.turn.white:[],chessPiece.turn.black:[]}
        self._GUI = chessGUI()
        self._chessBoard = chessBoard.chessBoard(chessBoard.gameMode.playAsWhite,chessPiece.turn.white)

    def runGame(self):
        pygame.init()
        running = True
        mouseButtonPressed = False
        waitbeforeAIMove = 50
        shouldDoAIMove = False
        while running:
            mCoord = pygame.mouse.get_pos() #Mouse position in Pygame coordinates
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN and not mouseButtonPressed and self.gameSituation==chessBoard.gameSituation.inGame:
                    mouseButtonPressed = True
                    self._GUI.pickUpPiece(self._chessBoard,mCoord)
                elif event.type == pygame.MOUSEBUTTONUP and mouseButtonPressed and self.gameSituation==chessBoard.gameSituation.inGame:
                    mouseButtonPressed = False
                    if self._hoverPiece is not None:
                        self._shouldDoAIMove = self._GUI.placePiece(self._chessBoard,mCoord)
                elif event.type == pygame.MOUSEBUTTONDOWN and not mouseButtonPressed and self.gameSituation!=chessBoard.gameSituation.inGame:
                    mouseButtonPressed = True
                    self.modifyGame(self._GUI.chooseFromMenu(self.gameSituation,mCoord))
                elif event.type == pygame.MOUSEBUTTONUP and mouseButtonPressed and self.gameSituation!=chessBoard.gameSituation.inGame:
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
            self._GUI.draw(self._chessBoard,self._gameSituation,self._caughtPieces,mCoord)
            pygame.display.flip()
        pygame.quit()

    def modifyGame(self,choice):
        if choice==None:
            pass
        else:
            if choice==chessBoard.gameMode.playAsWhite:
                #Resetting game, playing as white.
                self._chessBoard = chessBoard.chessBoard(chessBoard.gameMode.playAsWhite,chessPiece.turn.white)
                self._caughtPieces = {chessPiece.turn.white:[],chessPiece.turn.black:[]}
            elif choice==chessBoard.gameMode.playAsBlack:
                #Resettting game, playing as black.
                self._chessBoard = chessBoard.chessBoard(chessBoard.gameMode.playAsBlack,chessPiece.turn.black)
                self._caughtPieces = {chessPiece.turn.white:[],chessPiece.turn.black:[]}
            else:
                if type(choice)!=chessAI.AITypes:
                    raise ValueError
                self._AIType = choice