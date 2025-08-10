from skbuild import setup

setup(
    name="pyebur128",
    version="0.1.0",
    packages=["pyebur128"],
    package_dir={"": "src"},
    cmake_install_dir="src/pyebur128",
)
