SOURCES=../src/scale_factors.cpp scale_factors_test.cpp
INCPATHS=../include
CXXFLAGS=-std=c++11 -Wall

# ------------ MAGIC BEGINS HERE -------------

# Automatic generation of some important lists
OBJECTS=$(SOURCES:.cpp=.o)
INCFLAGS=$(foreach TMP,$(INCPATHS),-I$(TMP))

all: tests

tests: $(OBJECTS)
	$(CXX) $(OBJECTS) -o $@.exe

.cpp.o:
	$(CXX) $(INCFLAGS) $(CXXFLAGS) -c -g -O2 -fPIC $< -o $@

distclean: clean
	rm -f tests.exe

clean:
	rm -f $(OBJECTS)
