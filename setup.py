from setuptools import setup

setup(
    name="edge-tts",
    version="1.0.0",  # You can specify your version here
    install_requires=[
        "aiohttp>=3.8.0,<4.0.0",
        "certifi>=2023.11.17",
        "srt>=3.4.1,<4.0.0",
        "tabulate>=0.4.4,<1.0.0",
        "typing-extensions>=4.1.0,<5.0.0",
        "fastapi>=0.95.0",  # FastAPI version (you can specify the version you need)
        "uvicorn>=0.18.0",  # Uvicorn version (for running FastAPI)
    ],
    packages=find_packages(where="src"),  # Automatically find packages in the src folder
    package_dir={"": "src"},  # Tells setuptools that the package is in the 'src' directory
    include_package_data=True,  # To include non-Python files, such as SSL certs, config, etc.
)
