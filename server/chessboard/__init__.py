from pathlib import Path
from tempfile import gettempdir
from typing import List
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


class Chess:
    read_state: int = 0
    past_detect_states: List[List[List[int]]] = []
    next_move = None

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
            filename = tmp_filename / f"image-{cnt}.jpg"
            print(f"save to: {filename}")
            cnt += 1
            async with async_open(filename, "wb") as f:
                await f.write(await file.read())
            res = detect(filename)
            if res == None:
                return "failed"
            state = cls.get_state_from_past()
            min_diff = diff(state, res)
            min_res = res

            for _ in range(4):
                res = rotate(res)
                d = diff(state, res)
                if d < min_diff:
                    min_diff = d
                    min_res = res

            cls.past_detect_states.append(min_res)
            if len(cls.past_detect_states) > 10:
                cls.past_detect_states.pop(0)

            # todo: Connect to java

            cls.next_move = "a1a2"

        except Exception as e:
            cls.read_state = 0
            raise e
        cls.read_state = 0
        return "ok"

    @classmethod
    def get_move(cls):
        if cls.next_move == None:
            return "none"
        return cls.next_move

    @classmethod
    def done_move(cls):
        cls.next_move = None
        return "ok"
