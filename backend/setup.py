from setuptools import setup, find_packages

setup(
    name="backend",
    version="0.1.0",
    author="naps",
    # author_email="you@example.com",
    description="Backend package for NHentai archiver and web UI",
    packages=find_packages(),
    install_requires=[
        "Flask>=2.0",
        "flask-socketio>=5.0",
        "requests>=2.25",
        "beautifulsoup4>=4.9",
    ],
    python_requires='>=3.8',
    entry_points={
        'console_scripts': [
            'backend-archiver=backend.core.archiver:main',
            'backend-favorites=backend.core.favorites:main'
        ],
    },
)
