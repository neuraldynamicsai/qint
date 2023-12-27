from setuptools import find_packages, setup

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="qint",
    version="0.2.0",
    description="Quantized Integer type in Python!",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Neural Dynamics",
    author_email="support@neuraldynamicsai.com",
    packages=find_packages(),
    install_requires=[],
    license="MIT",
    project_urls={"GitHub": "https://github.com/neuraldynamicsai/qint"},
)
