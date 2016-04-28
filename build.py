from conan.packager import ConanMultiPackager


if __name__ == "__main__":
    builder = ConanMultiPackager()
    builder.add_common_builds(shared_option_name="OpenSSL:shared", pure_c=True)
    efence_builds = []
    for settings, options in builder.builds:
        efence_builds.append([settings, dict(options.items() + [('OpenSSL:no_electric_fence', True)])])
        efence_builds.append([settings, dict(options.items() + [('OpenSSL:no_electric_fence', False)])])
    builder.builds = efence_builds
    builder.run()
