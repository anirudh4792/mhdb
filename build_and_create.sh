# buid_and_create.sh
#
# This is a simple BASH script to build and execute mhdb/create_mhdb.
#
# Requires 'mentalhealth.xlsx' to be included in one of the following
# locations:
# • './data'
# • './mhdb/data'
# • '/data'
#
# Authors:
#     - Jon Clucas, 2017 (jon.clucas@childmind.org)
#
# Copyright 2017, Child Mind Institute (http://childmind.org),
# Apache v2.0 License

python3 setup.py build
python3 setup.py install
cd mhdb
./create_mhdb
# python3 create_mhdbnb.py
cd ..
