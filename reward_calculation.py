import json
import ast
import networkx as nx
from collections import defaultdict

# ---------------------------- CONFIG ----------------------------
INPUT_LOG_FILE = r"C:\Users\bhava\new_files\new_files\travel\viator\viator_random.txt"
OUTPUT_REWARD_FILE = "button_rewards.json"
DOMINANCE_WEIGHT = 1

# -------------------------- UTILITIES ---------------------------
def extract_set(button_list):
    return set(btn for btn in button_list if btn.strip())

def resolve_clickable_match(next_button, clickables):
    cleaned_btn = next_button.strip().lower()
    for clickable in clickables:
        parts = [p.strip().lower() for p in clickable.split('|')]
        if cleaned_btn in parts[1:3]:
            return clickable
    for clickable in clickables:
        if cleaned_btn and cleaned_btn in clickable.lower():
            return clickable
    return None

def parse_log_file(filename):
    steps = []
    with open(filename, "r", encoding="utf-8") as f:
        step = {}
        for line in f:
            line = line.strip()
            if line.startswith("clickables:"):
                raw = line.replace("clickables:", "").strip()
                try:
                    parsed = ast.literal_eval(raw)
                    step["clickables"] = [x for x in parsed if x.strip()]
                except Exception:
                    step["clickables"] = []
            elif line.startswith("history:"):
                raw = line.replace("history:", "").strip()
                try:
                    parsed = ast.literal_eval(raw)
                    step["history"] = [x for x in parsed if x.strip()]
                except Exception:
                    step["history"] = []
            elif line.startswith("next_button:"):
                next_btn = line.replace("next_button:", "").strip()
                if not next_btn:
                    continue
                step["next_button"] = next_btn
            elif line.startswith("-"):
                if step:
                    steps.append(step)
                    step = {}
        if step:  # Append last step if file doesn’t end with ----
            steps.append(step)
    print(f"📋 Total steps parsed: {len(steps)}")
    return steps

# -------------------- DOMINANCE GRAPH BUILD ---------------------
def build_dominance_graph(data):
    G = nx.DiGraph()
    last_clicked = "ENTRY_NODE"
    for entry in data:
        available = extract_set(entry.get("clickables", []))
        clicked = resolve_clickable_match(entry.get("next_button", ""), entry.get("clickables", []))
        if not clicked:
            continue
        for btn in available:
            if btn != last_clicked:
                G.add_edge(last_clicked, btn)
        last_clicked = clicked
    return G

# -------------------- REWARD CALCULATION ------------------------
def calculate_rewards(steps, graph):
    reward_map = defaultdict(list)
    seen_clickables = set()
    seen_screens = set()

    for i in range(len(steps) - 1):
        current = steps[i]
        next_step = steps[i + 1]

        print(f"\n⏭ Step {i} - Next Button: {current.get('next_button')}")
        current_clickables = extract_set(current.get("clickables", []))
        next_clickables = extract_set(next_step.get("clickables", []))

        new_clickables = next_clickables - current_clickables

        screen_sig = hash(frozenset(current_clickables))
        next_screen_sig = hash(frozenset(next_clickables))

        reward = 0
        reward += len(new_clickables)
        if screen_sig != next_screen_sig:
            reward += 2

        matched_clickable = resolve_clickable_match(current.get("next_button", ""), current.get("clickables", []))
        print(f"🧩 Matched: {matched_clickable}")

        if matched_clickable and matched_clickable in current.get("history", []):
            reward -= 1
        if screen_sig in seen_screens:
            reward -= 1

        seen_screens.add(screen_sig)
        seen_clickables |= current_clickables

        graph_key = matched_clickable if matched_clickable else current.get("next_button", "")
        dom_score = graph.out_degree(graph_key) if graph.has_node(graph_key) else 0
        reward += DOMINANCE_WEIGHT * dom_score

        reward_map[current.get("next_button", "")].append(reward)
        print(f"🏆 Reward: {reward}")

    average_rewards = {btn: sum(scores) / len(scores) for btn, scores in reward_map.items()}
    print(f"\n🎯 Final reward summary:\n{json.dumps(average_rewards, indent=2)}")
    return average_rewards

# ---------------------------- MAIN ------------------------------
if __name__ == "__main__":
    steps = parse_log_file(INPUT_LOG_FILE)
    dominance_graph = build_dominance_graph(steps)
    reward_result = calculate_rewards(steps, dominance_graph)

    with open(OUTPUT_REWARD_FILE, "w", encoding="utf-8") as f:
        json.dump(reward_result, f, indent=2)

    print(f"\n✅ Button-level reward summary with dominance saved to {OUTPUT_REWARD_FILE} with {len(reward_result)} entries.")
