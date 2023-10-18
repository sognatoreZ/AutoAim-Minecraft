import time

import cv2 as cv
import dxcam
import pyautogui
import pygetwindow as gw
from loguru import logger
import threading
import keyboard

# Change these consts if necessary
FPS = 60
WIN_SIZE = (1080, 720)
WIN_CENTER = (WIN_SIZE[0] // 2, WIN_SIZE[1] // 2 + 10)
WIN_TITLE = "Minecraft 1.12.2"
LABELS = {0: 'bee', 1: 'chicken', 2: 'cow', 3: 'creeper', 4: 'enderman', 5: 'fox', 6: 'frog', 7: 'ghast', 8: 'goat',
          9: 'llama', 10: 'pig', 11: 'sheep', 12: 'skeleton', 13: 'spider', 14: 'turtle', 15: 'wolf', 16: 'zombie'}
N_TYPES = len(LABELS)


class MinecraftController(object):

    def __init__(self):
        self.cam = dxcam.create()
        self.cam.start(self._get_win_coord(), FPS)

    @staticmethod
    def _get_win_coord():
        mc_wins = gw.getWindowsWithTitle(WIN_TITLE)
        assert mc_wins, "No Minecraft instance found. Launch your game before running the assist."
        mc_win = mc_wins[0]
        mc_win.activate()
        mc_win.resizeTo(*WIN_SIZE)
        return mc_win.left, mc_win.top, mc_win.right, mc_win.bottom

    def view_at(self, x, y):
        # TODO: Call rotate_view() to move the center of the window (WIN_CENTER) to (x, y)
        ...

    def grub_frame(self):
        return cv.cvtColor(self.cam.get_latest_frame(), cv.COLOR_RGB2BGR)

    @staticmethod
    def rotate_view(x, y):
        logger.debug(f"Move mouse: {x}, {y}. Current position: {pyautogui.position()}")
        pyautogui.moveRel(x, y)

    @staticmethod
    def apply():
        pyautogui.rightClick()


class VideoProcessThread(threading.Thread):
    def __init__(self, controller: MinecraftController):
        super().__init__()
        self._stop = threading.Event()
        self.ctrl = controller

        self.enable_aim_assist = False
        self.target_type = 7

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.is_set()

    def run(self):
        logger.info("VideoProcessThread start.")

        frame_ctr = 0
        t = time.perf_counter()

        while not self.stopped():
            frame = self.ctrl.grub_frame()

            # TODO: Run detection & call MinecraftController.view_at() to aim self.target_type
            ...

            # Draw aiming center
            cv.line(frame, (WIN_CENTER[0], WIN_CENTER[1] - 20), (WIN_CENTER[0], WIN_CENTER[1] + 20), (0, 0, 255), 5)
            cv.line(frame, (WIN_CENTER[0] - 20, WIN_CENTER[1]), (WIN_CENTER[0] + 20, WIN_CENTER[1]), (0, 0, 255), 5)

            # Show preview
            cv.imshow("Detection", frame)
            _ = cv.waitKey(1)

            # Calc FPS
            frame_ctr += 1
            if frame_ctr % 100 == 0:
                logger.debug(f"FPS: {100 / (time.perf_counter() - t)}")
                t = time.perf_counter()

    def loop_target_type(self):
        self.target_type = (self.target_type + 2) % (N_TYPES + 1) - 1
        logger.info(f"Current target: {LABELS[self.target_type] if self.target_type >= 0 else 'None'}")

    def switch_aiming(self):
        self.enable_aim_assist = not self.enable_aim_assist
        logger.info(f"Aim Assist: {'ON' if self.enable_aim_assist else 'OFF'}")


if __name__ == "__main__":
    logger.info("Minecraft Aim Assist start.")
    pyautogui.PAUSE = 0
    # logger.level("INFO")

    ctrl = MinecraftController()
    video_process_thread = VideoProcessThread(ctrl)
    video_process_thread.start()

    # keyboard.add_hotkey("up", lambda: MinecraftController.rotate_view(0, -20))
    # keyboard.add_hotkey("down", lambda: MinecraftController.rotate_view(0, 20))
    # keyboard.add_hotkey("left", lambda: MinecraftController.rotate_view(-20, 0))
    # keyboard.add_hotkey("right", lambda: MinecraftController.rotate_view(20, 0))
    keyboard.add_hotkey("r", video_process_thread.switch_aiming)
    keyboard.add_hotkey("m", video_process_thread.loop_target_type)

    keyboard.wait("ctrl+esc")
    video_process_thread.stop()
