import setuptools

setuptools.setup(
    name="mfcauto",
    version="0.1.0",
    url="https://github.com/ZombieAlex/mfcauto.py",
    license="MIT",

    author="ZombieAlex",
    author_email="zombiealex69@gmail.com",

    description="Communicates with MFC chat servers",
    long_description=open('README.rst').read(),

    packages=setuptools.find_packages(),

    install_requires=[],

    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
    ],
)
