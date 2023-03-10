# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
duHastPathAPI = os.path.abspath('../../duHast/src/duHast/APISamples')
duHastPathData = os.path.abspath('../../duHast/src/duHast/DataSamples')
duHastPathUI = os.path.abspath('../../duHast/src/duHast/UI')
duHastPathUtils = os.path.abspath('../../duHast/src/duHast/Utilities')
samplePathBAT = os.path.abspath('../../Samples/BAT')
samplePathFlows = os.path.abspath('../../Samples/Flows')
samplePathUI = os.path.abspath('../../Samples/UI')
samplePathShapely = os.path.abspath('../../Samples/Shapely')

sys.path += [
    duHastPathAPI, 
    duHastPathData, 
    duHastPathUI,
    duHastPathUtils,
    samplePathBAT, 
    samplePathFlows,
    samplePathUI,
    samplePathShapely
]
#sys.path.insert(0, os.path.abspath('../..'))

# web layout theme
import sphinx_adc_theme

# -- Project information -----------------------------------------------------

project = 'Sample Code Revit Batch Processor'
copyright = '2023, Jan Christel'
author = 'Jan Christel'

# The full version, including alpha/beta/rc tags
# need to be in double high commas for bumpver to recognize this a the version number
release = "0.0.4"


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.githubpages',
    'sphinx.ext.autosummary'
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []

# mocking clr and system imports
# also includes RevitFamilyLoadOption module since class defined in there inherits from an AutoDesk API class
# which is tripping sphinx
#, 'RevitFamilyLoadOption'
autodoc_mock_imports = ["clr", 'System', 'Autodesk', 'numpy', 'shapely', 'wpf','revit_script_util','revit_file_util','script_util']

# include __init__ docs in classes
autoclass_content = 'both'

# make sure code is document in order of source code
autodoc_default_options = {
    'member-order': 'bysource'
}
# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
#html_theme = 'alabaster'
html_theme = 'sphinx_adc_theme'
html_theme_path = [sphinx_adc_theme.get_html_theme_path()]

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']


# If true, the current module name will be prepended to all description
# unit titles (such as .. function::).
add_module_names = True