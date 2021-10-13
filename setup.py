from setuptools import setup, find_packages

setup(
    name='Monitor',
    version='0.1.0',
    description='Setting up a python package',
    author='Philip Slisenko',
    author_email='slisenko.philip@gmail.com',
    url='https://blog.godatadriven.com/setup-py',
    packages=find_packages(include=['src']),
    install_requires=['loguru', 'psycopg2', 'torch', 'torchvision'],
    extras_require={'dev': ['flake8', 'pytest']},
    entry_points={
        'console_scripts': [
            'run-operator=src.main:main',
            'start-recording=src.scripts.record_and_save:main'
        ]
    }
)