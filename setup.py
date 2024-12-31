from setuptools import setup, find_packages

setup(
    name="gitloom",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "anthropic",
        "gitpython",
    ],
    entry_points={
        'console_scripts': [
            'gitloom=gitloom.gitloom:main',  # format is command=package.module:function
        ],
    },
    python_requires='>=3.6'
)