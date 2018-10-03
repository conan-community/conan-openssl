from conans.model.conan_file import ConanFile
from conans import CMake, tools
import os


class DefaultNameConan(ConanFile):
    name = "DefaultName"
    version = "0.1"
    settings = "os", "compiler", "arch", "build_type"
    generators = "cmake"

    def build(self):
        cmake = CMake(self)

        if self.settings.os == "Android":
            cmake.definitions["CONAN_LIBCXX"] = ""

        cmake.configure()
        cmake.build()

    def imports(self):
        self.copy(pattern="*.dll", dst="bin", src="bin", root_package="OpenSSL")
        self.copy(pattern="*.dylib", dst="bin", src="lib", root_package="OpenSSL")

    def test(self):
        if not tools.cross_building(self.settings):
            self.run("cd bin && .%sdigest" % os.sep)
        assert os.path.exists(os.path.join(self.deps_cpp_info["OpenSSL"].rootpath, "LICENSE"))
