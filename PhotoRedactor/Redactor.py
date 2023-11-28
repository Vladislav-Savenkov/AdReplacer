from PIL import Image
from Photo import Photo


def main():
    photo1 = Photo("test_photo1.jpg")
    photo2 = Photo("test_photo2.jpg")
    dx, dy = 100, 100
    photo1.paste(photo2, dx, dy)
    photo1.photo.show()


if __name__ == "__main__":
    main()