from typing import List

import cv2

from common import FrameSize


class Camera:
    def __init__(self, src: int, frame_size: FrameSize, fps: int, no_frames_auto_settings: int) -> None:
        self.src: int = src
        self.frame_size: FrameSize = frame_size
        self.fps: int = fps
        self.no_frames_auto_settings: int = no_frames_auto_settings
        self.cap: cv2.VideoCapture = cv2.VideoCapture(src)

        if not self.cap.isOpened():
            raise Exception("Couldn't open a video capture")

        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, frame_size.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, frame_size.height)
        self.cap.set(cv2.CAP_PROP_FPS, fps)
        # TODO: disable auto settings -> set exposure, brightness, ... manually

    def take_frames(self, n: int) -> List:
        frames = []

        for i in range(self.no_frames_auto_settings + n):
            ret, frame = self.cap.read()
            if not ret:
                raise Exception("Didn't receive frame")
            frames.append(frame)

        return frames[-n:]

    def release_cap(self) -> None:
        self.cap.release()
