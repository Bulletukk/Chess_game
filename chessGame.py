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
        self._shouldDoAIMove = False

    def runGame(self):
        pygame.init()
        running = True
        mouseButtonPressed = False
        waitbeforeAIMove = 100
        while running:
            mCoord = pygame.mouse.get_pos() #Mouse position in Pygame coordinates
            pygame.mouse.set_cursor(self.chooseCursorType(mCoord))
            self._GUI.draw(self._chessBoard,self._gameSituation,self._caughtPieces,self._gameMode,mCoord)
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN and not mouseButtonPressed:
                    mouseButtonPressed = True
                    if self._gameSituation==chessBoard.gameSituation.inGame:
                        if not self._shouldDoAIMove:
                            self._GUI.pickUpPiece(self._chessBoard,self._gameMode,mCoord)
                    else:
                        self.modifyGame(self._GUI.chooseFromMenu(mCoord))
                elif event.type == pygame.MOUSEBUTTONUP and mouseButtonPressed:
                    mouseButtonPressed = False
                    if self._gameSituation==chessBoard.gameSituation.inGame:
                        if self._GUI.getHoverPiece() is not None:
                            addedCaughtPieces, self._gameSituation, self._shouldDoAIMove = self._GUI.placePiece(self._chessBoard,self._gameMode,mCoord)
                            self.addCaughtPieces(addedCaughtPieces)
                    else:
                        #No action.
                        mouseButtonPressed = False
                elif event.type == pygame.QUIT:
                    #Red X button pressed, exit game.
                    running = False
                else:
                    continue
            if self._shouldDoAIMove:
                waitbeforeAIMove -= 1
            if waitbeforeAIMove == 0:
                addedCaughtPieces, self._gameSituation, self._shouldDoAIMove = chessAI.doAIMove(self._chessBoard,self._AIType)
                self.addCaughtPieces(addedCaughtPieces)
                waitbeforeAIMove = 100
            pygame.display.flip()
        pygame.quit()

    def chooseCursorType(self,mCoord):
        if self._GUI.getHoverPiece() != None:
            return pygame.SYSTEM_CURSOR_HAND
        elif self._gameSituation==chessBoard.gameSituation.inGame:
            location = self._GUI.pointToPieceLocation(mCoord,self._gameMode)
            if not self._shouldDoAIMove and chessBoard.isValidBoardCoordinate(location):
                piece = self._chessBoard.getTiles()[location[0]][location[1]]
                if piece is not None:
                    if piece.getColour()==self._chessBoard.getTurn():
                        return pygame.SYSTEM_CURSOR_HAND
        else:
            if self._GUI.getMenuChoice()==chessGUI.menuSituation.pickSide and ((mCoord[0]>443.5 and mCoord[0]<657.7) or (mCoord[0]>219.3 and mCoord[0]<433.5)) and mCoord[1]>348.5 and mCoord[1]<411.5:
                return pygame.SYSTEM_CURSOR_HAND
            elif ((mCoord[0]>216.25 and mCoord[0]<319.575) or (mCoord[0]>329.975 and mCoord[0]<433.3) or (mCoord[0]>443.7 and mCoord[0]<547.025) or (mCoord[0]>557.425 and mCoord[0]<660.75)) and mCoord[1]>348.5 and mCoord[1]<411.5:
                return pygame.SYSTEM_CURSOR_HAND
        return pygame.SYSTEM_CURSOR_ARROW

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
                if self._gameMode == chessBoard.gameMode.playAsBlack:
                    self._shouldDoAIMove = True

    def addCaughtPieces(self,addedCaughtPieces):
        for p in addedCaughtPieces:
            self._caughtPieces[p.getColour()].append(p)