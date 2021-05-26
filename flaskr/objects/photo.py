import base64
import io
import os
import uuid
from datetime import datetime

import requests
from PIL import Image, ImageOps
from PIL.ExifTags import TAGS

from flaskr.objects.sexa_to_dec import *


class Photo:
    """
    Create a python object from a jpg file. It reads the metadata and creates attributes based on the ones found.
    """
    def __init__(self, filepath):
        self.image = Image.open(filepath)
        self.exif = {}
        if self.image._getexif() is not None:
            for tag, value in self.image._getexif().items():
                if tag in TAGS:
                    self.exif[TAGS[tag]] = value

            if 'DateTime' in self.exif:
                self.datetime = datetime.strptime(self.exif['DateTime'], "%Y:%m:%d %H:%M:%S")
            if 'GPSInfo' in self.exif and len(self.exif['GPSInfo'])>1:
                self.location_coor = sexa_to_dec(self.exif['GPSInfo'][1], [float(x) for x in self.exif['GPSInfo'][2]],
                                                 self.exif['GPSInfo'][3],
                                                 [float(x) for x in self.exif['GPSInfo'][4]])
                self.location_addr = requests.get(
                    f"https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat={self.location_coor[0]}&lon={self.location_coor[1]}").json()

        self.image = ImageOps.exif_transpose(self.image)
        data = io.BytesIO()
        self.image.save(data, 'JPEG')
        self.data = base64.b64encode(data.getvalue())  # Encoded img data

