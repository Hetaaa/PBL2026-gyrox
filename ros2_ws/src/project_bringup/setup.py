from glob import glob
import os

from setuptools import find_packages, setup

package_name = "slam"

setup(
    name=package_name,
    version="0.1.0",
    packages=find_packages(exclude=("test",)),
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        (os.path.join("share", package_name), ["package.xml"]),
        (os.path.join("share", package_name, "launch"), glob("launch/*.py")),
        (os.path.join("share", package_name, "config"), glob("config/*.yaml")),
        (os.path.join("share", package_name, "config", "odom"), glob("config/odom/*.yaml")),
        (os.path.join("share", package_name, "config", "slam"), glob("config/slam/*.yaml")),
        (os.path.join("share", package_name, "urdf"), glob("urdf/*")),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="Phoenix Team",
    maintainer_email="admin@phoenixslam.com",
    description="Single-package bringup for one Intel RealSense D435i SLAM stack",
    license="Apache-2.0",
    entry_points={
        "console_scripts": [
            "imu_transformer = project_bringup.imu_transformer:main",
        ],
    },
)
