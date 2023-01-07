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

