from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='pyroxide',
    version='0.2',
    description='HTTP(s)/SOCKS Proxy Sanitizer & Validator',
    py_modules=["pyroxide"],
    package_dir={'': 'src'},
    long_description=long_description,
    long_description_content_type="text/markdown",
    license='MIT',
    author = 'Steven Reagan',
    author_email = 'slreagan90@gmail.com',
    url = 'https://github.com/tinkerfish/pyroxide',
    download_url = 'https://github.com/tinkerfish/pyroxide/archive/v_0.2.tar.gz',
    keywords = ['PROXY', 'SOCKS', 'SANITIZE', 'VERIFY'],
    install_requires=[
        'requests'
    ],
    extras_require = {
        "dev": [
            "pytest>=3.6"
        ]
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
)
