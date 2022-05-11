### About 
This is a script to convert a given `*.srt` subtitle file to a syncronized voiceover mp3 file. This is done by using [AWS Polly](https://aws.amazon.com/polly/) for speech generation and then syncronizing according to the subtitle file. 

### Prerequisite

- Python
- An AWS account, may incurr standard AWS Polly charges
- AWS command line credentials already configured. Easiest way is to install [AWS CLI](https://aws.amazon.com/cli/) and run `aws configure`

### Installation

```bash
pip install -r requirements.txt
```
### Usage
usage: polly_srt2audio.py [-h] [--input_file INPUT_FILE] [--output_dir OUTPUT_DIR]
                          [--output_file OUTPUT_FILE] [--voice_id VOICE_ID]

### Example
```bash
mkdir output
python polly_srt2audio.py --input_file /Users/XXX/Downloads/captions.srt --output_dir output
```
An example voiced-over video:
<iframe width="560" height="315" src="https://www.youtube.com/embed/qXMs32VSgPo" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>