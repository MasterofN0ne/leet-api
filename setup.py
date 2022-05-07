import dotenv
from importlib_metadata import entry_points
from setuptools import setup, find_packages

setup(
    name='leet',
    version='0.0.1',
    packages=find_packages(),
    py_modules=['leet_cli'],
    install_requires=[
        'click',
        'requests',
        'pymongo',
        'python-dotenv',
        'passlib',
        'flask'
    ],
    entry_points='''
    [console_scripts]
    leet=leet_cli:main
    '''
)