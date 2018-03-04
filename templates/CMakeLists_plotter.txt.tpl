cmake_minimum_required (VERSION 2.6)
project (Plotter)

# Configure paths
set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} "${PROJECT_SOURCE_DIR}/cmake/modules")

# Detect if we are inside a CMSSW env
include(CMSSW)

# Ensure C++11 is available
include(CheckCXXCompilerFlag)
CHECK_CXX_COMPILER_FLAG("-std=c++11" COMPILER_SUPPORTS_CXX0X)
if(COMPILER_SUPPORTS_CXX0X)
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11 -O2")
else()
    message(STATUS "The compiler ${CMAKE_CXX_COMPILER} has no C++11 support. Please use a different C++ compiler.")
endif()

# Find ROOT
find_package(ROOT REQUIRED)
include_directories(${ROOT_INCLUDE_DIR})
find_library(ROOT_TMVA_LIBRARY TMVA ${ROOT_LIBRARY_DIR} NO_DEFAULT_PATH)

find_library(ROOT_GENVECTOR_LIB GenVector PATHS ${ROOT_LIBRARY_DIR}
    NO_DEFAULT_PATH)
find_library(ROOT_TREEPLAYER_LIB TreePlayer PATHS ${ROOT_LIBRARY_DIR}
    NO_DEFAULT_PATH)

{{ADD_FIND}}

include_directories(${PROJECT_SOURCE_DIR})
include_directories(${PROJECT_BINARY_DIR})
include_directories({{ADD_INCLUDE_DIRS}})

set(PLOTTER_SOURCES
    Plotter.cc
    {{ADD_SOURCES}}
    )

if(IN_CMSSW)
    set_property(DIRECTORY ${PROJECT_BINARY_DIR} PROPERTY COMPILE_DEFINITIONS CP3LLBB_PLOTTER)
    include(CP3Dictionaries)
    list(APPEND PLOTTER_SOURCES ${DICTIONARIES_SOURCES})
    add_custom_command(OUTPUT ${PROJECT_BINARY_DIR}/classes.h COMMAND
            ${PROJECT_SOURCE_DIR}/generateHeader.sh
            ${PROJECT_BINARY_DIR}/classes.h
            COMMENT "Generating classes.h...")
    STRING(REPLACE ":" ";" CMSSW_INCLUDES $ENV{CMSSW_SEARCH_PATH})
    STRING(REPLACE ":" ";" FWLITE_INCLUDES $ENV{CMSSW_FWLITE_INCLUDE_PATH})
    include_directories(${CMSSW_INCLUDES} ${FWLITE_INCLUDES})

endif()

list(APPEND PLOTTER_SOURCES classes.h)

add_executable(plotter ${PLOTTER_SOURCES})
set_target_properties(plotter PROPERTIES OUTPUT_NAME "plotter.exe")
{{ADD_PROPERTIES}}

# Link libraries
target_link_libraries(plotter ${ROOT_LIBRARIES})
target_link_libraries(plotter ${ROOT_GENVECTOR_LIB})
target_link_libraries(plotter ${ROOT_TMVA_LIBRARY})
target_link_libraries(plotter ${ROOT_TREEPLAYER_LIB})
{{ADD_LINK}}

find_library(TREEWRAPPER_LIB cp3_llbbTreeWrapper PATHS
    "$ENV{CMSSW_BASE}/lib/$ENV{SCRAM_ARCH}" NO_DEFAULT_PATH)
target_link_libraries(plotter ${TREEWRAPPER_LIB})
