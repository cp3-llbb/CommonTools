CC        = g++
CCFLAGS   = -Wall
SOURCES   =
ROOTFLAGS = `root-config --cflags`
ROOTLIBS  = `root-config --libs --ldflags`
TMVA = -L${ROOTSYS}lib -lTMVA

all: train.exe

train.exe: train.cc
	$(CC) $(TMVA) $(CCFLAGS) $(ROOTFLAGS) $(ROOTLIBS) train.cc -o train.exe

clean:
	rm *.exe
