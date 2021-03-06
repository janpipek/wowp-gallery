import logging
import os

from PIL import Image, ImageEnhance

from wowp.components import Actor

ENABLE_SHARPEN = True
SHARPNESS_FACTOR = 1.6  # 1.0=original, 0.0=blurred, 2.0=max.sharpness
JPEG_QUALITY = 92


class ImageResizer(Actor):
    def __init__(self):
        super(ImageResizer, self).__init__()
        self.inports.append("image_in")
        self.inports.append("image_size")
        self.inports.append("output_path")
        self.outports.append("out_file")

    def get_run_args(self):
        max_size = self.inports["image_size"].pop()
        return (
            (self.inports["image_in"].pop(),),
            {
                "output_path": self.inports["output_path"].pop(),
                "max_width": max_size,
                "max_height": max_size,
            },
        )

    @classmethod
    def run(cls, *args, **kwargs):
        image = args[0]
        max_width = kwargs.get("max_width")
        max_height = kwargs.get("max_height")
        infile = image.path
        filename = image.basename + ".jpg"
        outfile = os.path.join(kwargs.get("output_path"), filename)
        cls.resize_image(
            infile, outfile, max_width=max_width, max_height=max_height, orientation=image.exif_orientation
        )
        return {"out_file": outfile}

    @classmethod
    def resize_image(
        cls,
        infile,
        outfile, *,
        max_width: int,
        max_height: int,
        preserve_exif: bool = True,
        quality=JPEG_QUALITY,
        orientation=1,
        **kwargs
    ):
        if os.path.isfile(outfile):
            logging.debug(f"Not resizing image {outfile}...")
            return  # Unless forced
        os.makedirs(os.path.dirname(outfile), exist_ok=True)
        logging.info(f"Resizing image {outfile}...")

        img = Image.open(infile)

        exif = None

        if preserve_exif:
            try:
                exif = img.info["exif"]
            except KeyError:
                pass

        if orientation == 3:
            img = img.transpose(Image.ROTATE_180)
        elif orientation == 6:
            img = img.transpose(Image.ROTATE_270)
        elif orientation == 8:
            img = img.transpose(Image.ROTATE_90)

        scale = 1.0
        if img.width > max_width:
            scale = max_width / img.width
        if img.height > max_height:
            scale = min(scale, max_height / img.height)

        if scale < 1.0:
            width = int(scale * img.width)
            height = int(scale * img.height)
            resized = img.resize((width, height), Image.BICUBIC)
        else:
            resized = img

        save_kwargs = {"quality": quality}

        if ENABLE_SHARPEN:
            enhancer = ImageEnhance.Sharpness(resized)
            resized = enhancer.enhance(SHARPNESS_FACTOR)

        if exif:
            save_kwargs["exif"] = exif

        resized.save(outfile, **save_kwargs)
