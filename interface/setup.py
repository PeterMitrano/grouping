from setuptools import setup

setup(
    name='interface',
    packages=['interface'],
    include_package_data=True,
    install_requires=[
        'flask',
        'colorama'
    ],
)