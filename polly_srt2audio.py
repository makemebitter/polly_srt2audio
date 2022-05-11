from boto3 import Session
from botocore.exceptions import BotoCoreError, ClientError
from contextlib import closing
from pydub import AudioSegment
import pysrt
from pysrt import SubRipTime
from pydub.utils import mediainfo
import os
import argparse


class PollySRT(object):

    def __init__(self, input_file, output_dir, output_file, voice_id):
        self.input_file = input_file
        self.output_dir = output_dir
        self.voice_id = voice_id
        self.psrt = pysrt.open(self.input_file)
        self.output_file = output_file

    def init_polly(self):
        self.session = Session()
        self.polly = self.session.client("polly")

    def request_and_download(self, text="Hello world!", output_name="speech"):
        try:
            # Request speech synthesis
            response = self.polly.synthesize_speech(Text=text,
                                                    OutputFormat="mp3",
                                                    Engine="neural",
                                                    VoiceId=self.voice_id)
        except (BotoCoreError, ClientError) as error:
            # The service returned an error, exit gracefully
            print(error)

        # Access the audio stream from the response
        if "AudioStream" in response:
            # Note: Closing the stream is important because the service throttles on the
            # number of parallel connections. Here we are using contextlib.closing to
            # ensure the close method of the stream object will be called automatically
            # at the end of the with statement's scope.
            with closing(response["AudioStream"]) as stream:
                outdir = self.output_dir
                #         outdir = gettempdir()
                output = os.path.join(outdir, "{}.mp3".format(output_name))
                try:
                    # Open a file for writing the output as a binary stream
                    with open(output, "wb") as file:
                        file.write(stream.read())
                except IOError as error:
                    # Could not write to file, exit gracefully
                    print(error)

    def request_and_download_all(self):
        for i, srt in enumerate(self.psrt):
            key = i + 1
            print("Requesting Polly for line: {}/{}".format(
                key, len(self.psrt)))
            self.request_and_download(text=srt.text, output_name=key)

    def run(self):
        self.init_polly()
        self.request_and_download_all()
        self.merge_and_save()

    def merge_and_save(self):
        last_mark = SubRipTime()

        agg = AudioSegment.empty()
        original_bitrate = mediainfo(os.path.join(self.output_dir,
                                                  "1.mp3"))['bit_rate']
        for i, srt in enumerate(self.psrt):
            key = i + 1
            start_mark = srt.start
            #             print(last_mark, start_mark)
            if last_mark > start_mark:
                #
                print(
                    "WARNING: Subtitle: {}, Text: {} wasn't able to fit, automatically inserting at {}. To prevent this from happening, consider editing srt."
                    .format(key, srt.text, last_mark))
                start_mark = last_mark
            else:
                comp = (start_mark - last_mark).ordinal
                comp_silent = AudioSegment.silent(comp, 24000)
                agg += comp_silent
            file_dir = os.path.join(self.output_dir, "{}.mp3".format(key))
            sound = AudioSegment.from_mp3(file_dir)
            agg += sound

            last_mark = start_mark + SubRipTime(
                milliseconds=sound.duration_seconds * 1000)

        agg.export(os.path.join(self.output_dir, self.output_file),
                   format="mp3",
                   bitrate=original_bitrate)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--input_file', type=str
    )
    parser.add_argument(
        '--output_dir', type=str, default='./'
    )
    parser.add_argument(
        '--output_file', type=str, default='output.mp3'
    )
    parser.add_argument(
        '--voice_id', type=str, default='Matthew'
    )
    args = parser.parse_args()

    pollysrt = PollySRT(
        args.input_file, args.output_dir, args.output_file, args.voice_id)
    pollysrt.run()
