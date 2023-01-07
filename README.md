# YouTube Subs

## Overview

This is a simple CLI tool for generating subtitles
([in SRT format](https://mailchimp.com/resources/what-is-an-srt-file))
from YouTube videos.

### Business logic

1. You provide the CLI tool with a hyperlink for a YouTube video.
2. The tool downloads the video to your machine as `video.mp4`.
3. Then, from `video.mp4` it extracts audio using [FFmpeg](https://ffmpeg.org/)
and saves that audio locally as `audio.wav`.
4. In the next step, it uploads the `audio.wav` file
to your [GCS bucket](https://cloud.google.com/storage/docs/buckets).
5. [GCP's Speech-to-Text service](https://cloud.google.com/speech-to-text/)
picks up the the `audio.wav` file from the GCS bucket and transcribes it.
6. Finally, the transcription (**not 100% accurate,
but with timestamps!**) is saved as the `subtitles.srt` file on your computer.

### Folder structure

This project consists of a smaller, but still vital, infrastructure part,
and a bigger, in terms of lines of code (LOC), application part.

The infrastructure lives in the `./infra` directory
(with [its own `REAMDE.md` file](https://github.com/rafalkrol-xyz/youtube-subs/tree/main/infra#readme)),
the app's business logic lives in the `./src` directory,
while the `setup.py` and other files necessary to package this CLI tool, live here, at the project's root.

## Prerequisites

### Infrastructure

Before using the CLI or commencing with local development, you must **a) meet the infrastructure prerequisites**,
and **b) stand up the infra using the `pulumi up` command**.

_Refer to [the infra README](https://github.com/rafalkrol-xyz/youtube-subs/tree/main/infra#readme) for more details._

### Application

* [Python v3.10 or higher](https://www.python.org/)
* (OPTIONAL)[wheel](https://pypi.org/project/wheel/), [setuptools](https://pypi.org/project/setuptools/),
  and [twine](https://pypi.org/project/twine/):

  ```bash
  pip3 install wheel setuptools twine
  ```

* (OPTIONAL) user account at [Test PyPi](https://test.pypi.org/)

## Usage

**a)** download

```bash
pip install -i https://test.pypi.org/simple/ youtube-subs
```

**b)** run

```bash
ys generate https://www.youtube.com/watch?v=EgLCtVshp8E
```

## Local development

**a)** set up and activate Virtual Environment

```bash
pip3 -m venv venv
source venv/bin/activate
```

**b)** install dependencies

```bash
pip3 install -r requirements
```

**c)** build the tool for development

```bash
python3 setup.py develop
```

**d)** run the tool

```bash
ys
```

## Packaging & publishing

**a)** create a package

```bash
python setup.py sdist bdist_wheel
```

**b)** publish to [Test PyPi](https://test.pypi.org/)

```bash
twine upload --repository testpypi --skip-existing dist/*
```

## Acknowledgements

* the main business logic relies heavily on [this blog post](https://medium.com/searce/generate-srt-file-subtitles-using-google-clouds-speech-to-text-api-402b2f1da3bd)
* [this article](https://medium.com/nerd-for-tech/how-to-build-and-distribute-a-cli-tool-with-python-537ae41d9d78)
served me as a guidance for building and distributing a CLI tool in Python
