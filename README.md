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
