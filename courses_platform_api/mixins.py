import os
import random
import string


class GeneratorMixin:
    @staticmethod
    def slug(pk, length=15):
        chars = string.ascii_letters + "-" + string.digits
        rnd = random.SystemRandom()
        return ''.join(rnd.choice(chars) for _ in range(length)) + f"-{pk}"


class ImageMixin:
    @staticmethod
    def remove(image):
        if os.path.isfile(image.path):
            os.remove(image.path)
