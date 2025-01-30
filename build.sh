#!/bin/bash

# Update package list and install GDAL
apt-get update && apt-get install -y gdal-bin libgdal-dev

# Verify GDAL installation
gdalinfo --version

# Install Python GDAL package using pre-installed GDAL version
export CPLUS_INCLUDE_PATH=/usr/include/gdal
export C_INCLUDE_PATH=/usr/include/gdal
pip install GDAL==$(gdal-config --version | awk -F'[.]' '{print $1"."$2}')

# Proceed with your app deployment
exec "$@"
