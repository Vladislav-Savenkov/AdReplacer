from PIL import Image


def main():
    filename1 = "test_photo1.jpg"
    filename2 = "test_photo2.jpg"
    with Image.open(filename1) as cat:
        cat.load()
    with Image.open(filename2) as gosl:
        gosl.load()
    dx, dy = 80, 50
    c_w, c_h, g_w, g_h = cat.width, cat.height, gosl.width, gosl.height
    gosl.paste(cat.resize((g_w - dx * 2, g_h - dy * 2)), (dx, dy))
    gosl.show()


if __name__ == "__main__":
    main()