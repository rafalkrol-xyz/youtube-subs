import subprocess
import pytube
import os
from pydub.utils import mediainfo
from google.cloud import storage
from google.cloud import speech_v1
from google.cloud.speech_v1 import enums
from requests import delete
import srt
import datetime

BUCKET_NAME = 'youtube-subs-audio'  # TODO: grab this value from Pulumi stack outputs
storage_client = storage.Client()


def download_video(link, new_filename):
    try:
        yt = pytube.YouTube(link)
    except:
        print('Something went wrong when downloading the video from YouTube')

    video_path = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first().download()

    new_path = video_path.split('/')
    new_path[-1] = new_filename
    new_path = '/'.join(new_path)
    os.rename(video_path, new_path)

    return new_path


def video_info(video_filepath):
    """Returns the number of channels, bit rate, and sample rate of the provided video"""

    video_data = mediainfo(video_filepath)
    channels = video_data["channels"]
    bit_rate = video_data["bit_rate"]
    sample_rate = video_data["sample_rate"]

    return channels, bit_rate, sample_rate


def video_to_audio(video_filepath, audio_filename, video_channels, video_bit_rate, video_sample_rate):
    command = f"ffmpeg -i {video_filepath} -b:a {video_bit_rate} -ac {video_channels} -ar {video_sample_rate} -vn {audio_filename}"
    subprocess.call(command, shell=True)

    # FIXME: add error handling!!!


def upload_blob(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to a given GCS bucket"""
    # bucket_name = "your-bucket-name"
    # source_file_name = "local/path/to/file"
    # destination_blob_name = "storage-object-name"

    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    
    blob.upload_from_filename(source_file_name)

    print(
        "File {} uploaded to {}.".format(
            source_file_name, destination_blob_name
        )
    )


def long_running_recognize(storage_uri, channels, sample_rate):

    client = speech_v1.SpeechClient()

    config = {
        "language_code": "pl-PL",
        "sample_rate_hertz": int(sample_rate),
        # "encoding": speech_v1.RecognitionConfig.AudioEncoding.LINEAR16,
        "encoding": enums.RecognitionConfig.AudioEncoding.LINEAR16,
        "audio_channel_count": int(channels),
        "enable_word_time_offsets": True,
        "model": "latest_long",
        "enable_automatic_punctuation": True
    }
    audio = {"uri": storage_uri}

    operation = client.long_running_recognize(audio=audio, config=config)

    print(u"Waiting for operation to complete...")
    response = operation.result()
    return response


def subtitle_generation(speech_to_text_response, bin_size=3):
    """We define a bin of time period to display the words in sync with audio. 
    Here, bin_size = 3 means each bin is of 3 secs. 
    All the words in the interval of 3 secs in result will be grouped together."""
    transcriptions = []
    index = 0

    for result in speech_to_text_response.results:
        try:
            if result.alternatives[0].words[0].start_time.seconds:
                # bin start -> for first word of result
                start_sec = result.alternatives[0].words[0].start_time.seconds
                start_microsec = result.alternatives[0].words[0].start_time.nanos * 0.001
            else:
                # bin start -> For First word of response
                start_sec = 0
                start_microsec = 0
            end_sec = start_sec + bin_size  # bin end sec

            # for last word of result
            last_word_end_sec = result.alternatives[0].words[-1].end_time.seconds
            last_word_end_microsec = result.alternatives[0].words[-1].end_time.nanos * 0.001

            # bin transcript
            transcript = result.alternatives[0].words[0].word

            index += 1  # subtitle index

            for i in range(len(result.alternatives[0].words) - 1):
                try:
                    word = result.alternatives[0].words[i + 1].word
                    word_start_sec = result.alternatives[0].words[i + 1].start_time.seconds
                    word_start_microsec = result.alternatives[0].words[i + 1].start_time.nanos * 0.001  # 0.001 to convert nana -> micro
                    word_end_sec = result.alternatives[0].words[i + 1].end_time.seconds
                    word_end_microsec = result.alternatives[0].words[i + 1].end_time.nanos * 0.001

                    if word_end_sec < end_sec:
                        transcript = transcript + " " + word
                    else:
                        previous_word_end_sec = result.alternatives[0].words[i].end_time.seconds
                        previous_word_end_microsec = result.alternatives[0].words[i].end_time.nanos * 0.001

                        # append bin transcript
                        transcriptions.append(srt.Subtitle(index, datetime.timedelta(0, start_sec, start_microsec),
                                              datetime.timedelta(0, previous_word_end_sec, previous_word_end_microsec), transcript))

                        # reset bin parameters
                        start_sec = word_start_sec
                        start_microsec = word_start_microsec
                        end_sec = start_sec + bin_size
                        transcript = result.alternatives[0].words[i + 1].word

                        index += 1
                except IndexError:
                    pass
            # append transcript of last transcript in bin
            transcriptions.append(srt.Subtitle(index, datetime.timedelta(0, start_sec, start_microsec),
                                  datetime.timedelta(0, last_word_end_sec, last_word_end_microsec), transcript))
            index += 1
        except IndexError:
            pass

    # turn transcription list into subtitles
    subtitles = srt.compose(transcriptions)
    return subtitles


def main():
    new_filename = 'video.mp4'

    # if os.path.exists(new_filename) is False:
    download_video('https://www.youtube.com/watch?v=NTfygb7k8Ok', new_filename)

    channels, bit_rate, sample_rate = video_info(new_filename)
    audio_filename = 'audio.wav'

    # if os.path.exists(audio_filename) is False:
    video_to_audio(new_filename, audio_filename, channels, bit_rate, sample_rate)

    blob_name = f"audios/{audio_filename}"

    # FIXME: figure out how to only upload the file conditionally
    upload_blob(BUCKET_NAME, audio_filename, blob_name)

    gcs_uri = f"gs://{BUCKET_NAME}/{blob_name}"
    response = long_running_recognize(gcs_uri, channels, sample_rate)

    subtitles = subtitle_generation(response)
    print(subtitles)

    with open("subtitles.srt", "w") as f:
        f.write(subtitles)


if __name__ == '__main__':
    main()
