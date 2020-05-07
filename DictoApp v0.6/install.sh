#!/bin/bash
printf "Installing DictoApp dependencies:\n\n"
sudo apt-get update -y
sudo apt-get install -y gtk3-engines-unico
sudo apt-get install libgtk-3-dev
sudo apt-get install libglib2.0-dev
sudo apt-get install -y libpango-1.0-0
sudo apt-get install libgdk-pixbuf2.0-dev
sudo apt-get install libatk1.0*
sudo apt install python3-gi python3-gi-cairo gir1. 2-gtk-3.0
sudo apt-get install python3.6
sudo apt-get install python3-pip
sudo apt-get install python3 python-dev python3-dev
sudo apt-get install build-essential libssl-dev libffi-dev
sudo apt-get install libxml2-dev libxslt1-dev zlib1g-dev
sudo apt-get install python-pip
pip install wheel
pip3 install pycairo
pip3 install PyGObject
sudo apt-get install gobject-introspection-1.0
sudo apt-get install gobject-introspection libgirepository1.0-dev
printf "\n\nInstallation complete, starting DictoApp:\n\n"
python3 dictoapp.py
