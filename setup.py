from setuptools import setup, find_packages

setup(
    name="flutterswarm",
    version="0.2.0",
    packages=find_packages(),
    install_requires=[
        "asyncio",
        "pytest",
        "pytest-asyncio",
    ],
    python_requires=">=3.8",
)
