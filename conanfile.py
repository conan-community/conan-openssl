from conans import ConanFile
from conans import tools, AutoToolsBuildEnvironment
import os


class OpenSSLConan(ConanFile):
    name = "OpenSSL"
    version = "1.0.2k"
    settings = "os", "compiler", "arch", "build_type"
    url = "http://github.com/lasote/conan-openssl"
    license = "The current OpenSSL licence is an 'Apache style' license: https://www.openssl.org/source/license.html"
    description = "OpenSSL is an open source project that provides a robust, commercial-grade, and full-featured " \
                  "toolkit for the Transport Layer Security (TLS) and Secure Sockets Layer (SSL) protocols"
    # https://github.com/openssl/openssl/blob/OpenSSL_1_0_2c/INSTALL
    options = {"no_threads": [True, False],
               "no_electric_fence": [True, False],
               "no_zlib": [True, False],
               "zlib_dynamic": [True, False],
               "shared": [True, False],
               "no_asm": [True, False],
               "386": [True, False],
               "no_sse2": [True, False],
               "no_bf": [True, False],
               "no_cast": [True, False],
               "no_des": [True, False],
               "no_dh": [True, False],
               "no_dsa": [True, False],
               "no_hmac": [True, False],
               "no_md2": [True, False],
               "no_md5": [True, False],
               "no_mdc2": [True, False],
               "no_rc2": [True, False],
               "no_rc4": [True, False],
               "no_rc5": [True, False],
               "no_rsa": [True, False],
               "no_sha": [True, False]}
    default_options = "=False\n".join(options.keys()) + "=False"

    exports = ("win_bin/*", "readme.txt", "FindOpenSSL.cmake")

    # When a new version is avaiable they move the tar.gz to old/ location
    source_tgz = "https://www.openssl.org/source/openssl-%s.tar.gz" % version
    source_tgz_old = "https://www.openssl.org/source/old/1.0.2/openssl-%s.tar.gz" % version
    counter_config = 0

    def source(self):
        self.output.info("Downloading %s" % self.source_tgz)
        try:
            tools.download(self.source_tgz_old, "openssl.tar.gz")
            tools.unzip("openssl.tar.gz", ".")
        except:
            tools.download(self.source_tgz, "openssl.tar.gz")
            tools.unzip("openssl.tar.gz", ".")

        tools.check_sha256("openssl.tar.gz", "6b3977c61f2aedf0f96367dcfb5c6e578cf37e7b8d913b4ecb6643c3cb88d8c0")
        os.unlink("openssl.tar.gz")

    def config_options(self):
        if not self.options.no_electric_fence and self.settings.os == "Linux":
            self.options["electric-fence"].shared = self.options.shared
        if not self.options.no_zlib:
            self.options["zlib"].shared = self.options.zlib_dynamic

    def configure(self):
        del self.settings.compiler.libcxx

    def requirements(self):
        if not self.options.no_electric_fence and self.settings.os == "Linux":
            private = False if self.options.shared else True
            self.requires.add("electric-fence/2.2.0@lasote/stable", private=private)
        else:
            if "electric-fence" in self.requires:
                del self.requires["electric-fence"]

        if not self.options.no_zlib:
            self.requires.add("zlib/1.2.8@lasote/stable", private=False)
        else:
            if "zlib" in self.requires:
                del self.requires["zlib"]

    @property
    def subfolder(self):
        return "openssl-%s" % self.version

    def build(self):
        """
            For Visual Studio (tried with 2010) compiling need:
             - perl: http://www.activestate.com/activeperl/downloads
             - nasm: http://www.nasm.us/
            Put perl and nasm bin folder in USER PATH (not system path, so the visual 2010 command system symbol can find it)
            Open the visual 2010 command system symbol and run conan.
            Here are good page explaining it: http://hostagebrain.blogspot.com.es/2015/04/build-openssl-on-windows.html
        """
        config_options_string = ""
        if self.deps_cpp_info.include_paths:
            include_path = self.deps_cpp_info["zlib"].include_paths[0]
            if self.settings.os == "Windows":
                lib_path = self.deps_cpp_info["zlib"].lib_paths[0] + "/" + self.deps_cpp_info["zlib"].libs[
                    0] + ".lib"  # Concrete lib file
            else:
                lib_path = self.deps_cpp_info["zlib"].lib_paths[0]  # Just path, linux will find the right file
            config_options_string += ' --with-zlib-include="%s"' % include_path
            config_options_string += ' --with-zlib-lib="%s"' % lib_path
            # EFENCE LINK
            if "electric-fence" in self.requires:
                libs = " ".join(["-l%s" % lib for lib in self.deps_cpp_info["electric-fence"].libs])
                config_options_string += ' -L"%s" -I"%s" %s' % (self.deps_cpp_info["electric-fence"].lib_paths[0],
                                                                self.deps_cpp_info["electric-fence"].include_paths[0],
                                                                libs)
            else:
                tools.replace_in_file("./openssl-%s/Configure" % self.version, "::-lefence::", "::")
                tools.replace_in_file("./openssl-%s/Configure" % self.version, "::-lefence ", "::")
            self.output.warn("=====> Options: %s" % config_options_string)

        for option_name in self.options.values.fields:
            activated = getattr(self.options, option_name)
            if activated:
                self.output.info("Activated option! %s" % option_name)
                config_options_string += " %s" % option_name.replace("_", "-")

        if self.settings.os == "Linux":
            self.linux_build(config_options_string)
        elif self.settings.os == "Macos":
            self.osx_build(config_options_string)
        elif self.settings.compiler == "Visual Studio":
            self.visual_build(config_options_string)
        elif self.settings.os == "Windows" and self.settings.compiler == "gcc":
            self.mingw_build(config_options_string)

        self.output.info("----------BUILD END-------------")
        return

    def run_in_src(self, command, show_output=False):
        if not show_output and self.settings.os != "Windows":
            command += ' | while read line; do printf "%c" .; done'
        with tools.chdir(self.subfolder):
            self.run(command)
        self.output.writeln(" ")

    def linux_build(self, config_options_string):
        m32_suff = " -m32" if self.settings.arch == "x86" else ""
        if self.settings.build_type == "Debug":
            config_options_string = "-d " + config_options_string

        m32_pref = "setarch i386" if self.settings.arch == "x86" else ""
        config_line = "%s ./config -fPIC %s %s" % (m32_pref, config_options_string, m32_suff)
        self.output.warn(config_line)
        self.run_in_src(config_line)
        self.run_in_src("make depend")
        self.output.warn("----------MAKE OPENSSL %s-------------" % self.version)
        self.run_in_src("make")

    def osx_build(self, config_options_string):
        m32_suff = " -m32" if self.settings.arch == "x86" else ""
        if self.settings.arch == "x86_64":
            command = "./Configure darwin64-x86_64-cc %s" % config_options_string
        else:
            command = "./config %s %s" % (config_options_string, m32_suff)

        self.run_in_src(command)
        # REPLACE -install_name FOR FOLLOW THE CONAN RULES,
        # DYNLIBS IDS AND OTHER DYNLIB DEPS WITHOUT PATH, JUST THE LIBRARY NAME
        old_str = 'SHAREDFLAGS="$$SHAREDFLAGS -install_name $(INSTALLTOP)/$(LIBDIR)/$$SHLIB$'
        new_str = 'SHAREDFLAGS="$$SHAREDFLAGS -install_name $$SHLIB$'
        tools.replace_in_file("./openssl-%s/Makefile.shared" % self.version, old_str, new_str)
        self.output.warn("----------MAKE OPENSSL %s-------------" % self.version)
        self.run_in_src("make")

    def visual_build(self, config_options_string):
        self.output.warn("----------CONFIGURING OPENSSL FOR WINDOWS. %s-------------" % self.version)
        debug = "debug-" if self.settings.build_type == "Debug" else ""
        arch = "32" if self.settings.arch == "x86" else "64A"
        configure_type = debug + "VC-WIN" + arch
        # Will output binaries to ./binaries
        config_command = "perl Configure %s no-asm --prefix=../binaries" % configure_type
        whole_command = "%s %s" % (config_command, config_options_string)
        self.output.warn(whole_command)
        self.run_in_src(whole_command)

        if self.options.no_asm:
            self.run_in_src("ms\do_nasm")

        if arch == "64A":
            self.run_in_src("ms\do_win64a")
        else:
            self.run_in_src("ms\do_ms")
        runtime = self.settings.compiler.runtime
        # Replace runtime in ntdll.mak and nt.mak
        tools.replace_in_file("./openssl-%s/ms/ntdll.mak" % self.version, "/MD ", "/%s " % runtime)
        tools.replace_in_file("./openssl-%s/ms/nt.mak" % self.version, "/MT ", "/%s " % runtime)
        tools.replace_in_file("./openssl-%s/ms/ntdll.mak" % self.version, "/MDd ", "/%s " % runtime)
        tools.replace_in_file("./openssl-%s/ms/nt.mak" % self.version, "/MTd ", "/%s " % runtime)

        self.output.warn(os.curdir)
        vcvars = tools.vcvars_command(self.settings)
        vcvars = "%s && " % vcvars if vcvars else " "
        make_command = "nmake -f ms\\ntdll.mak" if self.options.shared else "nmake -f ms\\nt.mak "
        self.output.warn("----------MAKE OPENSSL %s-------------" % self.version)
        self.run_in_src("%s%s" % (vcvars, make_command))
        self.run_in_src("%s%s install" % (vcvars, make_command))
        # Rename libs with the arch
        renames = {"./binaries/lib/libeay32.lib": "./binaries/lib/libeay32%s.lib" % runtime,
                   "./binaries/lib/ssleay32.lib": "./binaries/lib/ssleay32%s.lib" % runtime}
        for old, new in renames.items():
            if os.path.exists(old):
                os.rename(old, new)

    def mingw_build(self, config_options_string):
        config_options_string = tools.unix_path(config_options_string)
        if self.settings.build_type == "Debug":
            config_options_string = "-d " + config_options_string
        if self.settings.arch == "x86":
            config_line = "./Configure mingw %s" % config_options_string
        else:
            config_line = "./Configure mingw64 %s" % config_options_string
        self.output.warn(config_line)
        with tools.chdir(self.subfolder):
            tools.run_in_windows_bash(self, config_line)
            self.output.warn("----------MAKE OPENSSL %s-------------" % self.version)
            tools.run_in_windows_bash(self, "make depend")
            tools.run_in_windows_bash(self, "make")

    def package(self):
        self.copy("FindOpenSSL.cmake", ".", ".")
        self.copy(pattern="*applink.c", dst="include/openssl/", keep_path=False)
        if self.settings.os == "Windows" and self.settings.compiler == "Visual Studio":
            self._copy_visual_binaries()
            if self.settings.compiler == "gcc":
                self.copy("*.a", "lib", keep_path=False)
            self.copy(pattern="*.h", dst="include/openssl/", src="binaries/include/", keep_path=False)
        else:
            if self.options.shared:
                self.copy(pattern="*libcrypto*.dylib", dst="lib", keep_path=False)
                self.copy(pattern="*libssl*.dylib", dst="lib", keep_path=False)
                self.copy(pattern="*libcrypto.so*", dst="lib", keep_path=False)
                self.copy(pattern="*libssl.so*", dst="lib", keep_path=False)
            else:
                self.copy("*.a", "lib", keep_path=False)
            self.copy(pattern="%s/include/*" % self.subfolder, dst="include/openssl/", keep_path=False)

    def _copy_visual_binaries(self):
        self.copy(pattern="*.lib", dst="lib", src="binaries/lib", keep_path=False)
        self.copy(pattern="*.dll", dst="bin", src="binaries/bin", keep_path=False)
        self.copy(pattern="*.dll", dst="bin", src="binaries/bin", keep_path=False)

    def package_info(self):
        if self.settings.compiler == "Visual Studio":
            suffix = str(self.settings.compiler.runtime)
            self.cpp_info.libs = ["ssleay32" + suffix, "libeay32" + suffix, "crypt32", "msi"]
        elif self.settings.os == "Linux":
            self.cpp_info.libs = ["ssl", "crypto", "dl"]
        else:
            self.cpp_info.libs = ["ssl", "crypto"]
