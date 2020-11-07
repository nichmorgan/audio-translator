import asyncio
import io
import numpy as np

import sounddevice as sd
from scipy.io.wavfile import write, read


async def record_audio(buffer, **kwargs):
    loop = asyncio.get_event_loop()
    event = asyncio.Event()
    idx = 0

    def callback(indata, frame_count, time_info, status):
        nonlocal idx
        if status:
            print(status)
        remainder = len(buffer) - idx
        if remainder == 0:
            loop.call_soon_threadsafe(event.set)
            raise sd.CallbackStop
        indata = indata[:remainder]
        buffer[idx:idx + len(indata)] = indata
        idx += len(indata)

    stream = sd.InputStream(callback=callback, dtype=buffer.dtype,
                            channels=buffer.shape[1], **kwargs)
    with stream:
        await event.wait()


async def play_audio(buffer, **kwargs):
    loop = asyncio.get_event_loop()
    event = asyncio.Event()
    idx = 0

    def callback(outdata, frame_count, time_info, status):
        nonlocal idx
        if status:
            print(status)
        remainder = len(buffer) - idx
        if remainder == 0:
            loop.call_soon_threadsafe(event.set)
            raise sd.CallbackStop
        valid_frames = frame_count if remainder >= frame_count else remainder
        outdata[:valid_frames] = buffer[idx:idx + valid_frames]
        outdata[valid_frames:] = 0
        idx += valid_frames

    stream = sd.OutputStream(callback=callback, dtype=buffer.dtype,
                             channels=buffer.shape[1], **kwargs)
    with stream:
        await event.wait()


def numpy_audio_to_bytesio(data):
    stream = io.BytesIO()
    scaled = np.int16(data/np.max(np.abs(data)) * 32767)
    write(stream, 44100, scaled)
    return stream


def save_binary_to_file(data, filename='audio.wav'):
    buffer = data
    if isinstance(data, io.BytesIO):
        buffer = buffer.read()
        data.seek(0)

    with open(filename, 'wb') as f:
        f.write(buffer)


def save_numpy_audio_to_file(data, filename='audio.wav'):
    stream = numpy_audio_to_bytesio(data)
    save_binary_to_file(stream, filename)