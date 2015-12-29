import os
import platform
import sys

if __name__ == "__main__":
    
    os.system('conan export lasote/stable')
    
    def test(settings, visual_version=None):
        argv =  " ".join(sys.argv[1:])
        curdir = os.path.abspath(os.path.curdir)
        if visual_version:
            vcvars = 'call "%vs' +  str(visual_version) + '0comntools%../../VC/vcvarsall.bat"'
            param = "x86" if "arch=x86 " in settings else "amd64"
            command = '%s %s && conan test . %s %s' % (vcvars, param, settings, argv)
        else:
            command = 'conan test . %s %s' % (settings, argv)
        retcode = os.system(command)
        if retcode != 0:
            exit("Error while executing:\n\t %s" % command)


    if platform.system() == "Windows":
        for visual_version in [10, 12, 14]:
            compiler = '-s compiler="Visual Studio" -s compiler.version=%s ' % visual_version
            for arch in ["x86", "x86_64"]:
                if visual_version == 10 and arch=="x86_64":
                    continue
                # Static
                test(compiler + '-s arch='+arch+' -s build_type=Debug -s compiler.runtime=MDd -o OpenSSL:shared=False', visual_version)
                test(compiler + '-s arch='+arch+' -s build_type=Debug -s compiler.runtime=MTd -o OpenSSL:shared=False', visual_version)
                test(compiler + '-s arch='+arch+' -s build_type=Release -s compiler.runtime=MD -o OpenSSL:shared=False', visual_version)
                test(compiler + '-s arch='+arch+' -s build_type=Release -s compiler.runtime=MT -o OpenSSL:shared=False', visual_version)
        
                # Shared
                test(compiler + '-s arch='+arch+' -s build_type=Debug -s compiler.runtime=MDd -o OpenSSL:shared=True', visual_version)
                test(compiler + '-s arch='+arch+' -s build_type=Debug -s compiler.runtime=MTd -o OpenSSL:shared=True', visual_version)
                test(compiler + '-s arch='+arch+' -s build_type=Release -s compiler.runtime=MD -o OpenSSL:shared=True', visual_version)
                test(compiler + '-s arch='+arch+' -s build_type=Release -s compiler.runtime=MT -o OpenSSL:shared=True', visual_version)

    else:  # Compiler and version not specified, please set it in your home/.conan/conan.conf (Valid for Macos and Linux)
        if not os.getenv("TRAVIS", False):   
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
