cmake_minimum_required (VERSION 2.6)
project (histFactory)

# Configure paths
set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} "${PROJECT_SOURCE_DIR}/cmake/modules")

# Detect if we are inside a CMSSW env
include(CMSSW)

# Ensure C++11 is available
include(CheckCXXCompilerFlag)
CHECK_CXX_COMPILER_FLAG("-std=c++0x" COMPILER_SUPPORTS_CXX0X)
if(COMPILER_SUPPORTS_CXX0X)
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -O3 -std=c++0x -g")
else()
    message(STATUS "The compiler ${CMAKE_CXX_COMPILER} has no C++11 support. Please use a different C++ compiler.")
endif()
# Find ROOT
find_package(ROOT REQUIRED)
find_library(ROOT_TREEPLAYER_LIBRARY TreePlayer ${ROOT_LIBRARY_DIR})
include_directories(${ROOT_INCLUDE_DIR})

# Find Python

if(IN_CMSSW)
    # Help cmake finding python inside CMSSW
    execute_process(COMMAND scram tool tag python LIBDIR OUTPUT_VARIABLE PYTHON_LIBRARY_PATH OUTPUT_STRIP_TRAILING_WHITESPACE)
    execute_process(COMMAND scram tool tag python LIB OUTPUT_VARIABLE PYTHON_LIBRARY OUTPUT_STRIP_TRAILING_WHITESPACE)
    set(PYTHON_LIBRARY "${PYTHON_LIBRARY_PATH}/lib${PYTHON_LIBRARY}.so")
    execute_process(COMMAND scram tool tag python INCLUDE OUTPUT_VARIABLE PYTHON_INCLUDE_DIR OUTPUT_STRIP_TRAILING_WHITESPACE)

    # Boost
    execute_process(COMMAND scram tool tag boost BOOST_BASE OUTPUT_VARIABLE
        BOOST_ROOT OUTPUT_STRIP_TRAILING_WHITESPACE)
    set(Boost_NO_SYSTEM_PATHS ON)
else()
    execute_process(COMMAND python-config --prefix OUTPUT_VARIABLE
        PYTHON_PREFIX OUTPUT_STRIP_TRAILING_WHITESPACE)
    list(APPEND CMAKE_LIBRARY_PATH "${PYTHON_PREFIX}/lib")
    list(APPEND CMAKE_INCLUDE_PATH "${PYTHON_PREFIX}/include")
endif()

set(Boost_NO_BOOST_CMAKE ON)
find_package(Boost REQUIRED)
include_directories(${Boost_INCLUDE_DIRS})

find_package(PythonLibs REQUIRED)
include_directories(${PYTHON_INCLUDE_PATH})

include_directories(src)

# Configure external

include(BuildExternals)

# Create header files
configure_file(src/config.h.in histFactory/config.h NEWLINE_STYLE UNIX)
include_directories(${PROJECT_BINARY_DIR})

# Create bash helper script for the plotter
configure_file(scripts/createPlotter.sh.in createPlotter.sh @ONLY NEWLINE_STYLE UNIX)

# plotter sources
set(PLOTTER_SOURCES
    src/createPlotter.cpp
    src/formula_parser.cpp
    )

# Multidraw sources
set(MULTIDRAW_SOURCES
    src/createHistoWithMultiDraw.cpp
    ${EXTERNAL_SRC_DIR}/jsoncpp.cpp
    ${EXTERNAL_SRC_DIR}/TMultiDrawTreePlayer.cxx
    ${EXTERNAL_SRC_DIR}/TSelectorMultiDraw.cxx
    ${MD_DICTIONARY}
    )

if(IN_CMSSW)

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

                list(APPEND PLOTTER_SOURCES ${CP3LLBB_SUBDIR}_dict.cpp)
                list(APPEND MULTIDRAW_SOURCES ${CP3LLBB_SUBDIR}_dict.cpp)
                
            endif()
        endif()
    endforeach()
endif()

add_executable(plotter ${PLOTTER_SOURCES})
set_target_properties(plotter PROPERTIES OUTPUT_NAME "createPlotter.exe")

add_executable(multidraw ${MULTIDRAW_SOURCES})
set_target_properties(multidraw PROPERTIES OUTPUT_NAME "createHistoWithMultiDraw.exe")

add_executable(count src/countProcessedEvents.cpp
    ${EXTERNAL_SRC_DIR}/jsoncpp.cpp)
set_target_properties(count PROPERTIES OUTPUT_NAME "createProcessedEvents.exe")

# Link libraries
target_link_libraries(plotter ${ROOT_LIBRARIES})
target_link_libraries(plotter ${PYTHON_LIBRARY})

target_link_libraries(plotter "uuid")

find_library(CTEMPLATE_LIBS NAMES "libctemplate_nothreads.a"
    "ctemplate_nothreads" PATHS ${EXTERNAL_LIB_DIR} NO_DEFAULT_PATH)
target_link_libraries(plotter ${CTEMPLATE_LIBS})

target_link_libraries(multidraw ${ROOT_LIBRARIES})
target_link_libraries(multidraw ${ROOT_TREEPLAYER_LIBRARY})
target_link_libraries(multidraw ${PYTHON_LIBRARY})

target_link_libraries(multidraw "uuid")

target_link_libraries(count ${ROOT_LIBRARIES})
