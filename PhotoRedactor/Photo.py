from PIL import Image


class Photo():
    def __init__(self, file_name):
        self.photo = Image.open(file_name)
        self.width = self.photo.width
        self.height = self.photo.height

    def paste(self, photo, x, y):
        self.photo.paste(photo.photo.resize((self.width - x * 2, self.height - y * 2)), (x, y))