from glob import glob
import os

from setuptools import find_packages, setup

package_name = "project_bringup"

setup(
    name=package_name,
    version="0.1.0",
    packages=find_packages(exclude=("test",)),
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        (os.path.join("share", package_name), ["package.xml"]),
        (os.path.join("share", package_name, "launch"), glob("launch/*.py")),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="Phoenix Team",
    maintainer_email="admin@phoenixslam.com",
    description="Main system bringup orchestrator with health checks for all subsystems",
    license="Apache-2.0",
    entry_points={},
)
