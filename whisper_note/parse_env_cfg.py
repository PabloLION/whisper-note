import dotenv
import os

TRANSLATE = "DEEPL"  # or "NONE", GOOGLE, MICROSOFT, AMAZON, YANDEX, PAPAGO, KAKAO
# #TODO: This should move to the config file
dotenv.load_dotenv()


class ConfigLoadingError(ValueError):
    pass


DEEPL_API_KEY = os.getenv("DEEPL_API_KEY")
if TRANSLATE == "DEEPL" and not DEEPL_API_KEY:
    raise ConfigLoadingError("DEEPL_API_KEY is not set in .env file")

parsed_config = {}
parsed_config["TRANSLATE_API_KEY"] = DEEPL_API_KEY
