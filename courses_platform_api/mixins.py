import random
import string


class GeneratorMixin:
    @staticmethod
    def slug(pk, length=15):
        chars = string.ascii_letters + "-" + string.digits
        rnd = random.SystemRandom()
        return ''.join(rnd.choice(chars) for _ in range(length)) + f"-{pk}"
