from codecs import open
from os import path

# Always prefer setuptools over distutils
from setuptools import find_packages, setup

here = path.abspath(path.dirname(__file__))
about = {}
with open(path.join(here, "bk_monitor_report", "__version__.py"), "r") as f:
    exec(f.read(), about)

long_description = "custom reporter python sdk for bk-monitor"
version = about["__version__"]

setup(
    name="bk-monitor-report",
    version=version,
    description="bk-monitor-report",  # noqa
    long_description=long_description,
    url="https://github.com/TencentBlueKing/bk-monitor-report",
    author="TencentBlueKing",
    author_email="contactus_bk@tencent.com",
    include_package_data=True,
    packages=find_packages(),
    install_requires=[
        "requests>=2.20.0",
        "prometheus-client>=0.9.0,<1.0.0",
    ],
    zip_safe=False,
)
