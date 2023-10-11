import os

from dotenv import load_dotenv

# #TODO: without .env it reports error
ENV_PATH = os.path.join(os.path.dirname(__file__), "..", ".env")
assert os.path.exists(ENV_PATH), f"{ENV_PATH=} not found"
load_dotenv(dotenv_path=ENV_PATH)
