"""Probe media."""

# TODO: https://pymediainfo.readthedocs.io/

import sys
from datetime import timedelta
from pprint import pprint

import ffmpeg

from .. import time


class MediaProbe:
    """..."""

    def __init__(self, path):
        """..."""
        self.path = path
        d = ffmpeg.probe(path)
        assert len(d) == 2, d.keys()
        self.format = d['format']
        self.streams = d['streams']

    @property
    def duration(self):
        return timedelta(seconds=float(self.format['duration']))


def cli_probemedia():
    """..."""
    # for path in sys.argv[1:]:
    #     print('####', path)
    #     for k, v in ffmpeg.probe(path).items():
    #         print('##', k)
    #         pprint(v)
    for path in sys.argv[1:]:
        probe = MediaProbe(path)
        print('####', probe.path)
        print('##', probe.duration, time.fmt_duration(probe.duration))
        print('## format')
        pprint(probe.format)
        print('## streams')
        pprint(probe.streams)


# #### /home/jupito/tmp/video/Sturmtruppen 2 - Tutti al Fronte (VhsRip).avi
# ## format
# {'bit_rate': '1038760',
#  'duration': '5273.139806',
#  'filename': '/home/jupito/tmp/video/Sturmtruppen 2 - Tutti al Fronte '
#              '(VhsRip).avi',
#  'format_long_name': 'AVI (Audio Video Interleaved)',
#  'format_name': 'avi',
#  'nb_programs': 0,
#  'nb_streams': 2,
#  'probe_score': 100,
#  'size': '684690936',
#  'start_time': '0.000000'}
# ## streams
# [{'avg_frame_rate': '2997/100',
#   'bit_rate': '898951',
#   'chroma_location': 'left',
#   'codec_long_name': 'MPEG-4 part 2',
#   'codec_name': 'mpeg4',
#   'codec_tag': '0x30355844',
#   'codec_tag_string': 'DX50',
#   'codec_time_base': '100/2997',
#   'codec_type': 'video',
#   'coded_height': 400,
#   'coded_width': 512,
#   'display_aspect_ratio': '32:25',
#   'disposition': {'attached_pic': 0,
#                   'clean_effects': 0,
#                   'comment': 0,
#                   'default': 0,
#                   'dub': 0,
#                   'forced': 0,
#                   'hearing_impaired': 0,
#                   'karaoke': 0,
#                   'lyrics': 0,
#                   'original': 0,
#                   'timed_thumbnails': 0,
#                   'visual_impaired': 0},
#   'divx_packed': 'false',
#   'duration': '5273.139806',
#   'duration_ts': 158036,
#   'has_b_frames': 1,
#   'height': 400,
#   'index': 0,
#   'level': -99,
#   'nb_frames': '158036',
#   'pix_fmt': 'yuv420p',
#   'quarter_sample': 'false',
#   'r_frame_rate': '30000/1001',
#   'refs': 1,
#   'sample_aspect_ratio': '1:1',
#   'start_pts': 0,
#   'start_time': '0.000000',
#   'time_base': '100/2997',
#   'width': 512},
#  {'avg_frame_rate': '0/0',
#   'bit_rate': '128000',
#   'bits_per_sample': 0,
#   'channel_layout': 'stereo',
#   'channels': 2,
#   'codec_long_name': 'MP3 (MPEG audio layer 3)',
#   'codec_name': 'mp3',
#   'codec_tag': '0x0055',
#   'codec_tag_string': 'U[0][0][0]',
#   'codec_time_base': '1/44100',
#   'codec_type': 'audio',
#   'disposition': {'attached_pic': 0,
#                   'clean_effects': 0,
#                   'comment': 0,
#                   'default': 0,
#                   'dub': 0,
#                   'forced': 0,
#                   'hearing_impaired': 0,
#                   'karaoke': 0,
#                   'lyrics': 0,
#                   'original': 0,
#                   'timed_thumbnails': 0,
#                   'visual_impaired': 0},
#   'index': 1,
#   'nb_frames': '84366235',
#   'r_frame_rate': '0/0',
#   'sample_fmt': 'fltp',
#   'sample_rate': '44100',
#   'start_pts': 0,
#   'start_time': '0.000000',
#   'time_base': '1/16000'}]
