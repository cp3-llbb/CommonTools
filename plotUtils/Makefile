ObjSuf        = o
SrcSuf        = cpp


CXX           = g++
CXXFLAGS      = $(shell root-config --cflags) -Iexternal/include
LD			  = g++
LIBS          = $(shell root-config --libs) -lTreePlayer
LDFLAGS		  = $(shell root-config --ldflags)

#------------------------------------------------------------------------------
SOURCES		= createHistoWithMultiDraw.cpp external/src/jsoncpp.cpp external/src/TMultiDrawTreePlayer_dict.cpp external/src/TMultiDrawTreePlayer.cpp
OBJECTS     = $(SOURCES:.$(SrcSuf)=.$(ObjSuf))
DEPENDS		= $(OBJECTS:.o=.d)

.SUFFIXES: .cpp .cc

###

all: createHistoWithMultiDraw

clean:
	@rm -f $(OBJECTS);
	@rm -f $(DEPENDS);

createHistoWithMultiDraw: $(OBJECTS)
	$(LD) $(LDFLAGS) $+ -o $@ $(LIBS)
	@ln -sf external/TMultiDrawTreePlayer/TMultiDrawTreePlayer_dict_rdict.pcm .

%.o: %.cpp
	$(CXX) $(CXXFLAGS) -c -o $@ $<

# Make the dependencies
%.d: %.cpp
	@echo "Generating dependencies for $<"
	@ $(CXX) $(CXXFLAGS) -MM $< | sed -e 's@^\(.*\)\.o:@src/\1.d src/\1.o:@' > $@

ifneq ($(MAKECMDGOALS), clean) 
-include $(DEPENDS) 
endif

