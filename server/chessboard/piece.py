from pathlib import Path
from ultralytics import YOLO
import click

curr = Path(__file__).parent


@click.group()
def main():
    pass


@main.command()
def train():
    model = YOLO("yolov8n-cls.pt")

    model.train(
        data=curr / "piece-data",
        imgsz=640,
        epochs=100,
        batch=8,
        name="chessboard-corner",
    )


@main.command()
def test():
    model = YOLO(curr / "runs/detect/chessboard-corner5/weights/best.pt")

    model.track("1.mp4", save=True)


if __name__ == "__main__":
    main()
