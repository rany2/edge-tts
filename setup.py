from setuptools import setup

# Metadata goes in setup.cfg. These are here for GitHub's dependency graph.
setup(
    name="edge-tts",
    install_requires=[
        "aiohttp>=3.8.0",
        "certifi>=2023.11.17",
    ],
)
