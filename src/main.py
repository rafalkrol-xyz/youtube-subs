# import local libraries
import video
import gcp

BUCKET_NAME = 'temporary_bucket_for_audio_files-0828716'  # TODO: name contains this static value: temporary_bucket_for_audio_files


def main():
    video_path = video.download('https://www.youtube.com/watch?v=SXXrBsBCJME')

    channels, bit_rate, sample_rate = video.info('video.mp4')

    audio_filename = 'audio.wav'
    video.video_to_audio(video_path, audio_filename, channels, bit_rate, sample_rate)

    gcs_uri = gcp.upload_blob(BUCKET_NAME, audio_filename, f'audios/{audio_filename}')

    response = gcp.transcribe_model_selection(gcs_uri, channels, sample_rate)

    subtitles = gcp.subtitle_generation(response)
    print(subtitles)

    with open("subtitles.srt", "w") as f:
        f.write(subtitles)


if __name__ == '__main__':
    main()
