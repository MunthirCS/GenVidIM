import os
from setuptools import setup, find_packages

# Function to read the requirements file
def read_requirements(file_path):
    with open(file_path, 'r') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]

# Get the absolute path to the directory containing setup.py
base_dir = os.path.abspath(os.path.dirname(__file__))

# Read the main requirements file
requirements = read_requirements(os.path.join(base_dir, 'GenVidIM', 'requirements.txt'))

# Read additional requirements files
requirements_animate = read_requirements(os.path.join(base_dir, 'GenVidIM', 'requirements_animate.txt'))
requirements_s2v = read_requirements(os.path.join(base_dir, 'GenVidIM', 'requirements_s2v.txt'))
requirements_serverless = read_requirements(os.path.join(base_dir, 'GenVidIM', 'requirements_serverless.txt'))

setup(
    name='GenVidIM',
    version='2.2.0',
    description='An open and advanced large-scale video generative model',
    long_description=open('GenVidIM/README.md').read(),
    long_description_content_type='text/markdown',
    author='Team Wan',
    author_email='',  # Add author email if available
    url='https://github.com/Wan-Video/Wan2.2',
    packages=find_packages(where='GenVidIM'),
    package_dir={'': 'GenVidIM'},
    install_requires=requirements,
    extras_require={
        'animate': requirements_animate,
        's2v': requirements_s2v,
        'serverless': requirements_serverless,
        'all': requirements_animate + requirements_s2v + requirements_serverless,
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Multimedia :: Video',
    ],
    python_requires='>=3.8',
    include_package_data=True,
    zip_safe=False,
)
