# main_engine.py
from .vision_agent import VisionAgent
from .rag_agent import RAGAgent
from .orchestrator import Orchestrator
from session_state import  update_actionables

def run_agent_decision_cycle(clickables, filtered_actionables, screen_image, full_history):
    current_package = "com.starbucks.mobilecard"
    # Update shared state
    update_actionables(filtered_actionables)

    # Extract recent history labels
    history_labels = [
        h.get("text") or h.get("desc") or h.get("class", "")
        for h in full_history[-20:]
        if h.get("text") or h.get("desc") or h.get("class")
    ]

    # Run agents
    vision_output = VisionAgent(history_labels,screen_image,filtered_actionables)
    print("Vision O/P",vision_output)
    rag_output = RAGAgent(history_labels).suggest(clickables, full_history)

    # Make decision
    decision = Orchestrator(history_labels).decide(vision_output, rag_output)

    print(f"🎯 Action: {decision['action']} → {decision['label']}")
    print(f"🤖 Agent: {decision['agent']}")
    print(f"🧠 Reason: {decision['reason']}")

    return vision_output["label"], vision_output["reason"]

