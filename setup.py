from setuptools import setup, find_packages
from os import path
here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='coinblockpro',
    version='0.0.1',

    description="A toy server written in Sanic to mimic an online currency"
                " exchange, with a REST and websocket API.",

    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/hypernormalisation/coinblockpro',

    author='Stephen Ogilvy',
    author_email='sogilvy@tuta.io',

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],

    keywords='logging',
    packages=find_packages(exclude=['bin', 'notebooks']),
    python_requires='>=3.6',
    install_requires=['sanic', 'dataset', 'websockets'],
    scripts=[
        'bin/run_cbp_server',
        'bin/ws_server.py',
        'bin/rest_server.py',
    ],
    project_urls={
        'Source': 'https://github.com/hypernormalisation/coinblockpro',
    },
)
