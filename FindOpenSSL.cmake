MESSAGE(STATUS "********* Conan FindOpenSSL wrapper! **********")

SET(OPENSSL_ROOT_DIR ${CONAN_OPENSSL_ROOT})
SET(OPENSSL_INCLUDE_DIR ${CONAN_INCLUDE_DIRS_OPENSSL})


if (DEFINED CMAKE_VERSION AND "${CMAKE_VERSION}" VERSION_LESS "3.7")
  include("${CONAN_OPENSSL_ROOT}/FindBoost_less_3.7.cmake")
else()
  include("${CONAN_OPENSSL_ROOT}/OriginalFindOpenSSL_3_8.cmake")
endif()
