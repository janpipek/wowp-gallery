import os

from PIL import Image

from wowp.components import Actor


class ThumbnailCreator(Actor):
    SIZE = 1

    def __init__(self):
        super(ThumbnailCreator, self).__init__(name="Thumbnail creator")
        # self.output_path = os.path.abspath(output_path)
        # self.inports.append("thumbnail_size")
        self.inports.append("infile")
        self.outports.append("outfile")

        # self.outports.append("image_out")

    def get_run_args(self):
        args = (self.inports["infile"].pop(),)  # , self.inport["thumbnail_size"].pop())
        kwargs = {} # "output_path": self.output_path}
        return args, kwargs

    @classmethod
    def run(cls, *args, **kwargs):
        infile = args[0]
        # size = args[1]
        # self.inports["thumbnail_size"].default = size   # Cache for later use
        outfile = os.path.splitext(infile)[0] + ".thumb.jpg"
        cls.create_thumbnail(infile, outfile)
        return {"outfile": outfile}

    @classmethod
    def create_thumbnail(cls, infile, outfile, **kwargs):
        if os.path.isfile(outfile):
            print("Not creating thumbnail {0}...".format(outfile))
            return  # Unless forced
        os.makedirs(os.path.dirname(outfile), exist_ok=True)
        print("Creating thumbnail {0}...".format(outfile))

        size = kwargs.get("size", cls.SIZE)
        img = Image.open(infile)

        ratio = float(size) / min(img.width, img.height)
        width = max(int(img.width * ratio), size)
        height = max(int(img.height * ratio), size)
        left = int((width - size) / 2)
        top = int((height - size) / 2)
        img = img.resize((width, height), Image.ANTIALIAS)
        img = img.crop((left, top, left + size, top + size))
        img.save(outfile)
