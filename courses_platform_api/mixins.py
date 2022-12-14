import os
import random
import string
from datetime import date


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


class Datemixin:
    def add_month(current_date: date, month: int) -> date:
        added_month = current_date.month + month
        if added_month > 12:
            new_month = added_month % 12
        else:
            new_month = added_month
        year = 0
        while (added_month > 12):
            year += 1
            added_month -= 12
        new_date = date(current_date.year + year, new_month, current_date.day)
        return new_date
