import google.generativeai as genai
from utils import load_json

api_keys = load_json("api_keys.json")


def gemini_model(api_key = api_keys["google_api_studio"], model_name = "gemini-1.5-flash"):
    genai.configure(api_key=api_keys["google_api_studio"])
    model = genai.GenerativeModel(model_name, system_instruction="You are an expert resume builder.")   
    return model


def call_gemini_api(input_text, model, temperature):
    """
    Call the GPT-3 API to generate text based on user input.
    """
    response = model.generate_content(input_text, generation_config=genai.types.GenerationConfig(temperature=temperature) ,stream=False)
    response = response.candidates[0].content.parts[0].text
    return response
    

#response = model.generate_content("Explain how AI works")