from setuptools import setup
import textwrap

setup(
    name='python-controlshift',
    version='0.1',
    author='MoveOn',
    packages=['controlshift',],
    url='https://github.com/MoveOnOrg/python-controlshift',
    license='MIT',
    description="python-controlshift is a python interface to the ControlShift ECRM. The goal is to provide simple access to ControlShift via the the REST public and Oauth APIs",
    long_description=textwrap.dedent(open('README.md', 'r').read()),
    install_requires=[
        'requests',
        'requests_oauthlib'
    ],
    keywords = "python controlshift",
    classifiers=['Development Status :: 4 - Beta', 'Environment :: Console', 'Intended Audience :: Developers', 'Natural Language :: English', 'Operating System :: OS Independent', 'Topic :: Internet :: WWW/HTTP'],
)
