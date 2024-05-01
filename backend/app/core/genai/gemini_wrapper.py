import os
import google.generativeai as genai

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Set up the model
generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 0,
  "max_output_tokens": 8192,
}

safety_settings = [
  {
    "category": "HARM_CATEGORY_HARASSMENT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_HATE_SPEECH",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
]

system_instruction = """
You are helping someone create a dashboard.

Your job is to look at a sample of their data and then ask a series of questions
to help you undestand what the person wants to accomplish with their dashboard.
Once you have enough information you will generate the complete dashboard code using streamlit. 
The code should be general and be able to run with no user intervention.
Use environment variables as needed and define them at the very top of the code. For the data, always use the env var CSV_PATH=os.getenv("CSV_PATH").
If you respond with code, you cannot include anything else. No context or explanations. Only code enclosed in ```python<code>```
"""


def start_gemini_session(lite: bool = False) -> genai.ChatSession:
  if lite:
      model = genai.GenerativeModel(
          model_name="gemini-1.0-pro",
          generation_config=generation_config,
          # system_instruction=system_instruction,
          safety_settings=safety_settings
      )
  else:
      model = genai.GenerativeModel(
          model_name="gemini-1.5-pro-latest",
          generation_config=generation_config,
          system_instruction=system_instruction,
          safety_settings=safety_settings
      )

  model._system_instruction
  convo = model.start_chat(history=[])
  return convo

# not in use for now, may use if we need custom logic for the gemini session
class GeminiSession:
    def __init__(self) -> None:
        self.__history = []
        self.model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest",
                              generation_config=generation_config,
                              safety_settings=safety_settings)
    
    def __add_message(self, message: str, role: str) -> None:
        self.__history.append({
            "role": role,
            "parts": [message]
        })

    def last_message(self) -> dict[str, str]:
        return self.__history[-1]

    async def generate_response(self, message: str) -> str:
        self.__add_message(message, "user")
        response = await self.model.generate_content_async(self.__history)
        resp_text = response.text
        self.__add_message(resp_text, "model")
        return resp_text