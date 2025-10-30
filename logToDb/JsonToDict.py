import json

REWARD_FILE = r"C:\Users\bhava\new_files\new_files\button_rewards.json"

with open(REWARD_FILE, "r", encoding="utf-8") as f:
    reward_dict = json.load(f)

print(reward_dict)