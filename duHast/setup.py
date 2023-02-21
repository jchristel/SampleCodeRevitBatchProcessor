# setup.py is required for local installation of the duHast package through:
# ipy -m pip install -e .

from setuptools import setup
from setuptools import find_packages

from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    # ...
    packages=find_packages(),
    package_dir={"": "src"},
    # ...
    long_description=long_description,
    long_description_content_type='text/markdown'
)