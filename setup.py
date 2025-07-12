from setuptools import setup, find_packages

setup(
    name="presentation-toolkit",
    version="1.0.0",
    description="Comprehensive presentation generation and evaluation toolkit",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "anthropic>=0.18.0",
        "requests>=2.31.0",
        "beautifulsoup4>=4.12.0",
        "selenium>=4.15.0",
        "playwright>=1.40.0",
        "reportlab>=4.0.0",
        "pillow>=10.0.0",
        "opencv-python>=4.8.0",
        "python-dotenv>=1.0.0",
        "openai==1.88.0",
        # Image validation dependencies
        "duckdb>=0.8.0",
        "aiohttp>=3.8.0",
        "numpy>=1.24.0",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "presentation-toolkit=main:main",
            "opencanvas=opencanvas.main:main",
        ],
    },
)