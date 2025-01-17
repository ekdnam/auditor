# initial setup of vm 
sudo apt-get update
sudo apt-get upgrade

# install python
sudo add-apt-repository ppa:deadsnakes/ppa 
sudo apt-get update 
sudo apt-get install python3.7
sudo apt install python3-pip

# install firefox and firefox driver
wget https://github.com/mozilla/geckodriver/releases/download/v0.32.2/geckodriver-v0.32.2-linux64.tar.gz
tar -C /usr/local/bin/ -xvf geckodriver-v0.32.2-linux64.tar.gz
sudo apt install firefox

# depedencies for imagehash
sudo apt install libjpeg-dev zlib1g-dev
# install xvfb
sudo apt-get install xvfb

# install depedencies
pip install --editable . -r requirements.txt

# fix a geckodriver issue
sudo apt install firefox-geckodriver

# download vpn
sudo apt-get install openvpn unzip
cd /etc/openvpn
sudo wget https://my.surfshark.com/vpn/api/v1/server/configurations
sudo unzip configurations
sudo wget https://ocean.surfshark.com/debian/pool/main/s/surfshark-release/surfshark-release_1.0.0-2.1_amd64.deb
sudo dpkg -i surfshark-release_1.0.0-2.1_amd64.deb
sudo apt-get update
sudo apt-get install surfshark-vpn
