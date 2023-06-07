from enum import Enum
from stockfish import Stockfish

class ChessPos:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y
    
    def set(self, pos):
        self.x = pos.x
        self.y = pos.y
    
    # 1, 3, ... , 17: gap / 0, 2, ... , 18: piece
    def valid(self):
        return 0 <= self.x <= 18 and 0 <= self.y <= 18
    
    # a1 -> 16, 2
    def setFromName(self, name):
        self.x = (9 - int(name[1])) * 2
        self.y = (ord(name[0]) - ord('a') + 1) * 2
    
    def name(self):
        if self.x % 2 != 0 or self.y % 2 != 0 or self.x == 0 or self.x == 18 or self.y == 0 or self.y == 18:
            return ""
        return f"{chr(self.y // 2 - 1 + ord('a'))}{int(9 - self.x // 2)}"
    
    def input(self, msg):
        try:
            name = input(msg)
            if len(name) != 2:
                raise Exception
            self.setFromName(name)
            if self.valid():
                return
        except:
            pass
        self.input(msg)
    
    def print(self):
        print(f"({self.x}, {self.y})", end='')
    
    def move(self, direction, forward):
        self.x += direction.value[0] * (1 if forward else -1)
        self.y += direction.value[1] * (1 if forward else -1)
    
    def isSame(self, pos):
        return self.x == pos.x and self.y == pos.y

class Direction(Enum):
    up = (-1, 0)
    right = (0, 1)
    down = (1, 0)
    left = (0, -1)

