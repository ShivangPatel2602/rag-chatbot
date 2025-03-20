import environ
import google.generativeai as genai

env = environ.Env()
environ.Env.read_env()

GOOGLE_API_KEY = env("GEMINI_API_KEY")

genai.configure(api_key=GOOGLE_API_KEY)