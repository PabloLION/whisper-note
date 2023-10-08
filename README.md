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

## Use

- Large model will cause the script to run slow: the recognition happens slower than a constantly speaking person, with M1 Ultra 128GB RAM.
- Recommend to use small model: It's faster and the recognition is not bad.

## Dev

Most of this should be converted to GitHub Issues when published.

- Trying to use [result](https://pypi.org/project/result/) to handle error, not sure how it feels.
- The idea is to build something to substitute Otter to take notes.
  - Check and try speech recognition package
- Features:
  - export to PDF/TXT/...
  - w/(o) translation, etc.
  - Different models by user speech input
  - Add export of full wav file. (can be chunked)
  - summary of the text with ChatGPT
  - input aggregated wav file for better recognition, translation, etc.
  - generate .SRT substitute
  - use dynamic .now() as a default name for the merged file
- UI:
  - Add a debug panel
  - use more "rich" for error, etc.
  - start/end control
  - Maybe add [textual](https://github.com/Textualize/textual) as a front end
  - Add a "Recording..." indicator every 5 seconds the input is idle.
  - Add logger to distinguish between log and model output
  - show queue length
- For translation, it seems that [DeepL](https://www.deepl.com/translator) is the best option, but it's not free. Given I don't need it, just doing the most basic thing: translate the text with some API.

## Special thanks

- AI Model [OpenAI/whisper](https://github.com/openai/whisper)
- real time script [davabase/whisper_real_time](https://github.com/davabase/whisper_real_time)
