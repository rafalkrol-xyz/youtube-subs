import os
import pytube
from pydub.utils import mediainfo
import subprocess


def download(url: str) -> str:
    """
    Download a YouTube video in an mp4 format using the provided URL.

    :param str url:
        The URL to a YouTube video, e.g.: 'https://www.youtube.com/watch?v=K2tA-R3v1GI'
    
    :return: str
        The default name of the downloaded video file ('video.mp4').
    """
    yt = pytube.YouTube(url=url)
    video_path = (yt.streams.filter(progressive=True, file_extension='mp4')
                  .order_by('resolution')
                  .desc()
                  .first()
                  .download())
    default_name = 'video.mp4'

    os.replace(video_path, default_name)

    return default_name


def info(video_filepath: str) -> tuple[int, int, int]:
    """
    Returns the number of channels, bit rate, and sample rate of the provided video.

    :param video_filepath: str
        The filepath to the video file.

    :return: tuple[int, int, int]
        A tuple containing the number of channels, bit rate, and sample rate of the video.
    """

    video_data = mediainfo(video_filepath)

    return int(video_data["channels"]), int(video_data["bit_rate"]), int(video_data["sample_rate"])


def video_to_audio(video_filepath: str,
                   audio_filename: str,
                   video_channels: int,
                   video_bit_rate: int,
                   video_sample_rate: int) -> None:
    """
    Convert a video file to an audio file using ffmpeg.

    :param video_filepath: str
        The filepath to the video file.
    :param audio_filename: str
        The name of the output audio file.
    :param video_channels: int
        The number of channels in the video file.
    :param video_bit_rate: int
        The bit rate of the video file.
    :param video_sample_rate: int
        The sample rate of the video file.
    """

    command = (
        f"ffmpeg -i {video_filepath} "
        f"-b:a {video_bit_rate} "
        f"-ac {video_channels} "
        f"-ar {video_sample_rate} "
        f"-vn {audio_filename} -y"
    )
    subprocess.call(command, shell=True)
