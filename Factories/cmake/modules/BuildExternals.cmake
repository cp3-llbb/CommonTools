# Build externals

set(EXTERNAL_DIR "${PROJECT_BINARY_DIR}/external")
set(EXTERNAL_INCLUDE_DIR "${EXTERNAL_DIR}/include")
set(EXTERNAL_LIB_DIR "${EXTERNAL_DIR}/lib")
set(EXTERNAL_SRC_DIR "${EXTERNAL_DIR}/src")

include_directories(${EXTERNAL_INCLUDE_DIR})

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

    MESSAGE(STATUS "Building ctemplate")
    execute_process(COMMAND curl -L "https://github.com/OlafvdSpek/ctemplate/archive/ctemplate-${CTEMPLATE_VERSION}.tar.gz" -o "${CTEMPLATE_TAR}" WORKING_DIRECTORY ${EXTERNAL_DIR})
    execute_process(COMMAND tar xf ${CTEMPLATE_TAR} WORKING_DIRECTORY ${EXTERNAL_DIR})
    execute_process(COMMAND ./configure --prefix=${EXTERNAL_DIR} WORKING_DIRECTORY ${CTEMPLATE_DIR})
    execute_process(COMMAND make -j10 WORKING_DIRECTORY ${CTEMPLATE_DIR})
    execute_process(COMMAND make install -j10 WORKING_DIRECTORY ${CTEMPLATE_DIR})

    set(EXTERNAL_BUILT ON CACHE BOOL "Are externals already built?")
endif()
