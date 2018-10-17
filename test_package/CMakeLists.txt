PROJECT(MyHello)
cmake_minimum_required(VERSION 2.8)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

ADD_EXECUTABLE(digest digest.cpp)

if(USE_FIND_PACKAGE)
    set(OpenSSL_DEBUG 1)
    find_package(OpenSSL REQUIRED)
    MESSAGE("LINK WITH ${OPENSSL_LIBRARIES}")

    include_directories(${OPENSSL_INCLUDE_DIRS})
    TARGET_LINK_LIBRARIES(digest ${OPENSSL_LIBRARIES})

    if(WIN32)
        TARGET_LINK_LIBRARIES(digest ws2_32 crypt32)
    endif()
    if(UNIX AND NOT APPLE)
        TARGET_LINK_LIBRARIES(digest dl pthread)
    endif()
else()
    MESSAGE("LINK WITH ${CONAN_LIBS}")
    include_directories(${CONAN_INCLUDE_DIRS})
    TARGET_LINK_LIBRARIES(digest ${CONAN_LIBS})
endif()
