cmake_minimum_required (VERSION 2.6)
project (treeFactory)

# Configure paths
set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} "${PROJECT_SOURCE_DIR}/../cmake/modules")

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
include_directories(${ROOT_INCLUDE_DIR})

# Find Python

if(NOT IN_CMSSW)
    execute_process(COMMAND python-config --prefix OUTPUT_VARIABLE
        PYTHON_PREFIX OUTPUT_STRIP_TRAILING_WHITESPACE)
    list(APPEND CMAKE_LIBRARY_PATH "${PYTHON_PREFIX}/lib")
    list(APPEND CMAKE_INCLUDE_PATH "${PYTHON_PREFIX}/include")
endif()

set(Boost_NO_BOOST_CMAKE ON)
find_package(Boost REQUIRED COMPONENTS system filesystem)
include_directories(${Boost_INCLUDE_DIRS})

find_package(PythonLibs REQUIRED)
include_directories(${PYTHON_INCLUDE_PATH})

include_directories(../common/include)

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

set(SKIMMER_SOURCES
    "src/createSkimmer.cc"
    "../common/src/formula_parser.cpp"
    )
list(APPEND SKIMMER_SOURCES ${DICTIONARIES_SOURCES})

add_executable(skimmer ${SKIMMER_SOURCES})
set_target_properties(skimmer PROPERTIES OUTPUT_NAME "createSkimmer.exe")

target_link_libraries(skimmer ${ROOT_LIBRARIES})
target_link_libraries(skimmer ${PYTHON_LIBRARY})
target_link_libraries(skimmer "uuid")
target_link_libraries(skimmer ${CTEMPLATE_LIBS})
target_link_libraries(skimmer ${Boost_FILESYSTEM_LIBRARY}
  ${Boost_SYSTEM_LIBRARY})
