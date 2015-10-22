PROJECT(MyHello)
cmake_minimum_required(VERSION 3.0)

include(conanbuildinfo.cmake)
CONAN_BASIC_SETUP()

ADD_EXECUTABLE(md5 md5.cpp)

TARGET_LINK_LIBRARIES(md5 ${CONAN_LIBS})