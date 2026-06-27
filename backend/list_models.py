import google.generativeai as genai
import os
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))
import backend.config as config

genai.configure(api_key=config.GEMINI_API_KEY)
for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        print(m.name)
