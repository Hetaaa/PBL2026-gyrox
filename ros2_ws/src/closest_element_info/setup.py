from setuptools import find_packages, setup

package_name = 'closest_element_info'

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
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
            'numpy'
        ],
    },
    entry_points={
        'console_scripts': [
            'closest_element_info = closest_element_info.closest_element_info:main',
            'emergency_zones = closest_element_info.closest_element_info:main',
            'emergency_zones_lidar = closest_element_info.closest_element_info:main',
        ],
    },
)
