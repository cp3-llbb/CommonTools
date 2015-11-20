set(DICTIONARIES_SOURCES "")

# Generate dictionnaries
include_directories($ENV{CMSSW_BASE}/src)

set(CP3LLBB_BASE "$ENV{CMSSW_BASE}/src/cp3_llbb")
file(GLOB CP3LLBB_SUBDIRS RELATIVE ${CP3LLBB_BASE} ${CP3LLBB_BASE}/*)
foreach(CP3LLBB_SUBDIR ${CP3LLBB_SUBDIRS})
    if (IS_DIRECTORY ${CP3LLBB_BASE}/${CP3LLBB_SUBDIR})
        # Do we have a dictionnary here?
        set(SRC ${CP3LLBB_BASE}/${CP3LLBB_SUBDIR}/src)
        if (EXISTS ${SRC}/classes.h
            AND EXISTS ${SRC}/classes_def.xml)

            REFLEX_GENERATE_DICTIONARY(${CP3LLBB_SUBDIR}_dict
                ${SRC}/classes.h
                SELECTION ${SRC}/classes_def.xml
                )

            list(APPEND DICTIONARIES_SOURCES ${CP3LLBB_SUBDIR}_dict.cpp)
            
        endif()
    endif()
endforeach()
