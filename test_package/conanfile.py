from conans.model.conan_file import ConanFile
from conans import CMake, tools
import os


class DefaultNameConan(ConanFile):
    name = "DefaultName"
    version = "0.1"
    settings = "os", "compiler", "arch", "build_type"
    generators = "cmake"

    def _build_cmake(self, use_find_package):
        cmake = CMake(self)

        if self.settings.os == "Android":
            cmake.definitions["CONAN_LIBCXX"] = ""
        cmake.definitions["USE_FIND_PACKAGE"] = use_find_package

        cmake.configure()
        cmake.build()

    def build(self):
        self._build_cmake(use_find_package=True)
        self._build_cmake(use_find_package=False)

    def imports(self):
        self.copy(pattern="*.dll", dst="bin", src="bin", root_package="OpenSSL")
        self.copy(pattern="*.dylib", dst="bin", src="lib", root_package="OpenSSL")

    def test(self):
        if not tools.cross_building(self.settings):
            self.run("cd bin && .%sdigest" % os.sep)
        assert os.path.exists(os.path.join(self.deps_cpp_info["OpenSSL"].rootpath, "LICENSE"))
