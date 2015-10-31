import os
import hashlib
import shutil
import platform
import sys


def test(arguments):
    command = "conan test %s" % arguments
    retcode = os.system(command)
    if retcode != 0:
        exit("Error while executing:\n\t %s" % command)

if __name__ == "__main__":
    channel = "lasote/stable"
    
    os.system('conan export %s' % channel)

    if platform.system() == "Windows":
        if len(sys.argv) != 2 or sys.argv[1] not in ["x86", "x86_64"]:
            print("Please, specify x86 or x86_64 as a parameter")
            exit()

        arch = sys.argv[1]
        print("Verify that you are running a %s visual console" % arch)
        raw_input("Press Enter to continue...")

        compiler = '-s compiler="Visual Studio" -s compiler.version=12 '
        # Static
        test(compiler + '-s arch='+arch+' -s build_type=Debug -s compiler.runtime=MDd -o OpenSSL:shared=False')
        test(compiler + '-s arch='+arch+' -s build_type=Debug -s compiler.runtime=MTd -o OpenSSL:shared=False')
        test(compiler + '-s arch='+arch+' -s build_type=Release -s compiler.runtime=MD -o OpenSSL:shared=False')
        test(compiler + '-s arch='+arch+' -s build_type=Release -s compiler.runtime=MT -o OpenSSL:shared=False')

        # Shared
        test(compiler + '-s arch='+arch+' -s build_type=Debug -s compiler.runtime=MDd -o OpenSSL:shared=True')
        test(compiler + '-s arch='+arch+' -s build_type=Debug -s compiler.runtime=MTd -o OpenSSL:shared=True')
        test(compiler + '-s arch='+arch+' -s build_type=Release -s compiler.runtime=MD -o OpenSSL:shared=True')
        test(compiler + '-s arch='+arch+' -s build_type=Release -s compiler.runtime=MT -o OpenSSL:shared=True')

    else:  # Compiler and version not specified, please set it in your home/.conan/conan.conf (Valid for Macos and Linux)
        if "travis" not in channel:
            # Static x86
            test('-s arch=x86 -s build_type=Debug -o OpenSSL:shared=False')
            test('-s arch=x86 -s build_type=Release -o OpenSSL:shared=False')
    
            # Shared x86
            test('-s arch=x86 -s build_type=Debug -o OpenSSL:shared=True')
            test('-s arch=x86 -s build_type=Release -o OpenSSL:shared=True')

        # Static x86_64
        test('-s arch=x86_64 -s build_type=Debug -o OpenSSL:shared=False')
        test('-s arch=x86_64 -s build_type=Release -o OpenSSL:shared=False')

        # Shared x86_64
        test('-s arch=x86_64 -s build_type=Debug -o OpenSSL:shared=True')
        test('-s arch=x86_64 -s build_type=Release -o OpenSSL:shared=True')
