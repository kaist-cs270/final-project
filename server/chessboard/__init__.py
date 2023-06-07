from pathlib import Path
from tempfile import gettempdir
from typing import List, Tuple
from aiofile import async_open
from fastapi import File, UploadFile
from server.chessboard.chess import detect


tmp_filename = Path(gettempdir())


def rotate(board: List[List[int]]) -> List[List[int]]:
    return list(map(list, zip(*board[::-1])))


def diff(board1: List[List[int]], board2: List[List[int]]) -> int:
    res = 0
    for i in range(8):
        for j in range(8):
            if board1[i][j] != board2[i][j]:
                res += 1
    return res


def count_board(board) -> Tuple[int, int]:
    w_cnt = 0
    b_cnt = 0

    for i in range(8):
        for j in range(8):
            if next[i][j] == 0:
                b_cnt += 1
            if next[i][j] == 2:
                w_cnt += 1

    return w_cnt, b_cnt


def print_board(board: List[List[int]]):
    for i in board:
        for j in i:
            print(j, end="")
        print()

class Chess:
    read_state: int = 0
    past_detect_states: List[List[List[int]]] = []
    next_move = None
    cnt = 0
    curr_state: List[List[int]] = None

    @classmethod
    def init(cls) -> None:
        cls.curr_state = []
        for i in range(8):
            t = []
            for _ in range(8):
                if i < 2:
                    t.append(0)
                elif i < 6:
                    t.append(1)
                else:
                    t.append(2)

        for _ in range(10):
            cls.past_detect_states.append(cls.curr_state)

    @classmethod
    def check_valid(cls, next) -> bool:
        w1, b1 = count_board(next)
        w2, b2 = count_board(cls.curr_state)
        d = diff(cls.curr_state, next)

        if d == 0:
            return True
        if w1 == w2 and b1 == b2 and d == 2:
            return True
        if w1 == w2 - 1 and b1 == b2 and d == 2:
            return True
        if b1 == b2 - 1 and w1 == w2 and d == 2:
            return True
        return False

    @classmethod
    def get_state_from_past(cls) -> List[str]:
        """
        Calculates the most likely state of the chessboard from past states.
        """
        res = []

        for i in range(8):
            t = []
            for j in range(8):
                l = {}
                for k in range(len(cls.past_detect_states)):
                    s = cls.past_detect_states[k]
                    if s[i][j] not in l:
                        l[s[i][j]] = 0
                    l[s[i][j]] += 1
                t.append(max(l, key=l.get))
            res.append(t)
        return res

    @classmethod
    async def read_image(cls, file: UploadFile = File(...)):
        try:
            if cls.read_state != 0:
                return "dropped"
            cls.read_state = 1
            filename = tmp_filename / f"image-{cls.cnt}.jpg"
            print(f"save to: {filename}")
            cls.cnt += 1
            async with async_open(filename, "wb") as f:
                await f.write(await file.read())
            res = detect(str(filename))
            if res is None:
                cls.read_state = 0
                return "failed"

            min_res = res
            if len(cls.past_detect_states) > 0:
                state = cls.get_state_from_past()
                min_diff = diff(state, res)

                for _ in range(4):
                    res = rotate(res)
                    d = diff(state, res)
                    if d < min_diff:
                        min_diff = d
                        min_res = res

            print(min_res)
            cls.past_detect_states.append(min_res)
            if len(cls.past_detect_states) > 10:
                cls.past_detect_states.pop(0)

            if cls.curr_state is None:
                cls.curr_state = min_res

            # todo: Connect to java

            if not cls.check_valid(min_res):
                return "not valid"
            
            

            cls.next_move = "a1a2"

        except Exception as e:
            cls.read_state = 0
            raise e
        cls.read_state = 0
        return "ok"

    @classmethod
    def get_move(cls):
        if cls.next_move is None:
            return "none"
        return cls.next_move

    @classmethod
    def done_move(cls):
        cls.next_move = None
        return "ok"
