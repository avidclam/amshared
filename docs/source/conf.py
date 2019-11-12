import os
import sys
sys.path.insert(0, os.path.abspath('../..'))
import amshared

project = amshared.__title__
author = amshared.__author__
copyright = amshared.__copyright__
release = amshared.__version__
version = '.'.join(release.split('.')[:2])
master_doc = 'index'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.autosummary'
]
templates_path = ['_templates']
exclude_patterns = []

html_theme = 'sphinx_rtd_theme'
#html_theme = 'bizstyle'
html_static_path = ['_static']

rst_epilog = """
.. |ProjectDesc| replace:: {project_desc}
.. |ProjectRelease| replace:: v{project_release}
""".format(project_desc=amshared.__description__,
           project_release=release)
