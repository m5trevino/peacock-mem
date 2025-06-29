from setuptools import setup, find_packages

setup(
    name="peacock-memory",
    version="1.0.0",
    py_modules=["peacock_launcher"],
    entry_points={
        "console_scripts": [
            "pea-mem=peacock_launcher:main",
        ],
    },
    install_requires=[
        "chromadb>=0.4.0",
        "rich>=13.0.0", 
        "questionary>=2.0.0",
        "typer>=0.9.0"
    ],
)

def main():
    from main import main as app_main
    app_main()
