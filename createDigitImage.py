import cv2
import numpy as np
import random
import os
import random

# Parameters for drawing the digits
image_size = (28, 28)  # Image size (height, width)
fonts = [
    cv2.FONT_HERSHEY_SIMPLEX,
    cv2.FONT_HERSHEY_PLAIN,
    cv2.FONT_HERSHEY_DUPLEX,
    cv2.FONT_HERSHEY_COMPLEX,
    cv2.FONT_HERSHEY_TRIPLEX,
    cv2.FONT_HERSHEY_COMPLEX_SMALL,
    cv2.FONT_HERSHEY_SCRIPT_SIMPLEX,
    cv2.FONT_HERSHEY_SCRIPT_COMPLEX
]
font = cv2.FONT_HERSHEY_SIMPLEX
font_scale = (1, 10)
angle = (-5, 5)
thickness = 2
color = (255, 255, 255)  # White color for the digits
shift = 2


def create_random_digit_image():
    # we had a lot of issues with ones, so we add more of those
    digit = random.choice([0,1,2,3,4,5,6,7,8,9,1,1])

    font = random.choice(fonts)
    font_scale_digit = random.randint(font_scale[0], font_scale[1])
    text_size = cv2.getTextSize(str(digit), font, font_scale_digit, thickness)[0]
    image_size_source = (max(text_size)*5//4, max(text_size)*5//4)
    text_x = (image_size_source[1] - text_size[0] - random.randint(-shift, shift)) // 2
    text_y = (image_size_source[0] + text_size[1] - random.randint(-shift, shift)) // 2
    image = np.zeros(image_size_source, dtype=np.uint8)
    cv2.putText(image, str(digit), (text_x, text_y), font, font_scale_digit, color, thickness)

    rotation_matrix = cv2.getRotationMatrix2D((image_size_source[0]/2, image_size_source[1]/2), random.randint(angle[0], angle[1]), 1)
    rotated_image = cv2.warpAffine(image, rotation_matrix, (image.shape[1], image.shape[0]))
    digit_image_resized = cv2.resize(rotated_image, (28, 28), interpolation=cv2.INTER_AREA)
    digit_image = cv2.GaussianBlur(digit_image_resized, (5, 5), 0)
    digit_image = cv2.normalize(digit_image, None, 0, 255, cv2.NORM_MINMAX)
    return (digit_image, digit)