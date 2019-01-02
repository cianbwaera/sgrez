#!/bin/sh
pip3 install --user -U -r requirements.txt
echo "Running build"
cd ../
python3 ./build.py
