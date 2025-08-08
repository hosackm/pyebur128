from setuptools import setup
from setuptools.command.build_py import build_py
from setuptools.errors import SetupError

import os
import shutil
import subprocess
import platform

if not os.path.exists("external/libebur128"):
    raise SetupError(
        "Couldn't find external/libebur128. Run: git submodule update --init --recursive"
    )


class CMakeBuild(build_py):
    def run(self):
        super().run()

        build_dir = os.path.abspath("build")
        os.makedirs(build_dir, exist_ok=True)

        subprocess.check_call(
            [
                "cmake",
                "-S",
                "external/libebur128",
                "-B",
                build_dir,
                "-DCMAKE_BUILD_TYPE=Release",
            ]
        )
        subprocess.check_call(["cmake", "--build", build_dir])

        extensions = {
            "Darwin": ".dylib",
            "Linux": ".so",
            "Windows": ".dll",
        }
        ext = extensions.get(platform.system())
        if not ext:
            raise SetupError(f"Unsupported platform: {platform.system()}")

        libname = f"libebur128{ext}"
        libsrc = os.path.join(build_dir, libname)
        libdst = os.path.join(self.build_lib, "pyebur128", libname)

        os.makedirs(os.path.dirname(libdst), exist_ok=True)
        shutil.copyfile(libsrc, libdst)


setup(
    name="pyebur128",
    version="0.1.0",
    packages=["pyebur128"],
    cmdclass={"build_py": CMakeBuild},
    include_package_data=True,
    package_data={"pyebur128": ["libebur128.dylib"]},
)
