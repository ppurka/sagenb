##########################################################
# The setup.py for the Sage Notebook
##########################################################

import os
from setuptools import setup
import distutils.log



def lremove(string, prefix):
    while string.startswith(prefix):
        string = string[len(prefix):]
    return string

def all_files(dir, prefix):
    """
    Return list of all filenames in the given directory, with prefix
    stripped from the left of the filenames.
    """

    X = []
    for F in os.listdir(dir):
        ab = dir+'/'+F
        if os.path.isfile(ab):
            X.append(lremove(ab, prefix))
        elif os.path.isdir(ab):
            X.extend(all_files(ab, prefix))
    return X


install_requires = [ 'twisted>=11.0.0'
                   , 'flask>=0.10.1'
                   , 'flask-oldsessions>=0.10'
                   , 'flask-openid'
                   , 'flask-autoindex'
                   , 'babel'
                   , 'flask-babel'
                   , 'webassets'
                   ]

if __name__ == '__main__':
    if os.environ.get("SAGE_SETUPTOOLS_DEBUG","no")=="yes":
        distutils.log.set_threshold(distutils.log.DEBUG)

    code = setup(name = 'sagenb',
          version     = '0.10.8.3',
          description = 'The Sage Notebook',
          license     = 'GNU General Public License (GPL) v3+',
          author      = 'William Stein et al.',
          author_email= 'sage-notebook@googlegroups.com',
          url         = 'http://github.com/sagemath/sagenb',
          install_requires = install_requires,
          dependency_links =    [
                                  'http://github.com/mitsuhiko/flask-oldsessions/tarball/master#egg=flask-oldsessions-0.10'
                                ],
          test_suite = 'sagenb.testing.run_tests.all_tests',
          packages    = [ 'sagenb'
                        , 'sagenb.flask_version'
                        , 'sagenb.interfaces'
                        , 'sagenb.misc'
                        , 'sagenb.notebook'
                        , 'sagenb.notebook.compress'
                        , 'sagenb.simple'
                        , 'sagenb.storage'
                        , 'sagenb.testing'
                        , 'sagenb.testing.tests'
                        , 'sagenb.testing.selenium'
                        ],
          scripts      = [ 'sagenb/data/sage3d/sage3d',
                         ],
          package_data = {'sagenb':
                              all_files('sagenb/data', 'sagenb/') +
                              all_files('sagenb/translations', 'sagenb/')
                         },
          zip_safe     = False,
          )
