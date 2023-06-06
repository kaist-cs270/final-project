from typing import List

from fastapi import FastAPI, File, UploadFile
from aiofile import async_open
from tempfile import gettempdir
from pathlib import Path

from server.chessboard.chess import detect


app = FastAPI()

cnt = 0
state = 0
tmp_filename = Path(gettempdir())
board = None

def is_valid_change(next: List[List[int]]) -> bool:
    differ = 0
    for i in range(8):
        for j in range(8):
            if board[i][j] != next[i][j]:
                differ += 1
    return differ <= 2


def rotate(board: List[List[int]]) -> List[List[int]]:
    return list(map(list, zip(*board[::-1])))

@app.post("/image")
async def image(file: UploadFile = File(...)):
    try:
        while state != 0:
            pass
        state = 1
        filename = tmp_filename / f"image-{cnt}.jpg"
        cnt += 1
        async with async_open(filename, "wb") as f:
            await f.write(await file.read())
        res = detect(filename)
        if res == None:
            state = 0
            return
        if board == None:
            board = res
        else:
            for _ in range(4):
                if is_valid_change(res):
                    board = res
                    # todo: send to chess robot
                    break
                res = rotate(res)
    except Exception as e:
        return e
    finally:
        state = 0