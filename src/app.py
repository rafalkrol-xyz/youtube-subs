# import local libraries
from src.video import download, info, video_to_audio
from src.gcp import list_buckets, upload_blob, transcribe_model_selection, subtitle_generation


def main(youtube_link: str, bucket_for_audio_files: str = None):
    video_path = download(youtube_link)

    if bucket_for_audio_files is None:
        bucket_names = list_buckets()

        for bucket_name in bucket_names:
            if 'temporary_bucket_for_audio_files' in bucket_name:
                bucket_for_audio_files = bucket_name

    channels, bit_rate, sample_rate = info('video.mp4')

    audio_filename = 'audio.wav'
    video_to_audio(video_path, audio_filename, channels, bit_rate, sample_rate)

    gcs_uri = upload_blob(bucket_for_audio_files, audio_filename, f'audios/{audio_filename}')

    response = transcribe_model_selection(gcs_uri, channels, sample_rate)

    subtitles = subtitle_generation(response)
    print(subtitles)

    with open("subtitles.srt", "w") as f:
        f.write(subtitles)
