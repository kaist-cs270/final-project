from ultralytics import YOLO
import click


@click.group()
def main():
    pass


@main.command()
def train():
    model = YOLO("yolov8n.pt")

    model.train(
        data="corner-data/data.yaml", imgsz=640, epochs=100, batch=8, name="chessboard-corner"
    )


@main.command()
def test():
    model = YOLO("./runs/detect/chessboard-corner5/weights/best.pt")

    model.track("1.mp4", save=True)


if __name__ == "__main__":
    main()
