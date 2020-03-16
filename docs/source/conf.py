import alabaster
import hadoop_test_cluster

# Project settings
project = 'hadoop-test-cluster'
copyright = '2018, Jim Crist-Harif'
author = 'Jim Crist-Harif'
release = version = hadoop_test_cluster.__version__

source_suffix = '.rst'
master_doc = 'index'
language = None
pygments_style = 'sphinx'
exclude_patterns = []

# Sphinx Extensions
extensions = ['sphinx.ext.extlinks', 'sphinxcontrib.autoprogram']

numpydoc_show_class_members = False

extlinks = {
    'issue': ('https://github.com/jcrist/hadoop-test-cluster/issues/%s', 'Issue #'),
    'pr': ('https://github.com/jcrist/hadoop-test-cluster/pull/%s', 'PR #')
}

# Sphinx Theme
html_theme = 'alabaster'
html_theme_path = [alabaster.get_path()]
templates_path = ['_templates']
html_static_path = ['_static']
html_theme_options = {
    'description': 'A docker setup for testing software on realistic Hadoop Clusters',
    'github_button': True,
    'github_count': False,
    'github_user': 'jcrist',
    'github_repo': 'hadoop-test-cluster',
    'travis_button': False,
    'show_powered_by': False,
    'page_width': '960px',
    'sidebar_width': '250px',
    'code_font_size': '0.8em'
}
html_sidebars = {
    '**': ['about.html',
           'navigation.html',
           'help.html',
           'searchbox.html']
}
