#! /bin/bash

rm -rf include src jsoncpp TMultiDrawTreePlayer lib share tclap*

# JSON-CPP

mkdir -p include
mkdir -p src

git clone https://github.com/open-source-parsers/jsoncpp.git

cd jsoncpp
python amalgamate.py

mv dist/jsoncpp.cpp ../src/
mv dist/json ../include/

cd ..

# TMultiDrawTreePlayer

git clone https://github.com/blinkseb/TMultiDrawTreePlayer.git

cd TMultiDrawTreePlayer

# Create dictionnary
rootcint -f TMultiDrawTreePlayer_dict.cpp -c -p classes.h LinkDef.h

mv TMultiDrawTreePlayer_dict.cpp ../src/
mv TMultiDrawTreePlayer.cxx ../src/TMultiDrawTreePlayer.cpp
mv TMultiDrawTreePlayer.h ../include/
mv classes.h ../include/

cd ..

# TCLAP

# TCLAP
curl -L "http://downloads.sourceforge.net/project/tclap/{tclap-1.2.1.tar.gz}?r=http%3A%2F%2Fsourceforge.net%2Fprojects%2Ftclap%2Ffiles%2F&ts=1431017326&use_mirror=freefr" -o "#1"
tar xf tclap-1.2.1.tar.gz

cd tclap-1.2.1
./configure --prefix=$PWD/../

make -j4
make install

cd ..
rm tclap-1.2.1.tar.gz
