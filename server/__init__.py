from fastapi import FastAPI, File, UploadFile
from server.chessboard import Chess


app = FastAPI()


@app.post("/upload-image")
async def image(file: UploadFile = File(...)):
    return await Chess.read_image(file)


@app.get("/get-move")
async def move():
    return Chess.get_move()


@app.post("/done-move")
async def done_move():
    return Chess.done_move()
