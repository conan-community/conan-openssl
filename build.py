#!/usr/bin/env python
# -*- coding: utf-8 -*-

from cpt.packager import ConanMultiPackager
from cpt.ci_manager import is_azure_pipelines


if __name__ == "__main__":
    builder = ConanMultiPackager()
    builder.add_common_builds(pure_c=True)
    builder.run()

    if is_azure_pipelines():
        from conans.client import conan_api

        instance, _, _ = conan_api.Conan.factory()
        instance.remove("*", force=True)
