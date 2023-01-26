# setup.py is required for local installation of the duHast package through:
# ipy -m pip install -e .

from setuptools import setup
from setuptools import find_packages
setup(
    # ...
    packages=find_packages(),
    package_dir={"": "src"}
    # ...
)