import cv2
import numpy as np
import pytesseract

import nursery.modules.config as config


def ocr():
    # Read the image
    img = cv2.imread(config.APP_SHOT_FILENAME)

    # Get the dimensions of the image
    height, width, _ = img.shape

    # Crop the image
    scale = width / config.ORIGIN_WIDTH

    img = img[
        int(config.OFFSET_TOP * scale) : int(height - config.OFFSET_BOTTOM * scale),
        int(config.OFFSET_X * scale) : int(width - config.OFFSET_X * scale),
    ]

    # Convert the image to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Make the image only have black and white
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # Invert the binary image
    thresh = cv2.bitwise_not(thresh)
    cv2.imwrite("debug.png", thresh)

    # Find contours in the inverted binary image
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Grab all numbers
    numbers = []

    # Iterate over each contour and filter out the ones that are not rectangular in shape
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)

        # Check it's a cell
        cellMinSize = config.GRID_SIZE * 0.9 * scale
        cellMaxSize = config.GRID_SIZE * 1.1 * scale
        if w > cellMinSize and h > cellMinSize and w < cellMaxSize and h < cellMaxSize:
            # Crop the rectangular contours from the original image
            number = img[y : y + h, x : x + w]

            if number.size > 0:
                x, y, w, h = 0, 0, number.shape[1], number.shape[0]

                # Center the number
                offset = int(((config.GRID_SIZE - 18) / 2) * scale)
                number = number[
                    y + offset : y + h - offset, x + offset : x + w - offset
                ]
                numbers.append(number)

    # Concat into one img
    numbers = cv2.hconcat(numbers)

    # Ocr it
    numbers = pytesseract.image_to_string(
        numbers, config='--psm 6 digits -c tessedit_char_whitelist="123456789"'
    )

    try:
        # Convert it into 2d matrix
        numbers = np.array([int(i) for i in list(numbers.strip())])
        numbers = np.flip(numbers)
        matrix = np.reshape(numbers, (16, 10))
    except:
        print("OCR seems to have failed")
        return

    return matrix
