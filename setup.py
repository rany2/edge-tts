import os
import shutil
import setuptools

# make edge-tts script
scripts=['build/edge-tts']
if not os.path.exists('build'):
    os.makedirs('build')
shutil.copyfile('src/edgeTTS/__init__.py', 'build/edge-tts')
if os.name == 'posix':
    shutil.copyfile('edge-playback.sh', 'build/edge-playback')
    scripts+=['build/edge-playback']

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="edge-tts",
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
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    scripts=scripts,
    python_requires=">=3.6",
)
