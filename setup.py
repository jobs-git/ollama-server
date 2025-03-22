from setuptools import setup, find_packages

setup(
    name='ollama-server',
    version='0.1.0',
    description='Server management for Ollama',
    author='James Guana',
    author_email='',
    packages=find_packages(),
    install_requires=[
        'requests',
    ],
    python_requires='>=3.8',
)
