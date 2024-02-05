import subprocess
from PIL import Image


class ImageGrabberFactory(object):
    @staticmethod
    def get_image_grabber(dummy_file=None):
        if dummy_file is not None:
            return DummyImageGrabber(file=dummy_file)
        else:
            return ImageGrabber()


class DummyImageGrabber(object):
    def __init__(self, file):
        self.file = file

    def grab_image(self, width, height, output_filename):
        image = Image.open(self.file)
        new_image = image.resize((width, height))
        new_image.save(output_filename)

        return True


class ImageGrabber(object):
    COMMAND = "libcamera-still"

    @staticmethod
    def grab_image(width, height, output_filename):
        run_pic = subprocess.run([
            ImageGrabber.COMMAND,
            "-t",
            "1",
            "--immediate",
            "-n",
            "1",
            "--width",
            "{}".format(width),
            "--height",
            "{}".format(height),
            "-o",
            "{}".format(output_filename)
        ])

        return run_pic.returncode == 0
