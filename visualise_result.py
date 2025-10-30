import json
import matplotlib.pyplot as plt

with open("button_rewards.json", "r") as f:
    rewards = json.load(f)

sorted_rewards = sorted(rewards.items(), key=lambda x: x[1], reverse=True)

top_buttons = sorted_rewards[:-1]
labels, values = zip(*top_buttons)

plt.barh(labels, values)
plt.xlabel("Reward")
plt.title("Top 10 Buttons by Reward")
plt.gca().invert_yaxis()
plt.tight_layout()
plt.show()
