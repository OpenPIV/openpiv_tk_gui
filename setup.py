import setuptools
from glob import glob

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="openpivgui",
    version="0.3.11",
    install_requires=['OpenPiv', 'pandas'],
    author="P. Vennemann and contributors.",
    author_email="vennemann@fh-muenster.de",
    description="A simple GUI for Open PIV.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/OpenPIV/openpiv_tk_gui",
    include_package_data = True,
    package_data={'': ['./res/*.png']},
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.0',
)
