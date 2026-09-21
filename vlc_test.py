import vlc
import time
import os

VLC_PATH = r"C:\Program Files (x86)\VideoLAN\VLC"

player = vlc.Instance(
    f'--plugin-path={VLC_PATH}\\plugins'
).media_player_new()

media = player.get_media(
    os.path.abspath("jarvis_test.mp3")
)

player.set_media(media)
player.play()

time.sleep(6)

player.stop()

print("VLC test finished.")