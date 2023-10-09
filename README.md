## Key Features

- **Live Speech Recognition and Transcription:** Automatically transcribe spoken words in real time (cannot be turned off).
- **Detailed Live Transcript:** View a live transcript of your conversation, including translations, and see the queue length.
- **Select Input Language:** Choose your preferred input language.
- **Optional Real-Time Translation:** Get instant translations of spoken content if needed.
- **Choose Model Size:** Select the model size that suits your needs.
- **Language-Specific Models:** Utilize models tailored for specific languages.
- **Export Trimmed Recordings:** Easily save trimmed `.wav` files of your recordings without silent gaps.
- **Export Transcript History:** Save your entire transcript history as an `.html` file.
- **High-Quality Transcription:** Optionally receive high-quality transcription after the recording is completed.
- **Upcoming Feature:** Stay tuned for an optional summary of the transcript generated with the help of ChatGPT.

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
- See the comment in `config.yml` for more details.

## Dev

### Env setup

- Suppose you have [`poetry`](https://python-poetry.org/) installed on your machine with `python@3.11`.
- Assume `pwd` is the root of this repo.

```zsh
poetry install --with dev
poetry run pre-commit install
touch .env
```

- Get an API key from DeepL and put it in `.env` in the root of this repo, like this:

  ```plaintext
  DEEPL_API_KEY=1234567890
  ```

- Maybe setup your own config file. #TODO: default config file
- #TODO: use `make` to make this easier

### Memo

Most of this should be converted to GitHub Issues when published.

- Trying to use [result](https://pypi.org/project/result/) to handle error, not sure how it feels.
- The idea is to build something to substitute Otter to take notes.
  - Check and try speech recognition package
- Features:
  - summary of the text with ChatGPT
  - generate .SRT substitute
  - Add DEV_MODE env variable, in which mode logger should be more verbose
- UI:
  - start/end control
  - Not needed: Add a "Still Recording..." indicator every 5 seconds the input is idle.
- For translation, it seems that [DeepL](https://www.deepl.com/translator) is the best option, but it's not free. Given I don't need it, just doing the most basic thing: translate the text with some API.
- I tried to use [textual](https://github.com/Textualize/textual) but the CSS is not applied on the dynamically rendered list items. And it's not easy to use. Maybe use electron / eel instead if we want a web UI.

## Special thanks

- AI Model [OpenAI/whisper](https://github.com/openai/whisper)
- real time transcript script [davabase/whisper_real_time](https://github.com/davabase/whisper_real_time)
