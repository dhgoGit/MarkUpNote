from setuptools import setup, find_packages

setup(
    name="markupnote",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "PyQt5>=5.15.10",
        "numpy>=1.26.4",
        "Pillow>=10.2.0",
        "easyocr>=1.7.1",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-qt>=4.2.0",
            "pytest-cov>=4.1.0",
            "black>=23.12.1",
            "isort>=5.13.2",
        ],
    },
    python_requires=">=3.8",
    author="MarkUpNote Team",
    description="A note application that converts images into markup language",
    keywords="note, markup, image processing",
) 