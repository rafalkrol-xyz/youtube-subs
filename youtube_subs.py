import click
from src import app


@click.group()
def cli():
    """
    YouTube Subs (invoked as `youtube-subs` or `ys`)
    is a very simple CLI tool, still in early stages of development,
    that can generate an SRT (SubRip format) file with subtitles for a given
    YouTube video using Google Cloud Platform (GCP) services,
    that you pay for, under the hood.
    """
    pass


@cli.command()
@click.option('-b', '--bucket',
              type=str,
              help="""
              Name of the Google Cloud Storage (GCS) bucket to place the audio files in.
              By default the CLI will usea bucket containing `temporary_bucket_for_audio_files` in its name.
              """,
              default=None)
@click.argument('youtube_link')
def generate(youtube_link, bucket):
    """
    Generate subtitles for a YouTube video passed via the YOUTUBE_LINK argument.
    E.g. ys generate https://www.youtube.com/watch?v=EgLCtVshp8E
    """
    app.main(youtube_link, bucket)
