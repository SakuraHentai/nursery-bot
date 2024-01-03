import signal
import time
from multiprocessing import Process, Queue, active_children
from random import randint

import pyautogui

from nursery.modules.config import GRID_GAP, GRID_SIZE, OFFSET_TOP, OFFSET_X


def _getMousePosByGridPos(appInfo, gridPos, needOffset=False):
    (appX, appY, scale) = appInfo
    y, x = gridPos
    scaledOffsetX = OFFSET_X * scale
    scaledOffsetTop = OFFSET_TOP * scale
    scaledGridSize = GRID_SIZE * scale
    scaledGridGap = GRID_GAP * scale

    # Offset need add back the gap
    mouseX = appX + (
        scaledOffsetX + x * scaledGridSize + scaledGridGap * x + scaledGridGap
    )
    mouseY = appY + (
        scaledOffsetTop + y * scaledGridSize + scaledGridGap * y + scaledGridGap
    )

    if needOffset:
        # Add a small random value with gap
        # Confirm it's in the cell
        mouseX += randint(int(scaledGridGap / 2), int(scaledGridGap))
        mouseY += randint(int(scaledGridGap / 2), int(scaledGridGap))

    return [mouseX, mouseY]


def _queueTask(chessboard, taskQueue):
    row = len(chessboard)
    col = len(chessboard[0])
    TARGET_SUM = 10

    # Search surrounding level
    level = 1
    found = False
    try:
        while True:
            print(f"loop level: {level} ============================")
            # We no need the right bottom edge
            for i in range(0, row):
                for j in range(0, col - 1):
                    center = chessboard[i][j]

                    # Check it variable
                    if center == 0:
                        continue

                    # Reset found flag
                    found = False
                    nums = [center]
                    # We search items from 3 o'clock, clockwise
                    for l in range(1, level + 1):
                        if j + l < col:
                            next = chessboard[i][j + l]
                            # if next == 0:
                            #     continue

                            nums.append(next)

                            if sum(nums) == TARGET_SUM:
                                taskQueue.put(([i, j], [i, j + l]), False)
                                # empty it
                                for clean in range(0, l + 1):
                                    chessboard[i][j + clean] = 0
                                found = True
                                break
                            if sum(nums) > TARGET_SUM:
                                break

                    if found:
                        continue

                    nums = [center]
                    # Search 6 o'clock
                    for l in range(1, level + 1):
                        if i + l < row:
                            next = chessboard[i + l][j]
                            # if next == 0:
                            #     continue

                            nums.append(next)

                            if sum(nums) == TARGET_SUM:
                                taskQueue.put(([i, j], [i + l, j]), False)
                                # empty it
                                for clean in range(0, l + 1):
                                    chessboard[i + clean][j] = 0
                                break
                            if sum(nums) > TARGET_SUM:
                                break

            # wait for next loop
            level += 1
            time.sleep(1)
    except:
        pass


def _processTask(appInfo, taskQueue):
    while True:
        try:
            task = taskQueue.get(block=False)
            fromCell, toCell = task
            fromPos = _getMousePosByGridPos(appInfo, fromCell, True)
            toPos = _getMousePosByGridPos(appInfo, toCell, True)
            print("fromCell", fromCell, "toCell", toCell)
            print("Drag from %s to %s" % (fromPos, toPos))
            pyautogui.moveTo(fromPos)
            time.sleep(0.06)
            pyautogui.dragTo(toPos, duration=0.3)
        except:
            pass


def _stopProcess(signal, frame):
    print("Caught Ctrl+C, stopping processes...")
    for p in active_children():
        p.terminate()
    exit(0)


def auto(appInfo, matrix):
    chessboard = matrix

    print(chessboard)

    taskQueue = Queue()
    proc = []
    # queue 10's it
    queueTask = Process(target=_queueTask, args=(chessboard, taskQueue))
    queueTask.start()
    proc.append(queueTask)

    # bot it
    processTask = Process(
        target=_processTask,
        args=(
            appInfo,
            taskQueue,
        ),
    )
    processTask.start()
    proc.append(processTask)

    # signals for kill process
    signal.signal(signal.SIGINT, _stopProcess)

    for p in proc:
        p.join()
