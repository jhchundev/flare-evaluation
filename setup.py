"""Setup configuration for the Flare Evaluation package."""

from setuptools import setup, find_packages
import os

# Read README for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="flare-evaluation",
    version="1.0.0",
    author="Flare Evaluation Team",
    author_email="",
    description="A comprehensive toolkit for optical flare analysis in sensor data",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/flare-evaluation",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Image Processing",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=3.0",
            "black>=22.0",
            "flake8>=4.0",
            "mypy>=0.950",
            "sphinx>=4.0",
        ],
        "visualization": [
            "matplotlib>=3.5",
            "plotly>=5.0",
            "pillow>=9.0",
        ],
        "advanced": [
            "scipy>=1.7",
            "scikit-image>=0.19",
            "opencv-python>=4.5",
        ],
    },
    entry_points={
        "console_scripts": [
            "flare-evaluate=flare_evaluation.cli.evaluate:main",
            "flare-generate=flare_evaluation.cli.generate:main",
            "flare-batch=flare_evaluation.cli.batch:main",
        ],
    },
    include_package_data=True,
    package_data={
        "flare_evaluation": [
            "config/*.json",
            "data/*.csv",
        ],
    },
    zip_safe=False,
)