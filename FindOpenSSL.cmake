#=============================================================================
# Copyright 2006-2009 Kitware, Inc.
# Copyright 2006 Alexander Neundorf <neundorf@kde.org>
# Copyright 2009-2011 Mathieu Malaterre <mathieu.malaterre@gmail.com>
#
# Distributed under the OSI-approved BSD License (the "License");
# see accompanying file Copyright.txt for details.
#
# This software is distributed WITHOUT ANY WARRANTY; without even the
# implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the License for more information.
#=============================================================================
# (To distribute this file outside of CMake, substitute the full
#  License text for the above reference.)


MESSAGE(STATUS "********* Conan FindOpenSSL wrapper! **********")

SET(OPENSSL_ROOT_DIR ${CONAN_OPENSSL_ROOT})
SET(OPENSSL_INCLUDE_DIR ${CONAN_INCLUDE_DIRS_OPENSSL})

include(FindPackageHandleStandardArgs)
FOREACH(THELIB ${CONAN_LIBS_OPENSSL})
    IF(NOT ${THELIB} MATCHES "ssl" AND NOT ${THELIB} MATCHES "crypto")
        find_library(LIB_${THELIB} NAMES ${THELIB} PATHS ${CONAN_LIB_DIRS_OPENSSL})
    ELSE()
        find_library(LIB_${THELIB} NAMES ${THELIB} PATHS ${CONAN_LIB_DIRS_OPENSSL} NO_DEFAULT_PATH)
    ENDIF()
    
    IF(${THELIB} MATCHES "ssl")
        set(OPENSSL_SSL_LIBRARY ${LIB_${THELIB}})
    ENDIF()
    IF(${THELIB} MATCHES "crypto")
        set(OPENSSL_CRYPTO_LIBRARY ${LIB_${THELIB}})
    ENDIF()
    IF(NOT ${LIB_${THELIB}} MATCHES "NOTFOUND")
        set(OPENSSL_LIBRARIES ${OPENSSL_LIBRARIES} ${LIB_${THELIB}})
    ENDIF()
    MESSAGE(${OPENSSL_LIBRARIES})
ENDFOREACH()


function(from_hex HEX DEC)
  string(TOUPPER "${HEX}" HEX)
  set(_res 0)
  string(LENGTH "${HEX}" _strlen)

  while (_strlen GREATER 0)
    math(EXPR _res "${_res} * 16")
    string(SUBSTRING "${HEX}" 0 1 NIBBLE)
    string(SUBSTRING "${HEX}" 1 -1 HEX)
    if (NIBBLE STREQUAL "A")
      math(EXPR _res "${_res} + 10")
    elseif (NIBBLE STREQUAL "B")
      math(EXPR _res "${_res} + 11")
    elseif (NIBBLE STREQUAL "C")
      math(EXPR _res "${_res} + 12")
    elseif (NIBBLE STREQUAL "D")
      math(EXPR _res "${_res} + 13")
    elseif (NIBBLE STREQUAL "E")
      math(EXPR _res "${_res} + 14")
    elseif (NIBBLE STREQUAL "F")
      math(EXPR _res "${_res} + 15")
    else()
      math(EXPR _res "${_res} + ${NIBBLE}")
    endif()

    string(LENGTH "${HEX}" _strlen)
  endwhile()

  set(${DEC} ${_res} PARENT_SCOPE)
endfunction()


if (OPENSSL_INCLUDE_DIR)
  if(OPENSSL_INCLUDE_DIR AND EXISTS "${OPENSSL_INCLUDE_DIR}/openssl/opensslv.h")
    file(STRINGS "${OPENSSL_INCLUDE_DIR}/openssl/opensslv.h" openssl_version_str
         REGEX "^#[\t ]*define[\t ]+OPENSSL_VERSION_NUMBER[\t ]+0x([0-9a-zA-Z])+.*")

    string(REGEX REPLACE "^.*OPENSSL_VERSION_NUMBER[\t ]+0x([0-9a-zA-Z])([0-9a-zA-Z][0-9a-zA-Z])([0-9a-zA-Z][0-9a-zA-Z])([0-9a-zA-Z][0-9a-zA-Z])([0-9a-zA-Z]).*$"
           "\\1;\\2;\\3;\\4;\\5" OPENSSL_VERSION_LIST "${openssl_version_str}")
    list(GET OPENSSL_VERSION_LIST 0 OPENSSL_VERSION_MAJOR)
    list(GET OPENSSL_VERSION_LIST 1 OPENSSL_VERSION_MINOR)
    from_hex("${OPENSSL_VERSION_MINOR}" OPENSSL_VERSION_MINOR)
    list(GET OPENSSL_VERSION_LIST 2 OPENSSL_VERSION_FIX)
    from_hex("${OPENSSL_VERSION_FIX}" OPENSSL_VERSION_FIX)
    list(GET OPENSSL_VERSION_LIST 3 OPENSSL_VERSION_PATCH)

    if (NOT OPENSSL_VERSION_PATCH STREQUAL "00")
      from_hex("${OPENSSL_VERSION_PATCH}" _tmp)
      math(EXPR OPENSSL_VERSION_PATCH_ASCII "${_tmp} + 96")
      unset(_tmp)
      string(ASCII "${OPENSSL_VERSION_PATCH_ASCII}" OPENSSL_VERSION_PATCH_STRING)
    endif ()

    set(OPENSSL_VERSION "${OPENSSL_VERSION_MAJOR}.${OPENSSL_VERSION_MINOR}.${OPENSSL_VERSION_FIX}${OPENSSL_VERSION_PATCH_STRING}")
  endif ()
endif ()

find_package_handle_standard_args(OpenSSL
  REQUIRED_VARS
    OPENSSL_LIBRARIES
    OPENSSL_INCLUDE_DIR
  VERSION_VAR
    OPENSSL_VERSION
  FAIL_MESSAGE
    "Could NOT find OpenSSL, try to set the path to OpenSSL root folder in the system variable OPENSSL_ROOT_DIR"
)


mark_as_advanced(
    OPENSSL_ROOT_DIR
    OPENSSL_INCLUDE_DIR
    OPENSSL_LIBRARIES
)