import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="edgeTTS-rany",
    version="0.0.1",
    author="rany",
    author_email="ranygh@riseup.net",
    description="Microsoft Edge's TTS",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/rany2/edge-tts",
    project_urls={
        "Bug Tracker": "https://github.com/rany2/edge-tts/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GPLv3 License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)
