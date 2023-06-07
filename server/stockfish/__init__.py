from .stockfish import Stockfish
from enum import Enum
from collections import deque


class ChessPiece(Enum):
    EMPTY = " "
    ROOK_BLACK = "r"
    KNIGHT_BLACK = "n"
    BISHOP_BLACK = "b"
    QUEEN_BLACK = "q"
    KING_BLACK = "k"
    PAWN_BLACK = "p"
    ROOK_WHITE = "R"
    KNIGHT_WHITE = "N"
    BISHOP_WHITE = "B"
    QUEEN_WHITE = "Q"
    KING_WHITE = "K"
    PAWN_WHITE = "P"


class ChessPos:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def set(self, pos):
        self.x = ord(pos[0]) - ord('a') + 2
        self.y = 18 - int(pos[1])

    def valid(self):
        return 2 <= self.x <= 17 and 2 <= self.y <= 17

    def is_same(self, pos):
        return self.x == pos.x and self.y == pos.y

    def move(self, direction, increment):
        if direction == Direction.UP:
            self.y += increment
        elif direction == Direction.DOWN:
            self.y -= increment
        elif direction == Direction.LEFT:
            self.x -= increment
        elif direction == Direction.RIGHT:
            self.x += increment

    def name(self):
        return chr(self.x - 2 + ord('a')) + str(9 - self.y // 2)

    def print_pos(self):
        print(self.name(), end='')


class Direction(Enum):
    UP = 0
    DOWN = 1
    LEFT = 2
    RIGHT = 3


class Chessboard:
    PIECE = " rnbqkpRNBQKP"
    board = [[" " for _ in range(15 + 4)] for _ in range(15 + 4)]
    prev_fen = ""
    fen = ""
    extra = ""
    is_user_turn = False
    is_over = False
    start_pos = ChessPos()
    end_pos = ChessPos()

    @staticmethod
    def to_move():
        return (
            Chessboard.start_pos.name() + Chessboard.end_pos.name() + Chessboard.extra
        )

    @staticmethod
    def from_move(move):
        Chessboard.start_pos.set(move[:2])
        Chessboard.end_pos.set(move[2:4])
        Chessboard.extra = move[4:]

    @staticmethod
    def init_board():
        for i in range(19):
            for j in range(19):
                Chessboard.board[i][j] = " "

        Chessboard.board[2] = list("  r n b q k b n r  ")
        Chessboard.board[4] = list("  p p p p p p p p  ")
        Chessboard.board[14] = list("  P P P P P P P P  ")
        Chessboard.board[16] = list("  R N B Q K B N R  ")

    @staticmethod
    def print_board():
        print("\n      a b c d e f g h")
        print("      ---------------")
        print("    " + "".join(Chessboard.board[0]))
        for i in range(2, 17, 2):
            print(f"{9 - i // 2} | {''.join(Chessboard.board[i])}")
        print("    " + "".join(Chessboard.board[18]))
        print("Fen: " + Chessboard.fen + "\n")

    @staticmethod
    def can_go(pos):
        if not pos.valid():
            return False
        if Chessboard.board[pos.x][pos.y] != " ":
            return False
        return True

    @staticmethod
    def is_white_turn():
        return "w" in Chessboard.fen

    @staticmethod
    def find_blank():
        if Chessboard.is_white_turn():
            for i in range(0, 19, 2):
                if Chessboard.board[0][i] == " ":
                    return ChessPos(0, i)
            for i in range(2, 9, 2):
                if Chessboard.board[i][0] == " ":
                    return ChessPos(i, 0)
                if Chessboard.board[i][18] == " ":
                    return ChessPos(i, 18)
        else:
            for i in range(0, 19, 2):
                if Chessboard.board[18][i] == " ":
                    return ChessPos(18, i)
            for i in range(16, 9, -2):
                if Chessboard.board[i][0] == " ":
                    return ChessPos(i, 0)
                if Chessboard.board[i][18] == " ":
                    return ChessPos(i, 18)
        return ChessPos()

    @staticmethod
    def move_piece(start_pos, end_pos):
        visited = [[False for _ in range(15 + 4)] for _ in range(15 + 4)]
        direction = [[None for _ in range(15 + 4)] for _ in range(15 + 4)]
        queue = deque()
        path = deque()
        pos = ChessPos(start_pos.x, start_pos.y)

        visited[pos.x][pos.y] = True
        queue.append(pos)

        while len(queue) > 0:
            pos = queue.popleft()

            for i in range(4):
                next_pos = ChessPos(pos.x, pos.y)
                next_dir = Direction(i)

                next_pos.move(next_dir, True)
                if Chessboard.can_go(next_pos) and not visited[next_pos.x][next_pos.y]:
                    visited[next_pos.x][next_pos.y] = True
                    direction[next_pos.x][next_pos.y] = next_dir
                    queue.append(next_pos)

        pos.set(end_pos)
        while not pos.is_same(start_pos):
            path.appendleft(direction[pos.x][pos.y])
            pos.move(direction[pos.x][pos.y], False)

        print(f"path for {start_pos.name()} -> {end_pos.name()}: ", end="")
        pos.set(start_pos)
        for dir in path:
            pos.print_pos()
            print(f" -> {dir} -> ", end="")
            pos.move(dir, True)
        pos.print_pos()
        print()

        Chessboard.board[end_pos.x][end_pos.y] = Chessboard.board[start_pos.x][
            start_pos.y
        ]
        Chessboard.board[start_pos.x][start_pos.y] = " "

    @staticmethod
    def go():
        if not Chessboard.can_go(Chessboard.end_pos):
            Chessboard.move_piece(Chessboard.end_pos, Chessboard.find_blank())

        # promotion, but don't change piece for convenience
        if Chessboard.extra:
            Chessboard.board[Chessboard.start_pos.x][
                Chessboard.start_pos.y
            ] = Chessboard.extra[0]

        Chessboard.move_piece(Chessboard.start_pos, Chessboard.end_pos)

        # castling
        if Chessboard.board[Chessboard.end_pos.x][Chessboard.end_pos.y] in ["k", "K"]:
            # king side
            if Chessboard.end_pos.y - Chessboard.start_pos.y == 4:
                Chessboard.move_piece(
                    ChessPos(Chessboard.end_pos.x, 16),
                    ChessPos(Chessboard.end_pos.x, 12),
                )
            # queen side
            if Chessboard.start_pos.y - Chessboard.end_pos.y == 4:
                Chessboard.move_piece(
                    ChessPos(Chessboard.end_pos.x, 2), ChessPos(Chessboard.end_pos.x, 8)
                )

        # en passant
        if (
            Chessboard.prev_fen.split(" ")[3] != "-"
            and Chessboard.fen.split(" ")[3] == "-"
        ):
            if Chessboard.board[Chessboard.end_pos.x][Chessboard.end_pos.y] == "p":
                Chessboard.move_piece(
                    ChessPos(Chessboard.end_pos.x - 2, Chessboard.end_pos.y),
                    Chessboard.find_blank(),
                )
            if Chessboard.board[Chessboard.end_pos.x][Chessboard.end_pos.y] == "P":
                Chessboard.move_piece(
                    ChessPos(Chessboard.end_pos.x + 2, Chessboard.end_pos.y),
                    Chessboard.find_blank(),
                )

    @staticmethod
    def is_move_completed():
        return True

    @staticmethod
    def set_turn():
        print("who will go first; user(0) / AI(1)")
        turn = input()
        if turn == "0":
            return True
        elif turn == "1":
            return False
        else:
            print("wrong input; choose between 0 and 1")
            return Chessboard.set_turn()

    @staticmethod
    def input_move():
        print("move: ", end="")
        pos = input()
        Chessboard.start_pos.set(pos[:2])
        Chessboard.end_pos.set(pos[2:4])
        Chessboard.extra = pos[4:]
        if Chessboard.start_pos.valid() and Chessboard.end_pos.valid():
            return Chessboard.to_move()
        else:
            print("wrong input; wrong format")
            return Chessboard.input_move()

    @staticmethod
    def quit():
        return Chessboard.start_pos.is_same(Chessboard.end_pos)

    @staticmethod
    def main():
        Chessboard.init_board()
        Chessboard.print_board()

        client = Stockfish()
        if client.start_engine():
            print("start engine")

            client.send_command("uci")
            client.get_output(0, False)

            client.send_command("position startPos")
            Chessboard.fen = client.get_fen()

            is_user_turn = Chessboard.set_turn()

            while not Chessboard.is_over:
                move = ""
                next_fen = ""

                if is_user_turn:
                    move = Chessboard.input_move()
                else:
                    move = client.get_best_move(100)
                    Chessboard.from_move(move)

                if Chessboard.quit():
                    break

                next_fen = client.move_and_get_fen(Chessboard.fen, move)

                if Chessboard.fen == next_fen:
                    print("wrong input; can't move as above")
                else:
                    Chessboard.prev_fen = Chessboard.fen
                    Chessboard.fen = next_fen
                    is_user_turn = not is_user_turn

                    Chessboard.go()

                Chessboard.print_board()

                move = client.get_best_move(100)

                if move == "(none)":
                    Chessboard.is_over = True
                    print("game over")

            client.stop_engine()
            print("stop engine")
        else:
            print("can't start engine")

