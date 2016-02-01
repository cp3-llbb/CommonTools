cmake_minimum_required (VERSION 2.6)
project (histFactory)

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
find_library(ROOT_TREEPLAYER_LIBRARY TreePlayer ${ROOT_LIBRARY_DIR})
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

# Create header files
configure_file(src/config.h.in histFactory/config.h NEWLINE_STYLE UNIX)
include_directories(${PROJECT_BINARY_DIR})

# Create bash helper script for the plotter
configure_file(scripts/createPlotter.sh.in createPlotter.sh @ONLY NEWLINE_STYLE UNIX)

set(COMMON_SOURCES
    ${EXTERNAL_SRC_DIR}/jsoncpp.cpp
    )

# plotter sources
set(PLOTTER_SOURCES
    src/createPlotter.cpp
    ../common/src/formula_parser.cpp
    )

# Multidraw sources
set(MULTIDRAW_SOURCES
    src/createHistoWithMultiDraw.cpp
    ${EXTERNAL_SRC_DIR}/TMultiDrawTreePlayer.cxx
    ${EXTERNAL_SRC_DIR}/TSelectorMultiDraw.cxx
    ${MD_DICTIONARY}
    )

if(IN_CMSSW)
    include(CP3Dictionaries)
    list(APPEND COMMON_SOURCES ${DICTIONARIES_SOURCES})
endif()

add_library(common STATIC ${COMMON_SOURCES})

add_executable(plotter ${PLOTTER_SOURCES})
set_target_properties(plotter PROPERTIES OUTPUT_NAME "createPlotter.exe")

add_executable(multidraw ${MULTIDRAW_SOURCES})
set_target_properties(multidraw PROPERTIES OUTPUT_NAME "createHistoWithMultiDraw.exe")

add_executable(count src/countProcessedEvents.cpp)
set_target_properties(count PROPERTIES OUTPUT_NAME "createProcessedEvents.exe")

# Link libraries
target_link_libraries(plotter common)
target_link_libraries(plotter ${ROOT_LIBRARIES})
target_link_libraries(plotter ${PYTHON_LIBRARY})
target_link_libraries(plotter ${Boost_FILESYSTEM_LIBRARY}
  ${Boost_SYSTEM_LIBRARY})

target_link_libraries(plotter "uuid")

find_library(CTEMPLATE_LIBS NAMES "libctemplate_nothreads.a"
    "ctemplate_nothreads" PATHS ${EXTERNAL_LIB_DIR} NO_DEFAULT_PATH)
target_link_libraries(plotter ${CTEMPLATE_LIBS})

target_link_libraries(multidraw common)
target_link_libraries(multidraw ${ROOT_LIBRARIES})
target_link_libraries(multidraw ${ROOT_TREEPLAYER_LIBRARY})
target_link_libraries(multidraw ${PYTHON_LIBRARY})

target_link_libraries(multidraw "uuid")

target_link_libraries(count common)
target_link_libraries(count ${ROOT_LIBRARIES})
