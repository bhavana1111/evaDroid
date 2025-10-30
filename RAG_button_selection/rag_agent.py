from logToDb.query import convertQueryToEmbedding,queryResult
from openai import OpenAI
import os

class RAGAgent:
    api_key = os.getenv("api_key")
    client = OpenAI(api_key=api_key)
    def __init__(self,history_labels,clickables):
        self.history_labels = history_labels
        self.clickables = clickables
        self.client = OpenAI(
            api_key= self.api_key
        )
    
    def getTop10Matching(self):
        queryEmbedding = convertQueryToEmbedding(self.clickables, self.history_labels)
        top_10_matching_buttons_with_rewards = queryResult(queryEmbedding)
        return top_10_matching_buttons_with_rewards
    def getButtonToBeClicked(self):
        clickables_from_db = self.getTop10Matching()
        print(clickables_from_db)

if __name__ == "__main__":
    # Sample input
    history_labels = ["Home", "Menu"]
    
    filtered_actionable = [
        {"label": "Offers", "bounds": "[10,20][100,120]"},
        {"label": "Cart", "bounds": "[200,300][300,400]"},
        {"label": "Settings", "bounds": "[500,600][700,800]"},
        {"label": "Plese Click me to explore more", "bounds": "[600,600][800,800]"},
    ]

    orch = RAGAgent(history_labels, filtered_actionable)
    top_choices = orch.getButtonToBeClicked()
    print("Top 3 buttons:", top_choices)