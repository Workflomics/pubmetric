from setuptools import setup, find_packages

setup(
    name='wfqc',
    version='0.1.0',
    description='A description of your project',
    author='Your Name',
    author_email='your.email@example.com',
    license='Apache License 2.0',
    packages=find_packages(),
    install_requires=[
        'aiohttp==3.9.5',
        'asyncio==3.4.3',
        'igraph',
        'requests',
        'py4cytoscape==1.9.0',
        'pandas',
        'tqdm==4.66.2',
        'numpy',
        'matplotlib',
        'nest_asyncio',
        'jsonpath-ng',
        'ruamel.yaml',
        'cwl_utils'
    ],
    extras_require={
        'test': [
            'pytest',
            'pytest-datadir',
            'pytest-asyncio'
        ]
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
