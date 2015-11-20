cmake_minimum_required (VERSION 2.6)
project (treeFactory)

# Configure paths
set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} "${PROJECT_SOURCE_DIR}/cmake/modules")

# Detect if we are inside a CMSSW env
include(CMSSW)

# Ensure C++11 is available
include(CheckCXXCompilerFlag)
CHECK_CXX_COMPILER_FLAG("-std=c++0x" COMPILER_SUPPORTS_CXX0X)
if(COMPILER_SUPPORTS_CXX0X)
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++0x -g")
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
else()
    execute_process(COMMAND python-config --prefix OUTPUT_VARIABLE
        PYTHON_PREFIX OUTPUT_STRIP_TRAILING_WHITESPACE)
    list(APPEND CMAKE_LIBRARY_PATH "${PYTHON_PREFIX}/lib")
    list(APPEND CMAKE_INCLUDE_PATH "${PYTHON_PREFIX}/include")
endif()

find_package(PythonLibs REQUIRED)
include_directories(${PYTHON_INCLUDE_PATH})

# Configure external
include(BuildExternals)

# Template library
find_library(CTEMPLATE_LIBS NAMES "libctemplate_nothreads.a"
    "ctemplate_nothreads" PATHS ${EXTERNAL_LIB_DIR} NO_DEFAULT_PATH)

# Create header files
configure_file(src/config.h.in treeFactory/config.h NEWLINE_STYLE UNIX)
include_directories(${PROJECT_BINARY_DIR})

# Create bash helper script for the plotter
configure_file(scripts/createSkimmer.sh.in createSkimmer.sh @ONLY NEWLINE_STYLE UNIX)

# Create targets

include(CP3Dictionaries)

set(SKIMMER_SOURCES "skimmer/createSkimmer.cc")
list(APPEND SKIMMER_SOURCES ${DICTIONARIES_SOURCES})

add_executable(skimmer ${SKIMMER_SOURCES})
set_target_properties(skimmer PROPERTIES OUTPUT_NAME "createSkimmer.exe")

target_link_libraries(skimmer ${ROOT_LIBRARIES})
target_link_libraries(skimmer ${ROOT_TREEPLAYER_LIBRARY})
target_link_libraries(skimmer ${PYTHON_LIBRARY})
target_link_libraries(skimmer "uuid")
target_link_libraries(skimmer ${CTEMPLATE_LIBS})
