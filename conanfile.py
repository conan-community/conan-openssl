from conans import ConanFile
from conans import tools
import os


class OpenSSLConan(ConanFile):
    name = "OpenSSL"
    version = "1.0.2l"
    settings = "os", "compiler", "arch", "build_type"
    url = "http://github.com/lasote/conan-openssl"
    license = "The current OpenSSL licence is an 'Apache style' license: https://www.openssl.org/source/license.html"
    description = "OpenSSL is an open source project that provides a robust, commercial-grade, and full-featured " \
                  "toolkit for the Transport Layer Security (TLS) and Secure Sockets Layer (SSL) protocols"
    # https://github.com/openssl/openssl/blob/OpenSSL_1_0_2l/INSTALL
    options = {"no_threads": [True, False],
               "no_zlib": [True, False],
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

    # When a new version is available they move the tar.gz to old/ location
    source_tgz = "https://www.openssl.org/source/openssl-%s.tar.gz" % version
    source_tgz_old = "https://www.openssl.org/source/old/1.0.2/openssl-%s.tar.gz" % version
    
    def build_requirements(self):
        # useful for example for conditional build_requires
        if self.settings.os == "Windows":
            self.build_requires("strawberryperl/5.26.0@conan/stable")
            self.build_requires("nasm/2.13.01@conan/stable")

    def source(self):
        self.output.info("Downloading %s" % self.source_tgz)
        try:
            tools.download(self.source_tgz_old, "openssl.tar.gz")
        except:
            tools.download(self.source_tgz, "openssl.tar.gz")
        tools.unzip("openssl.tar.gz")
        tools.check_sha256("openssl.tar.gz", "ce07195b659e75f4e1db43552860070061f156a98bb37b672b101ba6e3ddf30c")
        os.unlink("openssl.tar.gz")

    def configure(self):
        del self.settings.compiler.libcxx

    def requirements(self):
        if not self.options.no_zlib:
            self.requires("zlib/1.2.11@conan/stable")

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
        if "zlib" in self.deps_cpp_info.deps:
            zlib_info = self.deps_cpp_info["zlib"]
            include_path = zlib_info.include_paths[0]
            if self.settings.os == "Windows":
                lib_path = "%s/%s.lib" % (zlib_info.lib_paths[0], zlib_info.libs[0])
            else:
                lib_path = zlib_info.lib_paths[0]  # Just path, linux will find the right file
            config_options_string += ' --with-zlib-include="%s"' % include_path
            config_options_string += ' --with-zlib-lib="%s"' % lib_path

            tools.replace_in_file("./openssl-%s/Configure" % self.version, "::-lefence::", "::")
            tools.replace_in_file("./openssl-%s/Configure" % self.version, "::-lefence ", "::")
            self.output.info("=====> Options: %s" % config_options_string)

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

    def run_in_src(self, command, show_output=False):
        if not show_output and self.settings.os != "Windows":
            command += ' | while read line; do printf "%c" .; done'
        with tools.chdir(self.subfolder):
            self.run(command)
        self.output.writeln(" ")

    def linux_build(self, config_options_string):
        m32_suff = " -m32" if self.settings.arch == "x86" else ""
        if self.settings.build_type == "Debug":
            config_options_string = "-d no-asm -g3 -O0 -fno-omit-frame-pointer " \
                                    "-fno-inline-functions" + config_options_string

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
        self.run_in_src("perl --version")
        
        self.output.warn("----------CONFIGURING OPENSSL FOR WINDOWS. %s-------------" % self.version)
        debug = "debug-" if self.settings.build_type == "Debug" else ""
        arch = "32" if self.settings.arch == "x86" else "64A"
        configure_type = debug + "VC-WIN" + arch
        no_asm = "no-asm" if self.options.no_asm else ""
        # Will output binaries to ./binaries
        vcvars = tools.vcvars_command(self.settings)
        config_command = "%s && perl Configure %s %s --prefix=../binaries" % (vcvars, configure_type, no_asm)
        whole_command = "%s %s" % (config_command, config_options_string)
        self.output.warn(whole_command)
        self.run_in_src(whole_command)

        if not self.options.no_asm and self.settings.arch == "x86":
            # The 64 bits builds do not require the do_nasm
            # http://p-nand-q.com/programming/windows/building_openssl_with_visual_studio_2013.html
            self.run_in_src(r"%s && ms\do_nasm" % vcvars)
        else:
            if arch == "64A":
                self.run_in_src(r"%s && ms\do_win64a" % vcvars)
            else:
                self.run_in_src(r"%s && ms\do_ms" % vcvars)
        runtime = self.settings.compiler.runtime
        # Replace runtime in ntdll.mak and nt.mak
        tools.replace_in_file("./openssl-%s/ms/ntdll.mak" % self.version, "/MD ", "/%s " % runtime)
        tools.replace_in_file("./openssl-%s/ms/nt.mak" % self.version, "/MT ", "/%s " % runtime)
        tools.replace_in_file("./openssl-%s/ms/ntdll.mak" % self.version, "/MDd ", "/%s " % runtime)
        tools.replace_in_file("./openssl-%s/ms/nt.mak" % self.version, "/MTd ", "/%s " % runtime)

        make_command = "nmake -f ms\\ntdll.mak" if self.options.shared else "nmake -f ms\\nt.mak "
        self.output.warn("----------MAKE OPENSSL %s-------------" % self.version)
        self.run_in_src("%s && %s" % (vcvars, make_command))
        self.run_in_src("%s && %s install" % (vcvars, make_command))
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
        # Copy the license files
        self.copy("%s/LICENSE" % self.subfolder, keep_path=False)
        self.copy(pattern="*applink.c", dst="include/openssl/", keep_path=False)
        if self.settings.os == "Windows" and self.settings.compiler == "Visual Studio":
            self._copy_visual_binaries()
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
        
        suffix = str(self.settings.compiler.runtime)
        lib_path = os.path.join(self.package_folder, "lib")
        current_ssleay = os.path.join(lib_path, "ssleay32%s.lib" % suffix)
        current_libeay = os.path.join(lib_path, "libeay32%s.lib" % suffix)
        os.rename(current_ssleay, os.path.join(lib_path, "ssleay32.lib"))
        os.rename(current_libeay, os.path.join(lib_path, "libeay32.lib"))

    def package_info(self):
        if self.settings.compiler == "Visual Studio":
            self.cpp_info.libs = ["ssleay32", "libeay32", "crypt32", "msi", "ws2_32"]
        elif self.settings.os == "Linux":
            self.cpp_info.libs = ["ssl", "crypto", "dl"]
        else:
            self.cpp_info.libs = ["ssl", "crypto"]
