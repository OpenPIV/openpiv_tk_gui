import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="openpivgui",
    version="0.2.4",
    install_requires='OpenPiv',
    author="Peter Vennemann",
    author_email="vennemann@fh-muenster.de",
    description="A simple GUI for Open PIV.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/OpenPIV/openpiv_tk_gui",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.0',
)
