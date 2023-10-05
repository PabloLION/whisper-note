## Install

### Mac with Apple Silicon

```zsh
brew install portaudio # src/pyaudio/device_api.c:9:10: fatal error: 'portaudio.h' file not found
brew install ffmpeg
brew install mbedtls # /opt/homebrew/Cellar/mbedtls/3.4.1/lib/libmbedcrypto.13.dylib
```

After this, my mbedtls@3.4.1 gives only a `libmbedcrypto.14.dylib` but I renamed it manually:

```zsh
cp /opt/homebrew/Cellar/mbedtls/3.4.1/lib/libmbedcrypto.13.dylib /opt/homebrew/Cellar/mbedtls/3.4.1/lib/libmbedcrypto.14.dylib
```

Then setup the virtual environment and install the requirements with poetry:

```zsh
poetry install
```

### Not supported

I don't know how to install these.

- Windows
- Linux
- Mac with Intel

## Dev

Most of this should be converted to GitHub Issues when published.

- Trying to use [result](https://pypi.org/project/result/) to handle error, not sure how it feels.
- The idea is to build something to substitute Otter to take notes.
  - Check speech recognition
  - UI: start/end, args, export to PDF/TXT/..., clean transcription, etc.
  - Maybe add [textual](https://github.com/Textualize/textual) as a front end
  - Run model by user speech input
  - Try small and fast English only model

## Special thanks

- AI Model [OpenAI/whisper](https://github.com/openai/whisper)
- real time script [davabase/whisper_real_time](https://github.com/davabase/whisper_real_time)
