import os
import sys
from datetime import datetime

from snapper_config import SnapperConfigOptions, SnapperConfigParseResponse
from src.annotation_grabber import AnnotationGrabber, ReadingDetails
from src.image_annotator import ImageAnnotator
from src.image_grabber import ImageGrabber

CONFIG_FILE = "autobloomer_snapper_cfg.json"
SCRIPT_PATH = os.path.dirname(os.path.abspath(__file__))
IMAGE_WIDTH = 3840
IMAGE_HEIGHT = 2160


# Application entry point
def main():
    # Read config
    config_parser = SnapperConfigOptions(SCRIPT_PATH)
    config_response = config_parser.read_config("autobloomer_snapper_cfg.json")
    if config_response != SnapperConfigParseResponse.PARSE_OK:
        print("Could not obtain snapper config: {}".format(config_response))
        sys.exit()

    # Get the filename for the annotated image
    now = datetime.now()
    timestamp_string = now.strftime("%Y%m%d%%H%M%s")
    output_filename = "{}.jpg".format(timestamp_string)

    # Grab the image
    if not ImageGrabber.grab_image(
        width=IMAGE_WIDTH,
        height=IMAGE_HEIGHT,
        output_filename=output_filename
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
    annotated_image = ImageAnnotator.annotate_image(
        image_file=output_filename,
        annotation_details=annotation_details
    )

    annotated_image.save("assets/output.jpg")


if __name__ == "__main__":
    sys.exit(main())
