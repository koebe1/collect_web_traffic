# getData

master thesis project to collect network traffic

TO DO:

- add config file

Documentation:

How to use:

1. Set specifications in config file
2. Download Docker Container ####### replace $DATASET with the path on your system to dataset -> your/path/to/dataset
   a) docker run -it --name chrome -p 4444:4444 -v "$DATASET":/ssl -e SSLKEYLOGFILE=ssl/sslkeylogfile.txt retreatguru/headless-chromedriver
   b) docker run --rm --name tcpdump --net=container:chrome -v \$DATASET/captured:/tcpdump kaazing/tcpdump not host 127.0.0.1 and not host 172.17.0.1 -v -i any -w tcpdump/tcpdump.pcap
3. Specify websites you want to visit in websites.txt file

DEPENDENCIES

to install:

Docker Desktop for Mac / Docker for Windows

python dependencies

with pip:
pip install selenium
pip install argparse
pip install pyperclip
pip install yaml
pip install psutil
# collect_web_traffic
