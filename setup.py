"""setup.py"""

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="jupitotools",
    version="0.0.1",
    author="Jussi Toivonen",
    author_email="jupito@iki.fi",
    description="Miscellaneous tools by jupito",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'Click',
    ],
    # entry_points={
    #     'console_scripts': [
    #         'scrappy = jupitotools.net.scrappy:cli',
    #         'abbr-path = jupitotools.files:cli_abbr_path',
    #         'monday = jupitotools.time:cli_monday',
    #         'cute-hours = jupitotools.time:cli_cute_hours',
    #         'jwhen = jupitotools.time:cli_jwhen',
    #         'probemedia = jupitotools.media.probe:cli_probemedia',
    #         'ylemedia = jupitotools.media.ylemedia:cli_ylemedia',
    #     ],
    # },
    entry_points='''
[console_scripts]

abbr-path = jupitotools.files:cli_abbr_path

scrappy = jupitotools.net.scrappy:cli

monday = jupitotools.time:cli_monday
cute-hours = jupitotools.time:cli_cute_hours

jwhen = jupitotools.jwhen:cli_jwhen
milloin = jupitotools.milloin:cli

probemedia = jupitotools.media.probe:cli_probemedia
ylemedia = jupitotools.media.ylemedia:cli_ylemedia

read_vcards_from_dump = jupitotools.contacts:cli_read_vcards_from_dump
    ''',
)
