from setuptools import setup, find_packages
import os

ROOT = os.path.dirname(os.path.realpath(__file__))

setup(
    name = 'prox',
    version = '0.0.8',
    description = 'The tool to check the health of proxy list',
    long_description = open(os.path.join(ROOT, 'README.rst')).read(),
    url = 'http://github.com/lorien/prox',
    author = 'Gregory Petukhov',
    author_email = 'lorien@lorien.name',

    packages = find_packages(),
    include_package_data = True,
    scripts = ('bin/prox_check', 'bin/prox_task'),
    install_requires = [
        'urllib3',
        'pysocks',
        'peewee',
        'bottle',
        'pyyaml',
    ],
    license = "MIT",
    keywords = "proxy proxylist",
    classifiers = [
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.4',
        'License :: OSI Approved :: MIT License',
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
    ],
)
