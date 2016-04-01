from setuptools import setup, find_packages

import sys
from libkohlrabi import VERSION_S

install_requires = ['aioredis', 'msgpack-python']

PY_VER = sys.version_info

if PY_VER >= (3, 4):
    pass
elif PY_VER >= (3, 3):
    install_requires.append('asyncio')
else:
    raise RuntimeError("Kohlrabi requires Python > 3.3.")

classifiers = [
    'License :: OSI Approved :: MIT License',
    'Development Status :: 5 - Production/Stable',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Operating System :: POSIX',
    'Intended Audience :: Developers',
    'Topic :: Software Development',
    'Topic :: Software Development :: Libraries',
]


setup(
    name='Kohlrabi',
    version=VERSION_S,
    packages=find_packages(),
    url='https://github.com/SunDwarf/Kohlrabi',
    classifiers=classifiers,
    install_requires=install_requires,
    license='MIT',
    author='Isaac Dickinson',
    author_email='sun@veriny.tf',
    description='An asyncio-based task queue.',
    scripts=['kohlrabi-server.py', 'kohlrabi']
)
