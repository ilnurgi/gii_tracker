from setuptools import setup, find_packages

setup(
    name='gii_torrents',
    version='0.3',
    author='ilnurgi',
    author_email='ilnurgi@mail.ru',
    url='http://ilnurgi.ru',
    packages=find_packages(),
    install_requires=[
        'selenium',
        'pyyaml',
    ],
    entry_points={
        'console_scripts': [
            'gii_torrents = gii_torrents.app:main'
        ]
    }
)
