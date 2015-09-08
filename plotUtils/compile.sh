ROOT_INC=`root-config --incdir`
ROOT_LIB=`root-config --libs`

g++ -fPIC -std=c++11 -I TMultiDrawTreePlayer -I jsoncpp/dist `root-config --cflags` TMultiDrawTreePlayer/dictionary.cc TMultiDrawTreePlayer/TMultiDrawTreePlayer.cxx jsoncpp/dist/jsoncpp.cpp createHistoWithMultiDraw.cpp `root-config --ldflags --libs` -lTreePlayer
#g++ -std=c++11 -I $ROOT_INC -I TMultiDrawTreePlayer -I jsoncpp/dist $ROOT_LIB jsoncpp/dist/jsoncpp.cpp TMultiDrawTreePlayer/TMultiDrawTreePlayer.cxx createHistoWithMultiDraw.cpp 
