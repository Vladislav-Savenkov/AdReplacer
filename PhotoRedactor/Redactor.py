from typing import BinaryIO
from PIL import Image


def paste(photo1: BinaryIO, photo2: BinaryIO, x: int, y: int):
    '''
    Paste photo2 in photo1 by coords of left-up point
    '''
    image1, image2 = Image.open(photo1), Image.open(photo2)
    image1.paste(image2, (x, y))
    return image1


def paste_resize(photo1: BinaryIO, photo2: BinaryIO,
                 x_start: int, y_start: int, x_end: int, y_end: int):
    '''
    Paste photo2 in photo1 by coords of left-up and right-down points
    '''
    image1, image2 = Image.open(photo1), Image.open(photo2)
    image1.paste(image2.resize((x_end - x_start, y_end - y_start)), (x_start, y_start))
    return image1


def main():
    file1 = open("test_photo1.jpg", "rb")
    file2 = open("test_photo2.jpg", "rb")
    res = paste_resize(file1, file2, 100, 100, 200, 200)
    res.show()




if __name__ == "__main__":
    main()