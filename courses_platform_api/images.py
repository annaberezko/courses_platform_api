from imagekit import ImageSpec
from imagekit.processors import TrimBorderColor, Adjust, ResizeToFit

from courses_platform_api.settings import THUMB_SIZE


class ImageThumbnail(ImageSpec):
    processors = [ResizeToFit(width=THUMB_SIZE, height=THUMB_SIZE),
                  TrimBorderColor(),
                  Adjust(contrast=1.1, sharpness=2.0)]
    format = 'JPEG'
    options = {'quality': 95}
