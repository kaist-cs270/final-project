from pathlib import Path
from typing import List, Tuple
from ultralytics import YOLO
import numpy as np
import cv2

curr = Path(__file__).parent

corner_model = YOLO(curr / "./runs/detect/chessboard-corner4/weights/best.pt")
piece_model = YOLO(curr / "./runs/classify/chessboard-corner5/weights/best.pt")


def warp_image(
    image: np.ndarray, corners: np.ndarray, size: Tuple[int, int]
) -> np.ndarray:
    """
    Warp image to a rectangle with given corners and size
    """
    dst = np.array(
        [[0, 0], [size[0] - 1, 0], [size[0] - 1, size[1] - 1], [0, size[1] - 1]],
        dtype="float32",
    )

    M = cv2.getPerspectiveTransform(corners, dst)
    warped = cv2.warpPerspective(image, M, size)

    return warped


def detect(path: str) -> List[List[int]]:
    image = cv2.imread(path)
    results = corner_model.predict(image, save=False, verbose=False)
    boxes = results[0].boxes.xyxy.numpy().tolist()
    corners = list(
        map(lambda box: [(box[0] + box[2]) / 2, (box[1] + box[3]) / 2], boxes)
    )

    # Sort corners by convex hull algorithm
    corners = np.array(corners, dtype=np.float32)
    corners = cv2.convexHull(corners)
    corners = corners.reshape((-1, 2))

    final_corners = []

    # If corners are too close, remove them
    for y, x in corners:
        flag = False
        for p, q in final_corners:
            if abs(p - y) < 10 and abs(q - x) < 10:
                flag = True
                break
        if not flag:
            final_corners.append((y, x))

    corners = np.array(final_corners[:4])
    if len(corners) < 4:
        print("Not enough corners")
        return

    warped = warp_image(image, corners, (640, 640))

    gray = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)
    lines = cv2.HoughLines(edges, 1, np.pi / 180, 150)

    horizontal_lines = [(i * 80, np.pi / 2) for i in range(9)]
    vertical_lines = [(i * 80, 0) for i in range(9)]

    for line in lines:
        is_vertical = False
        rho, theta = line[0]
        if theta < np.pi / 4 or theta > 3 * np.pi / 4:
            is_vertical = True

        co = np.cos(theta)
        si = np.sin(theta)

        if is_vertical:
            m = int((rho - 320 * si) / co)
            idx = int((m + 40) / 80)
            if idx >= 0 and idx < 9:
                vertical_lines[idx] = (rho, theta)
        else:
            m = int((rho - 320 * co) / si)
            idx = int((m + 40) / 80)
            if idx >= 0 and idx < 9:
                horizontal_lines[idx] = (rho, theta)

    cross_points = []

    for i in range(9):
        points = []
        for j in range(9):
            # Find intersection of two lines
            rho1, theta1 = horizontal_lines[i]
            rho3, theta3 = vertical_lines[j]

            A = np.array(
                [[np.cos(theta1), np.sin(theta1)], [np.cos(theta3), np.sin(theta3)]]
            )
            b = np.array([rho1, rho3])
            x0, y0 = np.linalg.solve(A, b)
            x0 = int(x0)
            y0 = int(y0)
            # cv2.circle(warped, (x0, y0), 5, (0, 0, 255), -1)
            points.append((x0, y0))
        cross_points.append(points)

    res = []
    # save each cell as image
    for i in range(8):
        l = []
        for j in range(8):
            x1, y1 = cross_points[i][j]
            x2, y2 = cross_points[i + 1][j]
            x3, y3 = cross_points[i + 1][j + 1]
            x4, y4 = cross_points[i][j + 1]

            img = warp_image(
                warped,
                np.array([[x1, y1], [x2, y2], [x3, y3], [x4, y4]], dtype=np.float32),
                (80, 80),
            )
            t = piece_model.predict(img, save=False, verbose=False)[0].probs.top1
            l.append(t if t != 3 else 1)
        res.append(l)

    cv2.imwrite("1.jpg", warped)
    return res


if __name__ == "__main__":
    a = detect("./corner-data/test/images/1_mp4-30_jpg.rf.ba3b85836c51fce041db4e26038d4e3f.jpg")
    for i in a:
        print(i)