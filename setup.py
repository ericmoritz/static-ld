from setuptools import setup

setup(
    name="staticld",
    packages=["staticld"],
    zip_safe=False,
    install_requires=[
        "click==0.6",
        "rdflib==4.1.2",
        "jinja2==2.7.2",
    ],
    scripts=["bin/staticld"],
)
