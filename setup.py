import os
from setuptools import setup

long_description = "ArcSight Common Event Format library"
if os.path.exists("README.md"):
    long_description = open("README.md", "r").read()

setup(
    name="cefevent",
    packages=["cefevent"],
    version="0.5.5",
    description="ArcSight Common Event Format library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Henrique Goncalves",
    author_email="kamus@hadenes.io",
    url="https://github.com/kamushadenes/cefevent",
    download_url="https://github.com/kamushadenes/cefevent/tarball/0.5.5",
    keywords=["logging", "cef", "arcsight", "event", "security"],
)
