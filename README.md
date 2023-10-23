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
sudo apt install git install python3-pip python3-venv libopenjp2-7
```

## Download repo
```
git clone git@github.com:plb500/AutoBloomer-Snapper.git
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

## Streaming camera (for setting up zoom/focus etc)
SSH into the Raspberry Pi and run the following command:
```
libcamera-vid -t0 --width 1920 --height 1080 --framerate 10 --nopreview --codec h264 --profile high --intra 5 --listen -o tcp://0.0.0.0:8888
```
From a remote computer, open VLC, then select "Open Network" and use the following URL (replace XXX.XXX.XXX.XXX with the address of the Raspberry Pi):
```
tcp/h264://XXX.XXX.XXX.XXXX:8888
```
