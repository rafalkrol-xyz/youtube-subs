from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read()


setup(
    name='youtube-subs',
    version='0.0.1',
    author='Rafal Krol',
    author_email='ameotoko1+github@gmail.com',
    license='MIT',
    description='A simple tool to generate subtitles from a YouTube video',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/rafalkrol-xyz/youtube-subs',
    py_modules=['youtube_subs'],
    packages=find_packages(),
    install_requires=[requirements],
    python_requires='>=3.10',
    classifiers=[
            "Programming Language :: Python :: 3.10",
            "Operating System :: OS Independent",
    ],
    entry_points='''
        [console_scripts]
        ys=youtube_subs:cli
        youtube-subs=youtube_subs:cli
    '''
)
