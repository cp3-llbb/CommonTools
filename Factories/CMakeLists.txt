cmake_minimum_required (VERSION 2.6)
project (histFactory)

# Configure paths
set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} "${PROJECT_SOURCE_DIR}/cmake/modules")
set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} "${PROJECT_SOURCE_DIR}/../cmake/modules")

# Detect if we are inside a CMSSW env
include(CMSSW)

# Ensure C++11 is available
include(CheckCXXCompilerFlag)
CHECK_CXX_COMPILER_FLAG("-std=c++11" COMPILER_SUPPORTS_CXX0X)
if(COMPILER_SUPPORTS_CXX0X)
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -O3 -std=c++11 -g")
else()
    message(STATUS "The compiler ${CMAKE_CXX_COMPILER} has no C++11 support. Please use a different C++ compiler.")
endif()

# Find ROOT
find_package(ROOT REQUIRED)
include_directories(SYSTEM ${ROOT_INCLUDE_DIR})

# Find Python

if(NOT IN_CMSSW)
    execute_process(COMMAND python-config --prefix OUTPUT_VARIABLE
        PYTHON_PREFIX OUTPUT_STRIP_TRAILING_WHITESPACE)
    list(APPEND CMAKE_LIBRARY_PATH "${PYTHON_PREFIX}/lib")
    list(APPEND CMAKE_INCLUDE_PATH "${PYTHON_PREFIX}/include")
endif()

set(Boost_NO_BOOST_CMAKE ON)
find_package(Boost REQUIRED COMPONENTS system filesystem)
include_directories(SYSTEM ${Boost_INCLUDE_DIRS})

find_package(PythonLibs REQUIRED)
include_directories(SYSTEM ${PYTHON_INCLUDE_PATH})

include_directories(include)
include_directories(../common/include)
include_directories(../external/include)

# Configure external
include(BuildExternals)

# Create header files
configure_file(include/config.h.in ${PROJECT_SOURCE_DIR}/include/config.h NEWLINE_STYLE UNIX)

# Create bash helper script for the plotter
set(NAME "Plotter")
set(EXECUTABLE "histFactory.exe")
configure_file(
    scripts/createFactory.sh.in
    createPlotter.sh
    @ONLY NEWLINE_STYLE UNIX)

set(NAME "Skimmer")
set(EXECUTABLE "treeFactory.exe")
configure_file(
    scripts/createFactory.sh.in
    createSkimmer.sh
    @ONLY NEWLINE_STYLE UNIX)

set(SOURCES
    ../common/src/formula_parser.cpp
    ../external/src/jsoncpp.cpp
    src/Factory.cc
    src/HistFactory.cc
    src/TreeFactory.cc
    src/createFactory.cc
    )

if(IN_CMSSW)
    include(CP3Dictionaries)
    list(APPEND SOURCES ${DICTIONARIES_SOURCES})
endif()

add_executable(factory ${SOURCES})
set_target_properties(factory PROPERTIES OUTPUT_NAME "factory.exe")

# Link libraries
target_link_libraries(factory uuid)
target_link_libraries(factory ${ROOT_LIBRARIES})
target_link_libraries(factory ${PYTHON_LIBRARY})
target_link_libraries(factory ${Boost_FILESYSTEM_LIBRARY}
  ${Boost_SYSTEM_LIBRARY})

find_library(CTEMPLATE_LIBS NAMES "libctemplate_nothreads.a"
    "ctemplate_nothreads" PATHS ${EXTERNAL_LIB_DIR} NO_DEFAULT_PATH)
target_link_libraries(factory ${CTEMPLATE_LIBS})

add_custom_target(histFactory ALL
                  COMMAND ${CMAKE_COMMAND} -E create_symlink
                  "${PROJECT_BINARY_DIR}/factory.exe" "${PROJECT_BINARY_DIR}/histFactory.exe"
                  DEPENDS factory)

add_custom_target(treeFactory ALL
                  COMMAND ${CMAKE_COMMAND} -E create_symlink
                  "${PROJECT_BINARY_DIR}/factory.exe" "${PROJECT_BINARY_DIR}/treeFactory.exe"
                  DEPENDS factory)
