from collections import namedtuple

from PIL import ImageFont, Image, ImageDraw

SensorDataStrings = namedtuple("SensorDataStrings", "label value")


class AnnotationDetails(object):
    def __init__(self, grow_system_name, age, sensor_data_strings):
        self.grow_system_name = grow_system_name
        self.age = age
        self.sensor_data_strings = sensor_data_strings

    def longest_sensor_data_label_length(self):
        if len(self.sensor_data_strings) == 0:
            return 0

        return max(self.sensor_data_strings, key=lambda x: len(x.label)).label

    def longest_sensor_data_value_length(self):
        if len(self.sensor_data_strings) == 0:
            return 0

        return max(self.sensor_data_strings, key=lambda x: len(x.value)).value


SOURCE_FILE = "assets/plants.jpg"
details = AnnotationDetails(
    grow_system_name="Harvest Chamber",
    age=45,
    sensor_data_strings=[
        SensorDataStrings("Carbon Dioxide (PPM):", " 440"),
        SensorDataStrings("Temperature (°C):", "29.1"),
        SensorDataStrings("Humidity (%):", "46.3"),
        SensorDataStrings("Soil Moisture (%):", "60.4")
    ]
)

# Fonts
SENSOR_DATA_FONT_FILE = "assets/Sono-Medium.ttf"
AGE_FONT_FILE = "assets/highland-gothic.ttf"
GROW_SYSTEM_NAME_FONT_FILE = "assets/highland-gothic.ttf"

# Colors
GROW_SYSTEM_NAME_COLOR = (137, 255, 142, 255)
GROW_SYSTEM_NAME_STROKE_COLOR = (12, 33, 13, 255)
SENSOR_VALUE_COLOR = (0, 208, 255, 255)
SENSOR_LABEL_COLOR = (191, 243, 255, 255)
SENSOR_BACKGROUND_COLOR = (0, 0, 0, 150)
SENSOR_OUTLINE_COLOR = (255, 255, 255, 255)
AGE_COLOR = (247, 255, 158, 255)
AGE_STROKE_COLOR = (32, 33, 14, 255)

# Image ratios
IMAGE_HEIGHT_TO_GROW_SYSTEM_NAME_RATIO = 0.03
IMAGE_HEIGHT_TO_SENSOR_DATA_RATIO = 0.0225
IMAGE_HEIGHT_TO_AGE_RATIO = 0.025
IMAGE_HEIGHT_TO_SENSOR_PADDING_RATIO = 0.01
IMAGE_WIDTH_TO_SENSOR_BOX_RADIUS_RATIO = 0.01


def antialiased_rounded_rect(width, height, radius, stroke, stroke_width, fill):
    scale_factor = 8

    im = Image.new("RGBA", ((scale_factor * width), (scale_factor * height)), (0, 0, 0, 0))
    draw = ImageDraw.Draw(im, "RGBA")
    draw.rounded_rectangle(
        xy=(
            0,
            0,
            im.width,
            im.height
        ),
        radius=(radius * scale_factor),
        outline=stroke,
        width=(stroke_width * scale_factor),
        fill=fill
    )
    return im.resize((width, height), Image.LANCZOS)


def annotate_grow_system_name_and_age(name, age, dst_image):
    grow_system_name_font_height = int(dst_image.height * IMAGE_HEIGHT_TO_GROW_SYSTEM_NAME_RATIO)
    grow_system_name_font = ImageFont.truetype(GROW_SYSTEM_NAME_FONT_FILE, grow_system_name_font_height)

    age_font_height = int(dst_image.height * IMAGE_HEIGHT_TO_AGE_RATIO)
    age_font = ImageFont.truetype(AGE_FONT_FILE, age_font_height)
    age_string = "Day {}".format(age)

    padding = (grow_system_name_font_height / 2)

    # Get a drawing context for our image
    draw = ImageDraw.Draw(dst_image)

    # Calculate draw positions
    age_bb = age_font.getbbox(age_string, anchor="ls")
    age_height = age_bb[3] - age_bb[1]
    age_text_xy = (
        padding,
        dst_image.height - padding - age_height
    )

    grow_system_name_bb = grow_system_name_font.getbbox(name, anchor="lt")
    grow_system_name_height = grow_system_name_bb[3] - grow_system_name_bb[1]

    grow_system_name_xy = (
        padding,
        age_text_xy[1] - padding - grow_system_name_height
    )

    draw.text(
        xy=grow_system_name_xy,
        text=name,
        fill=GROW_SYSTEM_NAME_COLOR,
        stroke_fill=GROW_SYSTEM_NAME_STROKE_COLOR,
        stroke_width=int(grow_system_name_font_height / 5),
        font=grow_system_name_font,
        anchor="lt"
    )

    # Draw
    draw = ImageDraw.Draw(dst_image)
    draw.text(
        xy=age_text_xy,
        text=age_string,
        fill=AGE_COLOR,
        font=age_font,
        stroke_width=int(age_font_height / 5),
        stroke_fill=AGE_STROKE_COLOR,
        anchor="lt"
    )


def annotate_grow_system_name(name, dst_image):
    grow_system_name_font_height = int(dst_image.height * IMAGE_HEIGHT_TO_GROW_SYSTEM_NAME_RATIO)
    grow_system_name_font = ImageFont.truetype(GROW_SYSTEM_NAME_FONT_FILE, grow_system_name_font_height)

    # Get a drawing context for our image
    draw = ImageDraw.Draw(dst_image)

    # Calculate draw positions
    grow_system_name_bb = grow_system_name_font.getbbox(name, anchor="lt")
    grow_system_name_height = grow_system_name_bb[3] - grow_system_name_bb[1]
    grow_system_name_padding = (grow_system_name_height / 2)

    grow_system_name_left = grow_system_name_padding
    grow_system_name_top = (dst_image.height - grow_system_name_padding - grow_system_name_height)

    draw.text(
        xy=(grow_system_name_left, grow_system_name_top),
        text=name,
        fill=GROW_SYSTEM_NAME_COLOR,
        stroke_fill=(12, 33, 13, 255),
        stroke_width=6,
        font=grow_system_name_font,
        anchor="lt"
    )


