"""Media player."""

# https://github.com/jaseg/python-mpv

import mpv


def play_file(path, start=None):
    """Play media."""
    # gain = get_gain(path)
    def my_log(loglevel, component, message):
        print('[{}] {}: {}'.format(loglevel, component, message))

    player = mpv.MPV(log_handler=my_log, ytdl=True,
                     input_default_bindings=True, input_vo_keyboard=True)

    @player.property_observer('time-pos')
    def time_observer(_name, value):
        # Here, _value is either None if nothing is playing or a float
        # containing fractional seconds since the beginning of the file.
        print('Now playing at {:.2f}s'.format(value))

    player.play(path)
    player.wait_for_playback()
    del player


def ex1():
    def my_log(loglevel, component, message):
        print('[{}] {}: {}'.format(loglevel, component, message))

    player = mpv.MPV(log_handler=my_log, ytdl=True,
                     input_default_bindings=True, input_vo_keyboard=True)

    # Property access, these can be changed at runtime
    @player.property_observer('time-pos')
    def time_observer(_name, value):
        # Here, _value is either None if nothing is playing or a float
        # containing fractional seconds since the beginning of the file.
        print('Now playing at {:.2f}s'.format(value))

    player.fullscreen = True
    player.loop_playlist = 'inf'
    # Option access, in general these require the core to reinitialize
    player['vo'] = 'opengl'

    @player.on_key_press('q')
    def my_q_binding():
        print('THERE IS NO ESCAPE')

    # @player.on_key_press('s')
    # def my_s_binding():
    #     pillow_img = player.screenshot_raw()
    #     pillow_img.save('screenshot.png')

    player.play('https://youtu.be/DLzxrzFCyOs')
    player.wait_for_playback()

    del player


def ex2():
    player = mpv.MPV(ytdl=True, input_default_bindings=True,
                     input_vo_keyboard=True)

    player.playlist_append('https://youtu.be/PHIGke6Yzh8')
    player.playlist_append('https://youtu.be/Ji9qSuQapFY')
    player.playlist_append('https://youtu.be/6f78_Tf4Tdk')

    player.playlist_pos = 0

    while True:
        # To modify the playlist, use
        # player.playlist_{append,clear,move,remove}.
        # player.playlist is read-only
        print(player.playlist)
        player.wait_for_playback()
