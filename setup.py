from setuptools import setup, find_packages

setup(
    name="viime-extract",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pypdf",
        "pdfplumber",
        "python-dotenv",
        "pydantic",
        "tiktoken",
        "langchain",
        "langchain-core",
        "langchain-community",
        "langchain-docling",
        "langchain-openai",
        "langchain-text-splitters",
    ],
    entry_points={
        "console_scripts": [
            # Add command line scripts here
        ],
    },
    author="Jeff Baumes",
    author_email="jeffbaumes@kitware.com",
    description="A description of your module",
    url="https://github.com/kitware/viime-extract",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
