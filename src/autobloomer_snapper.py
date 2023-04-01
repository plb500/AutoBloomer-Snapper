import argparse
import os
import sys
from datetime import datetime

from snapper_config import SnapperConfigOptions, SnapperConfigParseResponse
from annotation_grabber import AnnotationGrabber
from image_annotator import ImageAnnotator
from image_grabber import ImageGrabber

CONFIG_FILE = "../autobloomer_snapper_cfg.json"
SCRIPT_PATH = os.path.dirname(os.path.abspath(__file__))
IMAGE_WIDTH = 3840
IMAGE_HEIGHT = 2160


# Application entry point
def main():
    # Parse arguments
    parser = argparse.ArgumentParser(description="AutoBloomer Snapper")
    parser.add_argument("-c", "--config-file", default=CONFIG_FILE, dest="snapper_config_file")
    args = parser.parse_args()

    # Read config
    config_parser = SnapperConfigOptions(None)
    config_response = config_parser.read_config(args.snapper_config_file)
    if config_response != SnapperConfigParseResponse.PARSE_OK:
        print("Could not obtain snapper config: {}".format(config_response))
        sys.exit()

    # Get the filename for the annotated image
    now = datetime.now()
    timestamp_string = now.strftime("%Y%m%d%H%M%s")
    output_filename = "{}.jpg".format(timestamp_string)
    image_path = os.path.join(config_parser.image_destination, output_filename)

    # Grab the image
    if not ImageGrabber.grab_image(
        width=IMAGE_WIDTH,
        height=IMAGE_HEIGHT,
        output_filename=image_path
    ):
        print("Could not grab image")
        sys.exit()

    annotation_grabber = AnnotationGrabber(
        host=config_parser.host_name,
        port=config_parser.port_number,
        passphrase=config_parser.passphrase
    )

    annotation_details = annotation_grabber.grab_annotations(
        config_parser.grow_system_id,
        reading_details=config_parser.sensor_readings
    )

    if annotation_details is not None:
        annotated_image = ImageAnnotator.annotate_image(
            image_file=output_filename,
            annotation_details=annotation_details
        )

        annotated_image.save(image_path)


if __name__ == "__main__":
    sys.exit(main())
