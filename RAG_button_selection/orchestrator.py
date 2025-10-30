from openai import OpenAI
from vision_agent import VisionAgent
import base64
import os

class Orchestrator:
    api_key = os.getenv("api_key")
    client = OpenAI(api_key=api_key)
    def __init__(self,history_labels,filtered_actionable,screen_image):
        self.history_labels = history_labels
        self.filtered_actionables = filtered_actionable
        self.screen_image = screen_image
        self.client = OpenAI(api_key= self.api_key)
    def buttonToBeClicked(self):
        visionAgent = VisionAgent(
            history_labels=self.history_labels,
            screen_image=self.screen_image,
            filtered_actionable=self.filtered_actionables)
        result = visionAgent.suggest()
        prompt = f"Top 3 buttons and reason to click that button from Vision Agent {result}"
        response=self.client.chat.completions.create(
            model="gpt-5",
            messages=[
                {
                    "role":"user",
                    "content":[
                        {
                            "type":"text",
                            "text":prompt
                        }
                    ]
                }
               
            ]
        )


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

    orch = Orchestrator(history_labels, filtered_actionable, screen_image)
    top_choices = orch.buttonToBeClicked()
    print("Top 3 buttons:", top_choices)