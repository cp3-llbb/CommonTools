cmake_minimum_required (VERSION 2.6)
project (Skimmer)

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
include_directories(${ROOT_INCLUDE_DIR})

find_library(ROOT_GENVECTOR_LIB GenVector PATHS ${ROOT_LIBRARY_DIR}
    NO_DEFAULT_PATH)

include_directories(${PROJECT_SOURCE_DIR})
include_directories(${PROJECT_BINARY_DIR})

# Configure external
set(EXTERNAL_DIR "${PROJECT_BINARY_DIR}/external")
set(EXTERNAL_INCLUDE_DIR "${EXTERNAL_DIR}/include")
set(EXTERNAL_LIB_DIR "${EXTERNAL_DIR}/lib")
set(EXTERNAL_SRC_DIR "${EXTERNAL_DIR}/src")

include_directories(${EXTERNAL_INCLUDE_DIR})

# Create python script to parallelize the skimmer
configure_file(scripts/parallelizedSkimmer.py.in parallelizedSkimmer.py @ONLY NEWLINE_STYLE UNIX)

set(SKIMMER_SOURCES
    Skimmer.cc
    ${EXTERNAL_SRC_DIR}/jsoncpp.cpp
    )

if(IN_CMSSW)
    include_directories($ENV{CMSSW_BASE}/src)

    add_custom_command(OUTPUT ${PROJECT_BINARY_DIR}/classes.h COMMAND
        ${PROJECT_SOURCE_DIR}/generateHeader.sh
        ${PROJECT_BINARY_DIR}/classes.h
        COMMENT "Generating classes.h...")

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

                list(APPEND SKIMMER_SOURCES ${CP3LLBB_SUBDIR}_dict.cpp)
                
            endif()
        endif()
    endforeach()
endif()

list(APPEND SKIMMER_SOURCES classes.h)

add_executable(skimmer ${SKIMMER_SOURCES})
set_target_properties(skimmer PROPERTIES OUTPUT_NAME "skimmer.exe")

# Link libraries
target_link_libraries(skimmer ${ROOT_LIBRARIES})
target_link_libraries(skimmer ${ROOT_GENVECTOR_LIB})

find_library(TREEWRAPPER_LIB cp3_llbbTreeWrapper PATHS
    "$ENV{CMSSW_BASE}/lib/$ENV{SCRAM_ARCH}" NO_DEFAULT_PATH)
target_link_libraries(skimmer ${TREEWRAPPER_LIB})