def annotate_sensor_data(sensor_data, dst_image):
    DataEntryDrawPos = namedtuple("DataEntryDrawPos", "label_pos value_pos")

    if len(sensor_data) == 0:
        return

    sensor_data_font_height = int(dst_image.height * IMAGE_HEIGHT_TO_SENSOR_DATA_RATIO)
    sensor_data_font = ImageFont.truetype(SENSOR_DATA_FONT_FILE, sensor_data_font_height)
    box_padding = int(dst_image.height * IMAGE_HEIGHT_TO_SENSOR_PADDING_RATIO)

    # Calculate draw positions
    num_entries = len(sensor_data)
    box_interior_padding = sensor_data_font_height
    entry_spacing_vertical = (sensor_data_font_height / 2)
    label_value_spacing = sensor_data_font.getlength(" ")
    longest_label = max(sensor_data, key=lambda x: len(x.label)).label
    longest_value = max(sensor_data, key=lambda x: len(x.value)).value
    label_bb = sensor_data_font.getbbox(longest_label, anchor="lt")
    value_bb = sensor_data_font.getbbox(longest_value, anchor="lt")
    longest_label_width = (label_bb[2] - label_bb[0])
    longest_value_width = (value_bb[2] - value_bb[0])

    sensor_data_background_width = (3 * label_value_spacing) + longest_label_width + longest_value_width
    sensor_data_background_height = ((num_entries + 1) * entry_spacing_vertical)

    sensor_data_draw_positions = []
    x_pos = int(dst_image.width - sensor_data_background_width - box_padding)
    entry_y_pos = entry_spacing_vertical
    for count, entry in enumerate(sensor_data):
        lb = sensor_data_font.getbbox(entry.label, anchor="ls")
        lb_height = lb[3] - lb[1]
        lb_width = lb[2] - lb[0]

        vb = sensor_data_font.getbbox(entry.label, anchor="ls")
        vb_height = vb[3] - vb[1]
        max_height = max(lb_height, vb_height)

        label_x = x_pos + label_value_spacing + (longest_label_width - lb_width)
        label_y = entry_y_pos + -(lb[1])

        value_x = label_x + lb_width + label_value_spacing
        value_y = label_y

        sensor_data_background_height += max_height
        entry_y_pos += (max_height + entry_spacing_vertical)
        sensor_data_draw_positions.append(
            DataEntryDrawPos(
                label_pos=(label_x, label_y),
                value_pos=(value_x, value_y)
            )
        )
    y_pos = int(dst_image.height - sensor_data_background_height - box_padding)

    # OK, done calculating. Draw stuff
    draw = ImageDraw.Draw(dst_image)
    sensor_data_box_radius = int(IMAGE_WIDTH_TO_SENSOR_BOX_RADIUS_RATIO * dst_image.width)
    rr_im = antialiased_rounded_rect(
        width=int(sensor_data_background_width),
        height=int(sensor_data_background_height),
        radius=sensor_data_box_radius,
        stroke=SENSOR_OUTLINE_COLOR,
        stroke_width=2,
        fill=SENSOR_BACKGROUND_COLOR
    )
    dst_image.paste(rr_im, (x_pos, y_pos))

    for count, entry in enumerate(sensor_data):
        draw_positions = sensor_data_draw_positions[count]
        draw.text(
            xy=(draw_positions.label_pos[0], y_pos + draw_positions.label_pos[1]),
            text=entry.label,
            fill=SENSOR_LABEL_COLOR,
            font=sensor_data_font,
            anchor="ls"
        )

        draw.text(
            xy=(draw_positions.value_pos[0], y_pos + draw_positions.value_pos[1]),
            text=entry.value,
            fill=SENSOR_VALUE_COLOR,
            font=sensor_data_font,
            anchor="ls"
        )


def annotate_age(age, dst_image):
    age_font_height = int(dst_image.height * IMAGE_HEIGHT_TO_AGE_RATIO)
    age_font = ImageFont.truetype(SENSOR_DATA_FONT_FILE, age_font_height)
    age_string = "Day {}".format(age)

    # Calculate positions
    age_bb = age_font.getbbox(age_string, anchor="ls")
    age_height = age_bb[3] - age_bb[1]
    age_padding = (age_height / 2)
    text_xy = (
        # (dst_image.width - age_width - age_padding),
        age_padding,
        age_padding
    )

    # Draw
    draw = ImageDraw.Draw(dst_image)
    draw.text(
        xy=text_xy,
        text=age_string,
        fill=AGE_COLOR,
        font=age_font,
        stroke_width=4,
        stroke_fill=(0, 0, 0, 255),
        anchor="lt"
    )


def annotate_image(image_file, annotation_details):
    with Image.open(image_file).convert("RGBA") as image:
        # Make a blank image for the annotations, initialized to transparent text color
        annotation_image = Image.new("RGBA", image.size, (255, 255, 255, 0))

        annotate_grow_system_name_and_age(annotation_details.grow_system_name, annotation_details.age, annotation_image)
        annotate_sensor_data(annotation_details.sensor_data_strings, annotation_image)

        out = Image.alpha_composite(image, annotation_image)
        out.show()


annotate_image(SOURCE_FILE, details)
