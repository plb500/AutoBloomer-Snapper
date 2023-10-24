# AutoBloomer-Snapper
App for taking pictures via Raspberry Pi camera and overlaying grow system/sensor details

# Install procedure
Set up the Raspberry Pi as normal and make sure networking, SSH etc is all functional

## Install pre-requisites

You will need to install the following components via git:
- git
- python3-pip
- python3-venv
- libopenjp2-7


Use the following commands
```
sudo apt update
sudo apt upgrade
sudo apt install git python3-pip python3-venv libopenjp2-7
```

## Download repo
```
git clone git@github.com:plb500/AutoBloomer-Snapper.git
cd AutoBloomer-Snapper
git submodule update --init --recursive
```

## Set up virtual environment
```
cd AutoBloomer-Snapper
python3 -m venv snapper-env
source snapper-env/bin/activate
pip3 install -r requirements.txt
```

## Build protobufs
```
cd AutoBloomer-Snapper
source snapper-env/bin/activate
cd python/pyproto
./protobuf_build_python.sh
```

## Configure snapshot app
App is configured via the file `autobloomer_snapper_cfg.json`, found in the repo root. The JSON file has the following options, split into two sections:
- `server_options`: First section, contains details about the host grow controller
  - `host_name`: Address of the host controller, used to obtain current sensor data and upload grow system image snapshot
  - `port_number`: Port number the host is listening on
  - `server_passphrase`: Host controller security key (optional)
- `data_options`: Second section, contains details about the images we are storing
  - `image_destination`: Location to store image snapshots on this Pi (MUST exist)
  - `grow_system_id`: ID of the grow system we are querying/uploading image data to
  - `sensor_details`: Block containing the sensor details we want to annotate on the images. Contains one or more entries, each containing the following options:
    - `sensor_id`: ID of the sensor we want to query
    - `reading_id`: Reading we want to display

## Running program
Inside the repo root is a file called `run_snapper.sh`. This will take a single image from the camera, read the sensor data, annotate the image with grow system details and store the image in the directory specified by the config file

To get the program to generate images on a schedule (i.e. take a picture eery 5 minutes), the easiest way is to call the above script via crontab. You can edit the crontab file by using
```
crontab -e
```
You can generate a crontab entry easily [here](https://crontab.guru/).

## Streaming camera (for setting up zoom/focus etc)
SSH into the Raspberry Pi and run the following command:
```
libcamera-vid -t0 --width 1920 --height 1080 --framerate 10 --nopreview --codec h264 --profile high --intra 5 --listen -o tcp://0.0.0.0:8888
```
From a remote computer, open VLC, then select "Open Network" and use the following URL (replace XXX.XXX.XXX.XXX with the address of the Raspberry Pi):
```
tcp/h264://XXX.XXX.XXX.XXX:8888
```
