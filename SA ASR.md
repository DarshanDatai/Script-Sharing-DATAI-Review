---
language:
- en
tags:
- speech
- audio
- voice
- accent
size_categories:
- 10K<n<100K
pretty_name: English Casual Speech Sample South African Accent
license: cc-by-4.0
---

# English Casual Speech Sample (South African Accent)

South African crowd-sourced participants respond to questions about their daily lives and activities.

This dataset is a sample of a larger collection from the same data collection campaign.

## Changelog

**FEB 2026:** initial share. ASR (Chirp3) transcripts. WER: 12%

## Specs
- Speakers: ~550 unique South African speakers
- Total duration: ~60 hours
- Files sample rate: 48kHz
- Actual sample rate: TBD
- Language: English (SA accent)
- Transcript: ASR (Chirp3)
- Topics: day-to-day conversation

## Collection Method

The dataset is collected to capture English as spoken with South African accents.

Speakers come from urban settings and participate in interviews where they speak freely about their interests, activities, and related topics.

The conversation happens via Google Meet, and participants are recorded via multimedia capture software (e.g., OBS) from the interviewer’s machine.

## Processing

### Audio Segmentation

Speech segments were extracted and standardized from one-hour recordings of natural conversations.

All files are processed as follows:

- If present, videos are discarded
- Both AAC and WAV files are transcoded to pcm_s16le
- The resulting normalized WAVs are passed through pyannote/voice-activity-detection
- Speech segments were detected using Silero VAD and exported as 48 kHz mono WAV files via FFmpeg
- Filenames: `{datapoint_id}_{start_ms}_{end_ms}.wav`

### ASR Transcripts

Each audio segment was transcribed using Chirp3

- Transcripts are provided alongside audio for reference or comparison.
- Documentation: [Chirp3 Batch Recognize](https://docs.cloud.google.com/speech-to-text/docs/batch-recognize)

Check [Word Error Rate (WER)](#wer) below on how WER is computed

## Dataset Structure

Each sample in the dataset represents a VAD-segmented speech clip paired with its ASR transcript.

| Field      | Type   | Description |
|------------|--------|-------------|
| `wav`      | Audio  | Speech segment audio file (48 kHz mono WAV) |
| `txt`      | String | ASR transcript corresponding to the speech segment |
| `__key__`  | String | Segment identifier formatted as `{datapoint_id}_{start_ms}_{end_ms}` |
| `__url__`  | String | Location of the WebDataset shard (`.tar`) containing the sample |

### Sample Instance (Preview)

```python
{
  'txt': "Okay. So like I mentioned ... [truncated]",

  'wav': <datasets.features._torchcodec.AudioDecoder object>,

  '__key__': '000f07ab58f1b43495f13044ca5dddb9_000255957_000290652',

  '__url__': 'hf://datasets/DATAI-By-ML-Data-Products/english-casual-speech-sample-south-african-accent/data/shard000000.tar'
}
```

### Segment Naming Convention

The `__key__` field encodes traceability metadata:

`{datapoint_id}_{start_ms}_{end_ms}`

| Component    | Description |
|--------------|-------------|
| datapoint_id | Identifier of the original recording track |
| start_ms     | Segment start timestamp (milliseconds) |
| end_ms       | Segment end timestamp (milliseconds) |

All segments are fully traceable to their original recordings and timestamps. Segments from the same `datapoint_id` belong to the same speaker.

## WER

Word Error Rate is calculated by normalizing both Golden Reference and ASR transcripts, aligning them while handling uncertain sections marked with `(??)`, and computing the ratio of errors (substitutions + insertions + deletions) to reference word count using the `jiwer` library.

Documentation: [JiWER](https://jitsi.github.io/jiwer/)

### Golden Reference

Golden reference transcripts were created through manual full-verbatim transcription, capturing speech exactly as spoken.

They represent the most reliable written form of the audio and function as the reference baseline for ASR evaluation.

### WER Process

Note: `(??)` marks unintelligible or uncertain speech identified during manual transcription. These regions indicate that the transcriber could not determine the spoken content with confidence. 
Such segments are excluded from WER scoring, and alignment resumes at the next reliable word match.

- **Text Normalization:** lowercase, digits converted to words, filler words removed, apostrophes stripped, punctuation cleaned  
- **Uncertain Region Handling:** sections marked with `(??)` are excluded; algorithm resyncs by finding the next 2 consecutive matching words  
- **Error Calculation:**
$$
\text{WER} = \frac{S + I + D}{N}
$$

Where:  
- \(S\) = Number of substitutions  
- \(I\) = Number of insertions  
- \(D\) = Number of deletions  
- \(N\) = Total number of words in the reference transcript

### TL;DR

Refer to the `__key__` column to obtain information about the segments.  

It is formatted as:

`{DATAPOINT-ID}_{START-MS}_{END-MS}.wav`

All segments from the same DATAPOINT-ID belong to the same speaker.

### Inquiries

hello@datai.world