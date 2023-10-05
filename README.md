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

### Not supported

I don't know how to install these.

- Windows
- Linux
- Mac with Intel

## Special thanks

- AI Model [OpenAI/whisper](https://github.com/openai/whisper)
- real time script [davabase/whisper_real_time](https://github.com/davabase/whisper_real_time)
