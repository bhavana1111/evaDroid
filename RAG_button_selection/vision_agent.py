#First we will check vision Agent
# We will pass history,current_clickables
#and screen shot to LLM 
#We will ask for the best button to click

import base64
import os
from openai import OpenAI
class VisionAgent:
    api_key = os.getenv("api_key")
    client = OpenAI(api_key=api_key)
    def __init__(self,history_labels,screen_image,filtered_actionable):
        self.history_labels = history_labels
        self.screen_image = screen_image
        self.filtered_actionables = filtered_actionable
        self.client = OpenAI(api_key= self.api_key)
    def suggest(self):
        prompt = self.build_vision_prompt(self.filtered_actionables, self.history_labels)
        prompt2= "What buttons are visible on the screen from vision perspective.You have seen the buttons right please select top 3 buttons from them.Give resosn why this are selected and reason because this result swill be used by orchetsrator to select the best button from RAG based selection also.One more thing to consider I have history of clicked buttons, I will provide that  our goal is to get maximum coverage like to click all the buttons available in the app. please only output top 3 buttons to be clicked and notes for orchestrator"
        data_uri = f"data:image/png;base64,{self.screen_image}"
        response=self.client.chat.completions.create(
            model="gpt-5",
            messages=[
                {
                    "role":"user",
                    "content":[
                        {
                            "type":"image_url",
                            "image_url":{
                                "url":data_uri,
                            }
                        },
                        {
                            "type":"text",
                            "text":prompt2
                        }
                    ]
                }
               
            ]
        )
        print("💬 LLM Response:", response.choices[0].message.content)
        return response.choices[0].message.content
    def build_vision_prompt(self,clickables, history):
        clickable_list_str = "\n".join([
        f'- {c["label"]} (bounds: {c["bounds"]})'
        for c in clickables if c.get("label")
    ]) or "None"
        history_list_str = "\n".join([
        f'- {h}' for h in history[-20:]
    ]) or "None"
        prompt = f"""
    You are a mobile UI Vision Agent.
    You will be shown:
    - A screenshot of the current mobile app screen
    - A list of current clickable buttons
    - A history of the last 20 button clicks
    Your task:
    1. Analyze the screenshot and clickables.
    2. Choose the **top 3 buttons** that are most likely to explore new areas of the app or improve coverage.
    3. If a button has already been clicked, and you believe that path has been fully explored, avoid suggesting it.
    4. Prioritize new, unexplored paths for maximum app exploration.
    Clickables:{clickable_list_str}
    History:{history_list_str}
    Output Format (strict):
    [
    {{"label": "<button_label>", "reason": "<why this button helps explore>"}},
  ...
]
This output will be compared with a RAG-based agent.
Make your decision carefully based on UI, history, and clickables.
"""
        return prompt.strip()



if __name__ == "__main__":
    # Sample input
    history_labels = ["Home", "Menu"]
    with open("screen.png", "rb") as f:
        screen_image = base64.b64encode(f.read()).decode("utf-8")
    
    filtered_actionable = [
        {"label": "Offers", "bounds": "[10,20][100,120]"},
        {"label": "Cart", "bounds": "[200,300][300,400]"},
        {"label": "Settings", "bounds": "[500,600][700,800]"},
        {"label": "Plese Click me to explore more", "bounds": "[600,600][800,800]"},
    ]

    agent = VisionAgent(history_labels, screen_image, filtered_actionable)
    top_choices = agent.suggest()
    print("Top 3 buttons:", top_choices)