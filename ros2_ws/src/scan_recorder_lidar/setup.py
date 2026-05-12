from setuptools import find_packages, setup

package_name = 'scan_recorder_lidar'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='nano',
    maintainer_email='nano@todo.todo',
    description='Record /scan data to CSV and SQLite.',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'scan_recorder = scan_recorder_lidar.scan_recorder:main',
        ],
    },
)
