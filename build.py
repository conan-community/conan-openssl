import os
from conan.packager import ConanMultiPackager
import sys
import platform
from copy import copy

def add_visual_builds(builder, visual_version, arch):
    if visual_version == 10 and arch == "x86_64":
        return
    base_set = {"compiler": "Visual Studio", 
                "compiler.version": visual_version, "arch": arch}
    sets = []
    sets.append({"build_type": "Debug", "compiler.runtime": "MDd"})
    sets.append({"build_type": "Debug", "compiler.runtime": "MTd"})
    sets.append({"build_type": "Release", "compiler.runtime": "MD"})
    sets.append({"build_type": "Release", "compiler.runtime": "MT"})
    
    for setting in sets:
       builder.add(copy(base_set).update(setting), {"OpenSSL:shared": False})
       builder.add(copy(base_set).update(setting), {"OpenSSL:shared": True})
       
def add_other_builds(builder):
    # Not specified compiler or compiler version, will use the auto detected     
    for arch in ["x86", "x86_64"]:
        for shared in [True, False]:
            for build_type in ["Debug", "Release"]:
                builder.add({"arch":arch, "build_type": build_type}, {"OpenSSL:shared": shared})
           
def get_builder(username, channel):
    args = " ".join(sys.argv[1:])
    builder = ConanMultiPackager(args, username, channel)
    if platform.system() == "Windows":
        for visual_version in [10, 12, 14]:
            for arch in ["x86", "x86_64"]:
                add_visual_builds(builder, visual_version, arch)
    else:
        add_other_builds(builder)
    
    return builder
        
if __name__ == "__main__":
    channel = os.getenv("CONAN_CHANNEL", "testing")
    username = os.getenv("CONAN_USERNAME", "lasote")
    current_page = os.getenv("CONAN_CURRENT_PAGE", 1)
    total_pages = os.getenv("CONAN_TOTAL_PAGES", 1)
    
    builder = get_builder(username, channel)
    builder.pack(current_page, total_pages)
    
    if os.getenv("CONAN_UPLOAD", False) and os.getenv("CONAN_REFERENCE") and os.getenv("CONAN_PASSWORD"):
        reference = os.getenv("CONAN_REFERENCE")
        builder.upload_packages(reference, os.getenv("CONAN_PASSWORD"))
