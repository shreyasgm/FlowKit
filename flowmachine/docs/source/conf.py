# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# FlowMachine documentation build configuration file, created by
# sphinx-quickstart on Thu May 11 22:37:12 2017.
#
# This file is execfile()d with the current directory set to its
# containing dir.
#
# Note that not all possible configuration values are present in this
# autogenerated file.
#
# All configuration values have a default; values that are commented out
# serve to show the default.

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys


project_root = os.path.dirname(os.path.abspath(__file__))
pymodule_path = os.path.join(project_root, "..", "..")
sys.path.insert(0, pymodule_path)


def setup(app):
    app.add_stylesheet("flowminder.css")


# -- General configuration ------------------------------------------------

# If your documentation needs a minimal Sphinx version, state it here.
#
# needs_sphinx = '1.0'

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.coverage",
    "sphinx.ext.mathjax",
    "sphinx.ext.viewcode",
    "sphinx.ext.autosummary",
    "nbsphinx",
    "IPython.sphinxext.ipython_console_highlighting",
    "numpydoc",
    "m2r",
]

mathjax_path = "https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.1/MathJax.js?config=TeX-AMS-MML_HTMLorMML"

# Don't re-execute Jupyter notebooks when building the docs.
nbsphinx_execute = "always"
nbsphinx_timeout = 60  # Give notebooks more time to run

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
#
source_suffix = [".rst", ".md"]

# The master toctree document.
master_doc = "index"

# General information about the project.
project = "FlowMachine"
copyright = "2017, Flowminder Foundation"
author = "Simon Tudge / Flowminder Analysts"

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#
# The short X.Y version.
version = ""
# The full version, including alpha/beta/rc tags.
release = ""

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = None

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This patterns also effect to html_static_path and html_extra_path
exclude_patterns = ["_build", "**.ipynb_checkpoints"]

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = "sphinx"

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = False

# -- Options for HTML output ----------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#

# Adds an HTML table visitor to apply Bootstrap table classes
# html_translator_class = 'guzzle_sphinx_theme.HTMLTranslator'
# html_theme_path = guzzle_sphinx_theme.html_theme_path()
html_theme = "basicstrap"
master_doc = "index"

# Register the theme as an extension to generate a sitemap.xml
extensions.append("sphinxjp.themes.basicstrap")

# Guzzle theme options (see theme.conf for more information)
html_theme_options = {
    "inner_theme": True,
    "inner_theme_name": "bootswatch-paper",
    "googlewebfont": True,
    "googlewebfont_url": "http://fonts.googleapis.com/css?family=Merriweather:300,300i,400,400i,700,700i,900,900i|Roboto:300,300i,400,400i,500,700,900",
    "googlewebfont_style": "font-family: 'Roboto', sans-serif",
    "h1_size": "2.0em",
    "h2_size": "1.6em",
    "h3_size": "1.3em",
    "h4_size": "1em",
    "content_fixed": True,
    "content_width": "1000px",
    "row_fixed": False,
    "header_inverse": True,
    "header_searchbox": True,
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]


# -- Options for HTMLHelp output ------------------------------------------

# Output file base name for HTML help builder.
htmlhelp_basename = "flowmachinedoc"


# -- Options for LaTeX output ---------------------------------------------

latex_elements = {
    # The paper size ('letterpaper' or 'a4paper').
    #
    # 'papersize': 'letterpaper',
    # The font size ('10pt', '11pt' or '12pt').
    #
    # 'pointsize': '10pt',
    # Additional stuff for the LaTeX preamble.
    #
    # 'preamble': '',
    # Latex figure (float) alignment
    #
    # 'figure_align': 'htbp',
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
    (master_doc, "flowmachine.tex", "FlowMachine", "Project analysts", "manual")
]


# -- Options for manual page output ---------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [(master_doc, "flowmachine", "FlowMachine", [author], 1)]


# -- Options for Texinfo output -------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    (
        master_doc,
        "flowmachine",
        "FlowMachine",
        author,
        "flowmachine",
        "toolkit for the analysis of Call Detail Records (CDRs)",
        "Miscellaneous",
    )
]

numpydoc_show_class_members = False