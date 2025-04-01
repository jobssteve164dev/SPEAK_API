from setuptools import setup, find_packages

with open("README_SDK.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="tts-edge-sdk",
    version="0.1.0",
    author="TTS Team",
    author_email="your.email@example.com",
    description="Edge TTS SDK for easy text-to-speech conversion",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/tts-edge-sdk",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        "edge-tts>=6.1.9",
        "pydub>=0.25.1",
    ],
) 