class Chessboard:

    # lower case: black, upper case: white
	# King, Queen, Rook, Bishop, kNight, Pawn
    PIECE = " rnbqkpRNBQKP"

    # 4 = extra space for piece captured
    board = [[' '] * (15 + 4) for _ in range(15 + 4)]
    prevFen = ""
    fen = ""
    extra = ""
    isUserTurn = True
    isOver = False
    startPos = ChessPos()
    endPos = ChessPos()
    robotPos = ChessPos()

    @classmethod
    def toMove(cls):
        return cls.startPos.name() + cls.endPos.name() + cls.extra

    @classmethod
    def fromMove(cls, move):
        cls.startPos.setFromName(move[:2])
        cls.endPos.setFromName(move[2:4])
        cls.extra = move[4:]
    
    @classmethod
    def initBoard(cls):
        cls.board[2] = list("  r n b q k b n r  ")
        cls.board[4] = list("  p p p p p p p p  ")
        cls.board[14] = list("  P P P P P P P P  ")
        cls.board[16] = list("  R N B Q K B N R  ")

    @classmethod
    def printBoard(cls):
        print("\n      a b c d e f g h")
        print("      ---------------")
        print("    " + ''.join(cls.board[0]))
        for i in range(2, 17, 2):
            print(f"{9 - i // 2} | " + ''.join(cls.board[i]))
        print("    " + ''.join(cls.board[18]))
        print("Fen: " + cls.fen + "\n")

    @classmethod
    def canGo(cls, pos, moveRobot = False):
        if not pos.valid():
            return False
        if not moveRobot and cls.board[pos.x][pos.y] != ' ':
            return False
        return True

    @classmethod
    def isWhiteTurn(cls):
        return 'w' in cls.fen

    @classmethod
    def findBlank(cls):
        if cls.isWhiteTurn():
            '''for i in range(2, 17, 2):
                if cls.board[0][i] == ' ':
                    return ChessPos(0, i)'''
            for i in range(2, 9, 2):
                if cls.board[i][0] == ' ':
                    return ChessPos(i, 0)
                if cls.board[i][18] == ' ':
                    return ChessPos(i, 18)
        else:
            '''for i in range(2, 17, 2):
                if cls.board[18][i] == ' ':
                    return ChessPos(18, i)'''
            for i in range(16, 9, -2):
                if cls.board[i][0] == ' ':
                    return ChessPos(i, 0)
                if cls.board[i][18] == ' ':
                    return ChessPos(i, 18)
        # no case for this
        return ChessPos()

    @classmethod
    def movePiece(cls, startPos, endPos, moveRobot = False):
        visited = [[False] * (15 + 4) for _ in range(15 + 4)]
        direction = [[None] * (15 + 4) for _ in range(15 + 4)]
        queue = []
        path = []
        pos = ChessPos(startPos.x, startPos.y)

        visited[pos.x][pos.y] = True
        queue.append(pos)

        while queue:
            pos = queue.pop(0)

            for dir in Direction:
                nextPos = ChessPos(pos.x, pos.y)
                nextDir = dir

                nextPos.move(nextDir, True)
                if cls.canGo(nextPos, moveRobot) and not visited[nextPos.x][nextPos.y]:
                    visited[nextPos.x][nextPos.y] = True
                    direction[nextPos.x][nextPos.y] = nextDir
                    queue.append(nextPos)

        pos.set(endPos)
        while not pos.isSame(startPos):
            path.insert(0, direction[pos.x][pos.y])
            pos.move(direction[pos.x][pos.y], False)

        print(moveRobot)
        print(f"path for {startPos.name()} -> {endPos.name()}: ", end='')
        pos.set(startPos)
        for dir in path:
            pos.print()
            print(f" -> {dir.name} -> ", end='')
            pos.move(dir, True)
        pos.print()
        print()

        if not moveRobot:
            cls.board[endPos.x][endPos.y] = cls.board[startPos.x][startPos.y]
            cls.board[startPos.x][startPos.y] = ' '
        cls.robotPos.set(endPos)

    @classmethod
    def go(cls):
        cls.movePiece(cls.robotPos, cls.startPos, True)

        if not cls.canGo(cls.endPos):
            cls.movePiece(cls.endPos, cls.findBlank())

        if cls.extra:
            cls.board[cls.startPos.x][cls.startPos.y] = cls.extra[0]

        cls.movePiece(cls.startPos, cls.endPos)

        if cls.board[cls.endPos.x][cls.endPos.y] in 'kK':
            if cls.endPos.y - cls.startPos.y == 4:
                cls.movePiece(ChessPos(cls.endPos.x, 16), ChessPos(cls.endPos.x, 12))
            if cls.startPos.y - cls.endPos.y == 4:
                cls.movePiece(ChessPos(cls.endPos.x, 2), ChessPos(cls.endPos.x, 8))

        if cls.prevFen.split(" ")[3] != "-" and cls.fen.split(" ")[3] == "-":
            if cls.board[cls.endPos.x][cls.endPos.y] == 'p':
                cls.movePiece(ChessPos(cls.endPos.x - 2, cls.endPos.y), cls.findBlank())
            if cls.board[cls.endPos.x][cls.endPos.y] == 'P':
                cls.movePiece(ChessPos(cls.endPos.x + 2, cls.endPos.y), cls.findBlank())

    @classmethod
    def isMoveCompleted(cls):
        return True

    @classmethod
    def setTurn(cls):
        try:
            turn = int(input("who will go first; user(0) / AI(1)\n"))
            if turn == 0:
                return True
            elif turn == 1:
                return False
        except Exception as e:
            print(e)
        print("wrong input; choose between 0 and 1")
        return cls.setTurn()

    @classmethod
    def inputMove(cls):
        try:
            pos = input("move: ")
            cls.startPos.setFromName(pos[:2])
            cls.endPos.setFromName(pos[2:4])
            cls.extra = pos[4:]
            if cls.startPos.valid() and cls.endPos.valid():
                return cls.toMove()
        except Exception as e:
            print(e)
        print("wrong input; wrong format")
        return cls.inputMove()

    @classmethod
    def quit(cls):
        return cls.startPos.isSame(cls.endPos)

    @classmethod
    def main(cls):
        cls.initBoard()
        cls.printBoard()

        client = Stockfish()
        if client.startEngine():
            print("start engine")

            client.sendCommand("uci")
            client.getOutput(0, False)

            client.sendCommand("position startPos")
            cls.fen = client.getFen()

            cls.isUserTurn = cls.setTurn()

            while not cls.isOver:
                move, nextFen = "", ""

                if cls.isUserTurn:
                    move = cls.inputMove()
                else:
                    move = client.getBestMove(100)
                    cls.fromMove(move)

                if cls.quit():
                    break

                nextFen = client.moveAndGetFen(cls.fen, move)

                if cls.fen == nextFen:
                    print("wrong input; can't move as above")
                else:
                    cls.prevFen = cls.fen
                    cls.fen = nextFen
                    cls.isUserTurn = not cls.isUserTurn

                    cls.go()

                cls.printBoard()

                move = client.getBestMove(100)

                if move == "(none)":
                    cls.isOver = True
                    print("game over")

            client.stopEngine()
            print("stop engine")
        else:
            print("can't start engine")

if __name__ == "__main__":
    Chessboard.main()
