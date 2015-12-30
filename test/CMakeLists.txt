PROJECT(MyHello)
cmake_minimum_required(VERSION 3.0)

include(conanbuildinfo.cmake)
CONAN_BASIC_SETUP()

find_package(OpenSSL)

IF(OPENSSL_FOUND)
    include_directories(${OPENSSL_INCLUDE_DIRS})
    ADD_EXECUTABLE(md5 md5.cpp)
    TARGET_LINK_LIBRARIES(md5 ${OPENSSL_LIBRARIES})
ELSE()
    MESSAGE(FATAL_ERROR "ERROR! OPENSSL NOT FOUND!")
ENDIF()