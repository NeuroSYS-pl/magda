import setuptools

with open('README.md', 'r') as f:
    long_description = f.read()

dependencies = [
    'colorama>=0.4,<1',
    'pyyaml>=5.3.1,<6',
    'ray[default]>=1.5.2,<2',
]

test_dependencies = [
    'pytest==6.1.*',
    'pytest-cov==2.10.*',
    'pytest-asyncio==0.14.*',
]

setuptools.setup(
    name='magda',
    version='0.2.0.rc2',
    author='NeuroSYS Research',
    description=(
        'Library for building Modular and Asynchronous Graphs '
        'with Directed and Acyclic edges (MAGDA)'
    ),
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/NeuroSYS-pl/magda',
    keywords=(
        'magda modular asynchronous parallelization'
        'directed-graphs acyclic-graphs pipeline python'
    ),
    packages=setuptools.find_packages(),
    license="Apache 2.0",
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
