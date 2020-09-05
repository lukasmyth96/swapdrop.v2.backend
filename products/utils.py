
from io import BytesIO
import os

from django.core.files import File
from PIL import Image


def resize_rotate_rename_compress_image(image, dims, quality, filename):

    if not bool(image):
        return image

    pil_img = Image.open(image)
    img_format = pil_img.format

    # Corrects image orientation
    exif = pil_img._getexif()
    orientation_key = 274  # cf ExifTags
    if exif and orientation_key in exif:
        orientation = exif[orientation_key]
        rotate_values = {
            3: Image.ROTATE_180,
            6: Image.ROTATE_270,
            8: Image.ROTATE_90
        }
        if orientation in rotate_values:
            pil_img = pil_img.transpose(rotate_values[orientation])

    pil_img = pil_img.resize(dims) 
    thumb_io = BytesIO() 
    pil_img.save(thumb_io, img_format, quality=quality)

    _, file_extension = os.path.splitext(image.name)
    new_filename = f'{filename}{file_extension}'
    image = File(thumb_io, name=new_filename) 

    return image
