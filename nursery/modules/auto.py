import signal
import time
from multiprocessing import Process, Queue, active_children

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
        mouseX += int(scaledGridSize / 2)
        mouseY += int(scaledGridSize / 2)

    return [mouseX, mouseY]


def _queueTask(chessboard, taskQueue):
    row = len(chessboard)
    col = len(chessboard[0])
    TARGET_SUM = 10

    # Search surrounding level
    surroundingLevel = 1
    found = False
    try:
        while True:
            # The chessboard is 16x10
            # So, if the level reach it, we stop
            if surroundingLevel > 16:
                break

            # We no need the right bottom edge
            for i in range(0, row):
                for j in range(0, col):
                    center = chessboard[i][j]

                    # Check it variable
                    if center == 0:
                        continue

                    # Reset found flag
                    found = False
                    nums = [center]
                    # We search items from 3 o'clock, clockwise
                    for level in range(1, surroundingLevel + 1):
                        if j + level < col:
                            next = chessboard[i][j + level]
                            nums.append(next)

                            if sum(nums) == TARGET_SUM:
                                taskQueue.put(([i, j], [i, j + level]), False)

                                # Empty it
                                for clean in range(0, level + 1):
                                    chessboard[i][j + clean] = 0
                                found = True
                                break
                            if sum(nums) > TARGET_SUM:
                                break

                    if found:
                        continue

                    nums = [center]
                    # Search 6 o'clock
                    for level in range(1, surroundingLevel + 1):
                        if i + level < row:
                            next = chessboard[i + level][j]
                            nums.append(next)

                            if sum(nums) == TARGET_SUM:
                                taskQueue.put(([i, j], [i + level, j]), False)

                                # Empty it
                                for clean in range(0, level + 1):
                                    chessboard[i + clean][j] = 0
                                break
                            if sum(nums) > TARGET_SUM:
                                break

            # Wait for next loop
            surroundingLevel += 1
            time.sleep(1)
    except:  # noqa: E722
        pass


def _processTask(appInfo, taskQueue):
    # B'z the task data is much more faster then the gui
    # So it just works, lol
    guiStarted = False
    while True:
        try:
            task = taskQueue.get(block=False)
            guiStarted = True

            fromCell, toCell = task
            fromPos = _getMousePosByGridPos(appInfo, fromCell)
            # Add offset to make sure across the cell
            toPos = _getMousePosByGridPos(appInfo, toCell, True)

            print("fromCell", fromCell, "toCell", toCell)
            print("Drag from %s to %s" % (fromPos, toPos))
            pyautogui.moveTo(fromPos)
            time.sleep(0.06)
            pyautogui.dragTo(toPos, duration=0.3)
        except:  # noqa: E722
            # Done all tasks.
            if guiStarted:
                break


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

    # Queue 10's
    queueTask = Process(target=_queueTask, args=(chessboard, taskQueue))
    queueTask.start()
    proc.append(queueTask)

    # Bot it
    processTask = Process(
        target=_processTask,
        args=(
            appInfo,
            taskQueue,
        ),
    )
    processTask.start()
    proc.append(processTask)

    # Signals for Ctl-C
    signal.signal(signal.SIGINT, _stopProcess)

    for p in proc:
        p.join()
