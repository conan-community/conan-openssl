# -*- coding: utf-8 -*-

from conans.client import conan_api


def pre_export(output, conanfile, conanfile_path, reference, **kwargs):
    instance, _, _ = conan_api.Conan.factory()
    instance.remove("*", force=True)
