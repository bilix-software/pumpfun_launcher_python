from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="pump-fun-token-launcher",
    version="1.0.0",
    author="Bilix Software",
    author_email="info@bilix.io",
    description="Programmatically launch pump.fun tokens with Python support",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bilix-software/pump-fun-token-launcher-python",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Office/Business :: Financial",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "mypy>=1.0.0",
        ],
    },
    keywords="pump.fun solana token crypto blockchain defi",
    project_urls={
        "Bug Reports": "https://github.com/bilix-software/pump-fun-token-launcher-python/issues",
        "Source": "https://github.com/bilix-software/pump-fun-token-launcher-python",
        "Documentation": "https://github.com/bilix-software/pump-fun-token-launcher-python#readme",
    },
)