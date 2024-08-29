import asyncio
import logging

from shazamio import Shazam

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ShazamService:
    def __init__(self):
        self.shazam = Shazam()

    async def _recognize_song(self, audio_wav_buffer):
        return await self.shazam.recognize(audio_wav_buffer.read())

    def identify_song(self, audio_wav_buffer):
        loop = asyncio.new_event_loop()
        try:
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self._recognize_song(audio_wav_buffer))
        except Exception as ex:
            logger.error(ex)
        finally:
            loop.close()

        if result and 'track' in result:
            track = result['track']
            album_art = track.get('images', {}).get('coverart', 'No cover art available')
            return {
                'title': track.get('title', 'Unknown'),
                'artist': track.get('subtitle', 'Unknown'),
                'album': next((item['text'] for item in track.get('sections', [{}])[0].get('metadata', []) if
                               item.get('title') == 'Album'), 'Unknown'),
                'album_art': album_art
            }
        else:
            return None
