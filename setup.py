"""
See:
https://packaging.python.org/guides/distributing-packages-using-setuptools/
https://github.com/pypa/sampleproject
"""

from setuptools import find_packages, setup

setup(
    name="HR Smart Knowledge Manager",
    version="0.0.1",
    description="HR smart knowledge manager",
    packages=find_packages(),
    python_requires=">=3.9, <4",
    install_requires=[],
    extras_require={
        "dev": [
            "pip-tools",
            "ipykernel==6.29.5",
            "openpyxl==3.1.5",
            "pip-chill==1.0.3",
        ],
        "frontend": [
            "flask>=3.0.3, <4",
            "requests>=2.32.3, <3",
        ],
        "api": [
            "flask>=3.0.3, <4",
            "boto3",
            "opensearch-py",
            "opensearch-haystack",
            "haystack-ai",
            "fastembed-haystack",
            "amazon-bedrock-haystack",
            "accelerate"
        ],
        "datapipeline": [
           "accelerate==0.33.0",
           "amazon-bedrock-haystack==0.9.3",
           "config==0.5.1",
           "fastembed-haystack==1.2.0",
           "h2==4.1.0",
           "opensearch-haystack>=0.9.0, <1",
           "pdfminer.six==20240706",
           "python-docx==1.1.2",
           "python-pptx==0.6.23",
           "qdrant-haystack==4.1.2",
           "s3fs==2024.6.1",
           "sentence-transformers==3.0.1",
        ]
    },
)
