# -*- coding: utf-8 -*-
#

import sys, os
sys.path.insert(0, os.path.abspath('../../'))
import holmium.core

extensions = ['sphinx.ext.autodoc', 'sphinx.ext.autosummary','sphinx.ext.doctest', 'sphinx.ext.intersphinx', 'sphinx.ext.todo', 'sphinx.ext.pngmath', 'sphinx.ext.ifconfig', 'sphinx.ext.viewcode']
templates_path = ['_templates']
source_suffix = '.rst'
master_doc = 'index'
project = u'holmium.core'
copyright = u'2013, Projectgoth Inc.'
version = release = holmium.core.__version__

exclude_patterns = []
#add_module_names = True
pygments_style = 'sphinx'

html_theme = 'sphinxdoc'
#html_theme_options = {}
#html_theme_path = []
html_title = "holmium"
#html_short_title = None
#html_logo = None
#html_favicon = None
html_static_path = ['_static']
#html_last_updated_fmt = '%b %d, %Y'
#html_use_smartypants = True
html_sidebars = {
           '**': ['globaltoc.html', 'sourcelink.html', 'searchbox.html'],
              'using/windows': ['windowssidebar.html', 'searchbox.html'],
              }
#html_additional_pages = {}
#html_domain_indices = True
#html_use_index = True
#html_split_index = False
#html_show_sourcelink = True
#html_show_sphinx = True
#html_show_copyright = True
htmlhelp_basename = 'holmiumcoredoc'

latex_documents = [
  ('index', 'holmiumcore.tex', u'holmium.core Documentation',
   u'Ali-Akber Saifee', 'manual'),
]
man_pages = [
    ('index', 'holmiumcore', u'holmium.core Documentation',
     [u'Ali-Akber Saifee'], 1)
]

texinfo_documents = [
  ('index', 'holmiumcore', u'holmium.core Documentation',
   u'Ali-Akber Saifee', 'holmiumcore', 'One line description of project.',
   'Miscellaneous'),
]
autodoc_default_flags = ["undoc-members","show-inheritance"]
intersphinx_mapping = {'http://docs.python.org/': None, "http://selenium-python.readthedocs.org/en/latest":None}