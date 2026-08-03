from functools import reduce
import random

import ddddocr
import cv2
import numpy as np
from matplotlib import pyplot as plt
from PIL import Image
import io
import time

slide_detector = ddddocr.DdddOcr(det=False, ocr=False)

def do_captcha(big_image: bytes, small_image: bytes):
    position = slide_detector.slide_match(small_image, big_image)
    x1, y1, x2, y2 = position["target"]

    big_image_img = Image.open(io.BytesIO(big_image))
    x_off = x1
    x_normalized = x_off * (280/big_image_img.width)

    generated_track = gen_track(x_normalized)
    total_time = reduce(lambda x,y: x+y["c"],generated_track["tracks"], 0)
    time.sleep(total_time/1000)
    return generated_track

def gen_track(moved_offset: int):
    """Generate a slightly randomized, human-like slider track."""

    sample_count = random.randint(19, 22)
    tracks = []
    previous_x = 0

    for index in range(1, sample_count + 1):
        progress = index / sample_count

        # Smoothstep's velocity starts at zero, peaks in the middle, and
        # returns to zero, which gives the track a slow-fast-slow shape.
        eased_progress = progress * progress * (3 - 2 * progress)
        if index < sample_count:
            eased_progress += random.uniform(-0.004, 0.004)
            x = round(moved_offset * eased_progress)
            x = min(moved_offset, max(previous_x, x))
        else:
            # Avoid any rounding error on the final sample.
            x = moved_offset

        if index <= 2:
            interval = random.randint(45, 85)
        elif index == sample_count:
            interval = random.randint(400, 700)
        elif index >= sample_count - 2:
            interval = random.randint(70, 160)
        else:
            interval = random.randint(28, 38)

        tracks.append({
            "a": x,
            "b": 0 if index == sample_count else random.choice((-1, 0, 0, 0, 1)),
            "c": interval,
        })
        previous_x = x

    return {
        "canvasLength": 280,
        "moveLength": moved_offset,
        # a: x, b: y, c: milliseconds since the previous sample
        "tracks": tracks,
    }

if __name__=="__main__":
    import json
    import base64

    with open("./captcha_test.json", "r") as captcha_response:
        resp = json.loads(captcha_response.read())
    # smallImage, bigImage, tagWidth, yHeight=0

    small_image = base64.b64decode(resp['smallImage'])
    big_image = base64.b64decode(resp['bigImage'])

    captcha_result = do_captcha(big_image, small_image)
