from nursery.modules.auto import auto
from nursery.modules.ocr import ocr
from nursery.modules.shot import appShot


def start():
    appInfo = appShot()
    chessboard = ocr()
    if chessboard:
        auto(appInfo, chessboard)
    else:
        print("No chessboard found")
