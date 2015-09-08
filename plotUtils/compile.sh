ROOT_INC=`root-config --incdir`
ROOT_LIB=`root-config --libs`

g++ -std=c++11 -I $ROOT_INC -I TMultiDrawTreePlayer -I jsoncpp/dist $ROOT_LIB jsoncpp/dist/jsoncpp.cpp TMultiDrawTreePlayer/TMultiDrawTreePlayer.cxx createHistoWithMultiDraw.cpp 
