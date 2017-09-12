#from distutils.core import setup
from setuptools import setup

setup(
    name='AbPyTools',
    classifiers=['Development Status :: 2 - Pre-Alpha',
                 'Intended Audience :: Science/Research',
                 'License :: OSI Approved :: MIT License',
                 'Natural Language :: English',
                 'Programming Language :: Python :: 3 :: Only',
                 'Topic :: Scientific/Engineering :: Bio-Informatics'],
    keywords='antibody-analysis bioinformatics data-processing',
    version='0.1.1',
    package_dir={'abpytools': 'abpytools'},
    packages=['abpytools',
              'abpytools.utils',
              'abpytools.core',
              'abpytools.analysis',
              'abpytools.features'],
    package_data={'abpytools': ['data/*.json']},
    url='https://github.com/gf712/AbPyTools',
    license='MIT',
    author='Gil Ferreira Hoben',
    author_email='gil.hoben.16@ucl.ac.uk',
    description='Python package for antibody analysis',
    install_requires=['numpy',
                      'joblib',
                      'pandas',
                      'tqdm>=4.15',
                      'seaborn',
                      'matplotlib',
                      'beautifulsoup4'],
    test_suite="tests"
)
