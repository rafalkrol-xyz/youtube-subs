from google.cloud import storage
from google.cloud import speech
import srt
import datetime


def list_buckets() -> list[str]:
    """
    Lists all buckets in your Google Cloud Platform (GCP) account
    and returns their names.

    :return: list[str]
    """

    storage_client = storage.Client()
    buckets = storage_client.list_buckets()

    bucket_names = set()

    for bucket in buckets:
        bucket_names.add(bucket.name)
    
    return bucket_names


def upload_blob(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to a given GCS bucket"""

    storage_client = storage.Client()

    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)

    print(
        "File {} uploaded to {}.".format(
            source_file_name, destination_blob_name
        )
    )

    return f'gs://{bucket_name}/{destination_blob_name}'


def transcribe_model_selection(gcs_uri: str, audio_channel_count: int, sample_rate_hertz: int):
    """Transcribe the given audio file synchronously with
    the selected model."""

    client = speech.SpeechClient()

    audio = speech.RecognitionAudio(uri=gcs_uri)

    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        audio_channel_count=audio_channel_count,
        sample_rate_hertz=sample_rate_hertz,
        language_code="pl-PL",
        model="latest_long",
        enable_word_time_offsets=True,
    )

    operation = client.long_running_recognize(config=config, audio=audio)

    print("Waiting for operation to complete...")
    response = operation.result(timeout=1800)  # 30 minutes

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
                start_microsec = (result.alternatives[0].words[0].start_time.nanos * 0.001
                                  if hasattr(result.alternatives[0].words[0].start_time, 'nanos')
                                  else result.alternatives[0].words[0].start_time.seconds / 1000000)
            else:
                # bin start -> For First word of response
                start_sec = 0
                start_microsec = 0
            end_sec = start_sec + bin_size  # bin end sec

            # for last word of result
            last_word_end_sec = result.alternatives[0].words[-1].end_time.seconds
            last_word_end_microsec = (result.alternatives[0].words[-1].end_time.nanos * 0.001
                                      if hasattr(result.alternatives[0].words[-1].end_time, 'nanos')
                                      else result.alternatives[0].words[-1].end_time.seconds / 1000000)

            # bin transcript
            transcript = result.alternatives[0].words[0].word

            index += 1  # subtitle index

            for i in range(len(result.alternatives[0].words) - 1):
                try:
                    word = result.alternatives[0].words[i + 1].word
                    word_start_sec = result.alternatives[0].words[i + 1].start_time.seconds
                    word_start_microsec = (result.alternatives[0].words[i + 1].start_time.nanos * 0.001
                                           if hasattr(result.alternatives[0].words[i + 1].start_time, 'nanos')
                                           else result.alternatives[0].words[i + 1].start_time.seconds / 1000000)
                    word_end_sec = result.alternatives[0].words[i + 1].end_time.seconds
                    word_end_microsec = (result.alternatives[0].words[i + 1].end_time.nanos * 0.001
                                         if hasattr(result.alternatives[0].words[i + 1].end_time, 'nanos')
                                         else result.alternatives[0].words[i + 1].end_time.seconds / 1000000)

                    if word_end_sec < end_sec:
                        transcript = transcript + " " + word
                    else:
                        previous_word_end_sec = result.alternatives[0].words[i].end_time.seconds
                        previous_word_end_microsec = (result.alternatives[0].words[i].end_time.nanos * 0.001
                                                      if hasattr(result.alternatives[0].words[i].end_time, 'nanos')
                                                      else result.alternatives[0].words[i].end_time.seconds / 1000000)

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
