import pyautogui
import win32gui

from nursery.modules.config import APP_NAME, APP_SHOT_FILENAME, ORIGIN_WIDTH


def appShot():
    # Find the handle of the application window
    hwnd = win32gui.FindWindow(None, APP_NAME)
    if hwnd == 0:
        print("Can't find the window")
        exit()

    # Get the dimensions of the window
    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
    width, height = right - left, bottom - top

    im = pyautogui.screenshot(region=(left, top, width, height))
    im.save(APP_SHOT_FILENAME)

    scale = width / ORIGIN_WIDTH

    return (left, top, scale)
