#! /bin/bash

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
