import setuptools

with open('README.md', 'r') as f:
    long_description = f.read()

dependencies = [
    'pyyaml>=5.3.1,<6',
    'ray>=1.2.0,<2',
]

test_dependencies = [
    'pytest==6.1.*',
    'pytest-cov==2.10.*',
    'pytest-asyncio==0.14.*',
]

setuptools.setup(
    name='magda',
    version='0.1.0',
    author='NeuroSYS',
    description='Library for building Modular and Asynchronous Graphs with Directed and Acyclic edges (MAGDA)',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/NeuroSYS-pl/magda',
    packages=setuptools.find_packages(),
    license="Apache 2",
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    entry_points={},
    python_requires='>=3.7',
    install_requires=dependencies,
    extras_require={
        'test': test_dependencies,
    },
    setup_requires=[
        'pytest-runner',
    ],
    tests_require=test_dependencies,
)
