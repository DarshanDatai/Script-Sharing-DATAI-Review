---
license: cc-by-4.0
language:
- en
pretty_name: KE/PH English Dialogue
tags:
- audio
- accent
size_categories:
- 10K<n<100K
---

# Kenya/Philippines English Dialogue
Two-speaker dialogues in English, recorded on split tracks.
## Changelog
`Jan 2026`: v1 release - vad-segmented WebRTC tracks
## Specs
- Speakers: >150; ~15 PH, remaining KE
- Total duration: ~65 hours
- Files sample rate: 48kHz
- Actual sample rate: TBD
- Language: English (PH, KE accents)
- Topics: day-to-day conversation
## Collection method
The dataset is built to capture the variety in the Kenyan accent.

The Philippino interviewers are instructed to carry out natural conversations about daily life topics with crowd sourced Kenyans.

The conversation happens via WebRTC and both participants are recorded on-cloud in Opus format.

The recording mechanism currently creates a separate track on each connection.
A Kenyan interviewee who's connection drops will appear across multiple tracks in the same room.
Speakers will be clustered in the next release.
See usage section for more details.
## Processing
- Transcoding from Opus 48kHz to pcm_s16le
- silero-vad chunking into 1 to 30 seconds segments
- TBD
## Usage
Refer to the `__key__` column to obtain information about the segments.

It is formatted as follows:
`ROOM-ID_TRACK-ID_START-MILLISECONDS_END-MILLISECONDS`

A `ROOM-ID` usually hosts one conversation between the two participants.

The `TRACK-ID` indicates from which track the segment was taken.

*Note:* all segments from the same track belong to one speaker. 
Segments from two tracks in the same room might belong to the same speaker, if they reconnected.
### Inquiries
`hello@datai.world`