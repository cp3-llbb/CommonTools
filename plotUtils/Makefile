ObjSuf        = o
SrcSuf        = cpp


CXX           = g++
CXXFLAGS      = $(shell root-config --cflags) -Iexternal/include
LD			  = g++
LIBS          = $(shell root-config --libs) -lTreePlayer
LDFLAGS		  = $(shell root-config --ldflags)

#------------------------------------------------------------------------------
SOURCESHIST	= createHistoWithMultiDraw.cpp external/src/jsoncpp.cpp external/src/TMultiDrawTreePlayer_dict.cpp external/src/TMultiDrawTreePlayer.cpp
OBJECTSHIST    	= $(SOURCESHIST:.$(SrcSuf)=.$(ObjSuf))
DEPENDSHIST	= $(OBJECTSHIST:.o=.d)

SOURCESCOUNT     = countProcessedEvents.cpp external/src/jsoncpp.cpp external/src/TMultiDrawTreePlayer_dict.cpp external/src/TMultiDrawTreePlayer.cpp
OBJECTSCOUNT     = $(SOURCESCOUNT:.$(SrcSuf)=.$(ObjSuf))
DEPENDSCOUNT     = $(OBJECTSCOUNT:.o=.d)


.SUFFIXES: .cpp .cc

###

all: createHistoWithMultiDraw.exe countProcessedEvents.exe

clean:
	@rm -f $(OBJECTSCOUNT);
	@rm -f $(DEPENDSCOUNT);

createHistoWithMultiDraw.exe: $(OBJECTSHIST)
	$(LD) $(LDFLAGS) $+ -o $@ $(LIBS)
	@ln -sf external/TMultiDrawTreePlayer/TMultiDrawTreePlayer_dict_rdict.pcm .

countProcessedEvents.exe: $(OBJECTSCOUNT)
	$(LD) $(LDFLAGS) $+ -o $@ $(LIBS)

%.o: %.cpp
	$(CXX) $(CXXFLAGS) -c -o $@ $<

# Make the dependencies
%.d: %.cpp
	@echo "Generating dependencies for $<"
	@ $(CXX) $(CXXFLAGS) -MM $< | sed -e 's@^\(.*\)\.o:@src/\1.d src/\1.o:@' > $@

ifneq ($(MAKECMDGOALS), clean) 
-include $(DEPENDSHIST)
-include $(DEPENDSCOUNT) 
endif

