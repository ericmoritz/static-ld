from setuptools import setup

setup(
    name="static-ld",
    packages=["staticld"],
    install_requires=[
        "click==0.6",
    ],
    scripts=["bin/static-ld"],
)
