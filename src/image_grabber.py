import subprocess


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
