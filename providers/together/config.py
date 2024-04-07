import os
import warnings
warnings.filterwarnings('ignore')
import dotenv
dotenv.load_dotenv()
from openai import OpenAI


TOGETHER_URL = os.environ.get("TOGETHER_URL")
TOGETHER_API_KEY = os.environ.get("TOGETHER_API_KEY")


def get_together_client():
    return OpenAI(
        api_key=TOGETHER_API_KEY,
        base_url='https://api.together.xyz/v1',
    )