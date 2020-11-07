import asyncio
import sys

import numpy as np

import audio
import ibm

channels = 1
frames = 250_000


async def main(**kwargs):
    buffer = np.empty((frames, channels), dtype='float32', )
    print('Gravando ...')
    await audio.record_audio(buffer, **kwargs)
    print('Reproduzindo ...')
    await audio.play_audio(buffer, **kwargs)
    print('done')

    stream = audio.numpy_audio_to_bytesio(buffer)
    audio.save_binary_to_file(stream, 'input.wav')

    status, text, score = ibm.speech_to_text(stream)
    if not status:
        raise Exception('A transcrição do audio falhou')
    else:
        print(f'Texto de entrada: {text} | Score: {score}')

    text = ibm.translate_text(text, 'pt-en')
    print(f'Texto traduzido: {text}')

    output_stream = ibm.text_to_speech(text)
    audio.save_binary_to_file(output_stream, 'output.wav')


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit('\nInterrompido pelo usuário')
