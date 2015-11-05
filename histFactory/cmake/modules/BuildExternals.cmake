# Build externals

set(EXTERNAL_DIR "${PROJECT_BINARY_DIR}/external")
set(EXTERNAL_INCLUDE_DIR "${EXTERNAL_DIR}/include")
set(EXTERNAL_LIB_DIR "${EXTERNAL_DIR}/lib")
set(EXTERNAL_SRC_DIR "${EXTERNAL_DIR}/src")

include_directories(${EXTERNAL_INCLUDE_DIR})

set(JSONCPP_VERSION "1.6.5")
set(JSONCPP_TAR "jsoncpp-${JSONCPP_VERSION}.tar.gz")
set(JSONCPP_DIR ${EXTERNAL_DIR}/jsoncpp-${JSONCPP_VERSION})

set(MD_VERSION "1.1.2")
set(MD_TAR "TMultiDrawTreePlayer-${MD_VERSION}.tar.gz")
set(MD_DIR ${EXTERNAL_DIR}/TMultiDrawTreePlayer-${MD_VERSION})

set(TCLAP_VERSION "1.2.1")
set(TCLAP_TAR "tclap-${TCLAP_VERSION}.tar.gz")
set(TCLAP_DIR ${EXTERNAL_DIR}/tclap-${TCLAP_VERSION})

set(CTEMPLATE_VERSION "2.3")
set(CTEMPLATE_TAR "ctemplate-${CTEMPLATE_VERSION}.tar.gz")
set(CTEMPLATE_DIR ${EXTERNAL_DIR}/ctemplate-ctemplate-${CTEMPLATE_VERSION})


if (NOT EXTERNAL_BUILT)

    if (NOT IS_DIRECTORY ${EXTERNAL_INCLUDE_DIR})
        file(MAKE_DIRECTORY ${EXTERNAL_INCLUDE_DIR})
    endif()

    if (NOT IS_DIRECTORY ${EXTERNAL_SRC_DIR})
        file(MAKE_DIRECTORY ${EXTERNAL_SRC_DIR})
    endif()

    if (NOT IS_DIRECTORY ${EXTERNAL_LIB_DIR})
        file(MAKE_DIRECTORY ${EXTERNAL_LIB_DIR})
    endif()

    MESSAGE(STATUS "Building json-cpp")

    execute_process(COMMAND curl -L "https://github.com/open-source-parsers/jsoncpp/archive/${JSONCPP_VERSION}.tar.gz" -o "${JSONCPP_TAR}" WORKING_DIRECTORY ${EXTERNAL_DIR})
    execute_process(COMMAND tar xf ${JSONCPP_TAR} WORKING_DIRECTORY ${EXTERNAL_DIR})
    execute_process(COMMAND python amalgamate.py WORKING_DIRECTORY ${JSONCPP_DIR})
    execute_process(COMMAND ${CMAKE_COMMAND} -E copy ${JSONCPP_DIR}/dist/jsoncpp.cpp ${EXTERNAL_SRC_DIR})
    execute_process(COMMAND ${CMAKE_COMMAND} -E copy_directory ${JSONCPP_DIR}/dist/json ${EXTERNAL_INCLUDE_DIR}/json/)

    MESSAGE(STATUS "Building TMultiDrawTreePlayer")
    execute_process(COMMAND curl -L "https://github.com/blinkseb/TMultiDrawTreePlayer/archive/v${MD_VERSION}.tar.gz" -o "${MD_TAR}" WORKING_DIRECTORY ${EXTERNAL_DIR})
    execute_process(COMMAND tar xf ${MD_TAR} WORKING_DIRECTORY ${EXTERNAL_DIR})
    execute_process(COMMAND ${CMAKE_COMMAND} -E copy ${MD_DIR}/TMultiDrawTreePlayer.cxx ${EXTERNAL_SRC_DIR})
    execute_process(COMMAND ${CMAKE_COMMAND} -E copy ${MD_DIR}/TSelectorMultiDraw.cxx ${EXTERNAL_SRC_DIR})
    execute_process(COMMAND ${CMAKE_COMMAND} -E copy ${MD_DIR}/TMultiDrawTreePlayer.h ${EXTERNAL_INCLUDE_DIR})
    execute_process(COMMAND ${CMAKE_COMMAND} -E copy ${MD_DIR}/TSelectorMultiDraw.h ${EXTERNAL_INCLUDE_DIR})

    MESSAGE(STATUS "Building TCLAP")
    execute_process(COMMAND curl -L "http://downloads.sourceforge.net/project/tclap/tclap-1.2.1.tar.gz?r=http%3A%2F%2Fsourceforge.net%2Fprojects%2Ftclap%2Ffiles%2F&ts=1431017326&use_mirror=freefr" -o "${TCLAP_TAR}" WORKING_DIRECTORY ${EXTERNAL_DIR})
    execute_process(COMMAND tar xf ${TCLAP_TAR} WORKING_DIRECTORY ${EXTERNAL_DIR})
    execute_process(COMMAND ./configure --prefix=${EXTERNAL_DIR} WORKING_DIRECTORY ${TCLAP_DIR})
    execute_process(COMMAND make -j4 WORKING_DIRECTORY ${TCLAP_DIR})
    execute_process(COMMAND make install -j4 WORKING_DIRECTORY ${TCLAP_DIR})

    MESSAGE(STATUS "Building ctemplate")
    execute_process(COMMAND curl -L "https://github.com/OlafvdSpek/ctemplate/archive/ctemplate-${CTEMPLATE_VERSION}.tar.gz" -o "${CTEMPLATE_TAR}" WORKING_DIRECTORY ${EXTERNAL_DIR})
    execute_process(COMMAND tar xf ${CTEMPLATE_TAR} WORKING_DIRECTORY ${EXTERNAL_DIR})
    execute_process(COMMAND ./configure --prefix=${EXTERNAL_DIR} WORKING_DIRECTORY ${CTEMPLATE_DIR})
    execute_process(COMMAND make -j10 WORKING_DIRECTORY ${CTEMPLATE_DIR})
    execute_process(COMMAND make install -j10 WORKING_DIRECTORY ${CTEMPLATE_DIR})

    set(EXTERNAL_BUILT ON CACHE BOOL "Are externals already built?")
endif()

ROOT_GENERATE_DICTIONARY(TMultiDrawTreePlayer_dict
    ${MD_DIR}/classes.h
    LINKDEF ${MD_DIR}/LinkDef.h)
set(MD_DICTIONARY "TMultiDrawTreePlayer_dict.cxx")
