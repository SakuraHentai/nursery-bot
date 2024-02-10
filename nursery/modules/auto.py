import signal
import time
from multiprocessing import Process, Queue, active_children

import numpy as np
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
    try:
        while True:
            # The chessboard is 16x10
            # So, if the level reach it, we stop
            if surroundingLevel > 16:
                break

            # We no need the right bottom edge
            for i in range(0, row):
                for j in range(0, col):
                    # Check it variable
                    if chessboard[i][j] == 0:
                        continue

                    # Search for a rectangle
                    for column in range(0, surroundingLevel + 1):
                        # Record whether found is used to jump out of the loop
                        found = False
                        for rowI in range(0, surroundingLevel + 1):
                            if j + column < col and i + rowI < row:
                                # Skip the 1*1 rectangle
                                if rowI == 0 and column == 0:
                                    continue
                                rr = i + rowI
                                cc = j + column
                                # Rectangular numpy array
                                children = chessboard[i:rr+1, j:cc+1]
                                sum = np.sum(children)

                                if sum == TARGET_SUM:
                                    target = ([i, j], [rr, cc])
                                    print('Find the target:', target, ' Rectangle: ', children)
                                    # Clean the rectangular
                                    for cR in range(i, rr + 1):
                                        for rR in range(j, cc + 1):
                                            chessboard[cR][rR] = 0
                                    taskQueue.put(target, False)
                                    found = True
                                    break
                                if sum > TARGET_SUM:
                                    break

                        if found:
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
