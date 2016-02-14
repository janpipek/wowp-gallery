from wowp.components import Actor
import os
import jinja2
import codecs


class AlbumPageCreator(Actor):
    SIZE = 256

    def __init__(self, output_path):
        super(AlbumPageCreator, self).__init__()
        self.output_path = os.path.abspath(output_path)
        self.inports.append("images")

    def get_run_args(self):
        args = (self.inports["images"].pop(),)
        kwargs = {"output_path": self.output_path}
        return args, kwargs

    @classmethod
    def run(cls, *args, **kwargs):
        images = args[0]
        outfile = os.path.join(kwargs.get("output_path"), "index.html")
        cls.create_page(images, outfile)
        return { }

    @classmethod
    def create_page(cls, images, outfile, **kwargs):
        basedir = os.path.dirname(os.path.abspath(__file__))

        jinja_loader = jinja2.FileSystemLoader(os.path.join(basedir, "resources"))
        env = jinja2.Environment(loader=jinja_loader)

        template = env.get_template("index.html")

        with codecs.open(outfile, "w", encoding="utf-8") as fout:
            fout.write(template.render(images=images))



