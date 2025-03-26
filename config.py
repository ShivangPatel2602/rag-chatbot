import environ
from openai import OpenAI

env = environ.Env()
environ.Env.read_env()

OPENAI_API_KEY = env("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)