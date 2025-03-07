import cv2
import numpy as np
import random
import os
from PIL import Image, ImageDraw, ImageFont

data_dir = "."

# Parameters for drawing the digits
font_files = []
image_size = (28, 28)  # Image size (height, width)
font_scale_cv2 = (1, 2)
font_size_PIL = (10, 20)
angle = (-5, 5)
thickness = 2
color = (255, 255, 255)  # White color for the digits
shift = 2
blurs = [None, (3,3), (5,5)]

fonts_cv = [
    cv2.FONT_HERSHEY_SIMPLEX,
    cv2.FONT_HERSHEY_PLAIN,
    cv2.FONT_HERSHEY_DUPLEX,
    cv2.FONT_HERSHEY_COMPLEX,
    cv2.FONT_HERSHEY_TRIPLEX,
    cv2.FONT_HERSHEY_COMPLEX_SMALL,
    cv2.FONT_HERSHEY_SCRIPT_SIMPLEX,
    cv2.FONT_HERSHEY_SCRIPT_COMPLEX
]

def write_test_images(directory, images):
    empty_test_dir(directory)
    for (file_name, image) in images:
        cv2.imwrite(os.path.join(directory, file_name), image)

def empty_test_dir(directory):
    if os.path.exists(directory):
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
    os.makedirs(directory, exist_ok=True)   


def read_fonts_PIL():
    font_folder = "Fonts"
    font_folder = "FontsWindows"
    global font_files
    if font_files is None or len(font_files) == 0:
        font_files = []
        for dirpath, dirnames, filenames in os.walk(f"{data_dir}/{font_folder}/"):
            for filename in filenames:
                if (filename.endswith("tf")):   # todo :D
                    font_files.append(os.path.join(dirpath, filename))

def create_random_digit_image():
    #if (random.random() > .5):
    #    return create_random_digit_image_CV2()
    #else:
        return create_random_digit_image_PIL()

def create_random_digit_image_CV2():
    # we had a lot of issues with ones, so we add more of those
    digit = random.choice([0,1,2,3,4,5,6,7,8,9,1,1])

    font = random.choice(fonts_cv)
    font_scale_digit = random.randint(font_scale_cv2[0], font_scale_cv2[1])
    text_size = cv2.getTextSize(str(digit), font, font_scale_digit, thickness)[0]
    print(text_size)
    image_size_source = (max(text_size)*5//4, max(text_size)*5//4)
    text_x = (image_size_source[1] - text_size[0] - random.randint(-shift, shift)) // 2
    text_y = (image_size_source[0] + text_size[1] - random.randint(-shift, shift)) // 2
    digit_image = np.zeros(image_size_source, dtype=np.uint8)
    cv2.putText(digit_image, str(digit), (text_x, text_y), font, font_scale_digit, color, thickness)

    rotation_matrix = cv2.getRotationMatrix2D((image_size_source[0]/2, image_size_source[1]/2), random.randint(angle[0], angle[1]), 1)
    digit_image = cv2.warpAffine(digit_image, rotation_matrix, (digit_image.shape[1], digit_image.shape[0]))
    digit_image = cv2.resize(digit_image, (28, 28), interpolation=cv2.INTER_AREA)
    digit_image = cv2.GaussianBlur(digit_image, (5, 5), 0)
    digit_image = cv2.normalize(digit_image, None, 0, 1, cv2.NORM_MINMAX)
    return (digit_image, digit)    

def create_random_digit_image_PIL(fixed_font_file = None):
    read_fonts_PIL()
    # we had a lot of issues with ones, so we add more of those
    digit = random.choice([0,1,2,3,4,5,6,7,8,9,1,1])

    font_file = fixed_font_file if fixed_font_file is not None else random.choice(font_files)
    font_size = random.randint(font_size_PIL[0], font_size_PIL[1])
    font = ImageFont.truetype(font_file, font_size)

    img = Image.new('RGB', (0, 0), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    text_size_PIL = draw.textbbox((0, 0), str(digit), font)
    (w, h) = (text_size_PIL[2], text_size_PIL[3])
    text_size = max(w, h)*5//4
    img = Image.new('RGB', (text_size, text_size), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    text_x = (text_size - w - random.randint(-shift, shift)) // 2
    text_y = (text_size - h - random.randint(-shift, shift)) // 2
    draw.text((text_x, text_y), str(digit), font=font, fill=(0, 0, 0))
    #image = np.zeros(image_size_source, dtype=np.uint8)
    #cv2.putText(image, str(digit), (text_x, text_y), font, font_scale_digit, color, thickness)
    # todo naming image vs img etc
    #draw.text((50, 50), "HEY there!", font=font, fill=(0, 0, 0))
    digit_image = np.array(img)
    digit_image = cv2.cvtColor(digit_image, cv2.COLOR_RGB2BGR)

    rotation_matrix = cv2.getRotationMatrix2D((w/2, h/2), random.randint(angle[0], angle[1]), 1)
    digit_image = cv2.warpAffine(digit_image, rotation_matrix, (digit_image.shape[1], digit_image.shape[0]), borderValue=(255,255,255))
    digit_image = cv2.resize(digit_image, (28, 28), interpolation=cv2.INTER_AREA)
    blur = random.choice(blurs)
    if blur != None:
        digit_image = cv2.GaussianBlur(digit_image, blur, 0)
    digit_image = 1-cv2.normalize(digit_image, None, 0, 1, cv2.NORM_MINMAX)
    digit_image = cv2.cvtColor(digit_image, cv2.COLOR_BGR2GRAY)

    font_name = os.path.splitext(os.path.basename(font_file))[0]
    return (digit_image, digit, font_name)

        
if __name__ == "__main__":
    output_dir = "digits_test_set"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)


    # Generate a test set of 100 images with random digits
    num_images = 10

    i = 0

    images = []
    read_fonts_PIL()
    for (i, font_file) in enumerate(font_files):
        (digit_image, digit, font_name) = create_random_digit_image_PIL(font_file[2:])
        images.append((f"PIL_font_{font_name}.png", digit_image*255))

    for i in range(num_images):
        (digit_image, digit) = create_random_digit_image_CV2()
        images.append((f"cv2_digit_{i}_{digit}.png", digit_image*255))
    
    write_test_images("create_digits_data", images)
