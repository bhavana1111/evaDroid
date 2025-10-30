import re
import subprocess
import xml.etree.ElementTree as ET
import time
import hashlib
from collections import defaultdict
from rag_model import completion_model
import boto3
from RAG_button_selection_new.vision_agent import selectReasonAndButtonFromImg
from RAG_button_selection_new.rag_agent import selectReasonAndButtonFromRAG
from RAG_button_selection_new.orchestrator import getButtonTobeClicked
history = []
screen_clickables = dict()
screen_visit_counts = defaultdict(int)
screen_scroll_attempts = defaultdict(int)
BUCKET_NAME = "dump-images-ra"
REGION = "us-east-2"

start_time = time.time()
max_duration = 60 * 60  # 30 minutes
XML_PATH = './dump/window_dump.xml'
start_activity = "com.mcdonalds.app/com.mcdonalds.mcdcoreapp.common.activity.SplashActivity"
package_name = "com.mcdonalds.app"

scrollable_layouts = {
    "androidx.recyclerview.widget.RecyclerView",
    "android.widget.ScrollView",
    "android.widget.HorizontalScrollView",
    "android.widget.ListView"
}

def normalize(text):
    return text.strip().lower() if text else ""

def restart_app():
    global screen_visit_counts
    global screen_scroll_attempts
    print("🔄 Restarting app...")
    subprocess.call(f"adb shell am force-stop {package_name}", shell=True)
    time.sleep(2)
    subprocess.call(f"adb shell am start -n {start_activity}", shell=True)
    time.sleep(8)
    screen_visit_counts = defaultdict(int)
    screen_scroll_attempts = defaultdict(int)

def scroll_down():
    print("🔽 Scrolling down...")
    subprocess.run("adb shell input swipe 500 1500 500 500", shell=True)
    time.sleep(2)

def ensure_in_test_app():
    try:
        output = subprocess.check_output(
            'adb shell dumpsys activity activities',
            shell=True, text=True
        )
        found_resumed = False
        for line in output.splitlines():
            if "mResumedActivity" in line or "ResumedActivity" in line:
                found_resumed = True
                if package_name in line:
                    print("✅ App is in foreground.")
                    return
                else:
                    print("🚫 Another app in foreground. Restarting app...")
                    restart_app()
                    return
        if not found_resumed:
            print("⚠️ Could not find resumed activity info. Restarting app...")
            restart_app()
    except subprocess.CalledProcessError as e:
        print(f"⚠️ Error checking foreground: {e}. Restarting app as fallback...")
        restart_app()

def create_dump():
    subprocess.call("adb shell uiautomator dump", shell=True)
    subprocess.call("adb pull /sdcard/window_dump.xml ./dump", shell=True)
    print("📸 Dump created.")

def get_display_name_from_node_and_children(node):
    text = node.attrib.get("text", "").strip()
    desc = node.attrib.get("content-desc", "").strip()
    res_id = node.attrib.get("resource-id", "").strip()
    if text:
        return text
    if desc:
        return desc
    if res_id:
        return res_id
    for child in node:
        name = get_display_name_from_node_and_children(child)
        if name:
            return name
    return None

def extract_clickables(xml_path):
    tree = ET.parse(xml_path)
    root = tree.getroot()
    clickables = []

    def traverse(node, parent=None):
        a = node.attrib
        cls = a.get("class", "")
        text = a.get("text", "").strip()
        desc = a.get("content-desc", "").strip()
        res_id = a.get("resource-id", "").strip()
        bounds = a.get("bounds", "").strip()
        clickable_attr = a.get("clickable") == "true"

        is_clickable = (
            clickable_attr or text or desc
        ) and bounds != "[0,0][0,0]"

        if is_clickable:
            if cls in {"android.widget.FrameLayout", "android.widget.LinearLayout", "android.view.ViewGroup"}:
                if not (text or desc):
                    is_clickable = False

        if is_clickable:
            parent_class = parent.attrib.get("class", "") if parent is not None else "ROOT"
            parent_children = list(parent) if parent is not None else []
            index = parent_children.index(node) if node in parent_children else -1

            clickables.append({
                "node": node,
                "text": text,
                "desc": desc,
                "res_id": res_id,
                "class": cls,
                "bounds": bounds,
                "parent_class": parent_class,
                "index": index
            })

        for child in node:
            traverse(child, node)

    traverse(root)
    return clickables

def tap(bounds):
    coords = list(map(int, re.findall(r'\d+', bounds)))
    if len(coords) == 4:
        x = (coords[0] + coords[2]) // 2
        y = (coords[1] + coords[3]) // 2
        subprocess.run(f"adb shell input tap {x} {y}", shell=True)
        print(f"✅ Tapped at ({x}, {y})")
        return True
    return False

def log_for_vectorization(clickables, history, button):
    local_clickables = [
        f'{c["res_id"]}|{c["text"]}|{c["desc"]}|class={c["class"]}|parent={c["parent_class"]}|index={c["index"]}'
        for c in clickables
    ]
    local_history = [
        f'{h["res_id"]}|class={h["class"]}|parent={h["parent_class"]}' for h in history
    ]
    with open("vector_log_local_rag.txt", "a", encoding="utf-8") as f:
        f.write("clickables:" + str(local_clickables) + "\n")
        f.write("history:" + str(local_history) + "\n")
        f.write("next_button:" + str(button) + "\n")
        f.write("-" * 100 + "\n")

def is_actionable(c):
    if not c.get("bounds") or c["bounds"] == "[0,0][0,0]":
        return False
    node = c.get("node")
    if node is None:
        return False
    cls = (c.get("class") or "").lower()
    text = (c.get("text") or "").lower()
    desc = (c.get("desc") or "").lower()

    if text in ["background image", ""] and desc in ["", None]:
        return False

    if node.attrib.get("clickable") == "true":
        if cls in ["android.widget.framelayout", "android.widget.linearlayout", "android.view.viewgroup"]:
            if not (text or desc):
                return False
        return True

    if any(w in cls for w in ["button", "imageview", "checkbox", "radiobutton"]):
        return True

    if "tab" in cls and (desc or text):
        return True

    return False
def take_screenshot(local_path="screen.png"):
    try :
        subprocess.run("adb shell screencap -p /sdcard/screen.png", shell=True, check=True)
        subprocess.run("adb pull /sdcard/screen.png {}".format(local_path), shell=True, check=True)
        return local_path
    except Exception as e:
        print("error with taking SS")
        restart_app()
   

def upload_to_s3(file_path, bucket=BUCKET_NAME, region=REGION):
    s3 = boto3.client("s3")
    key = f"screen.png"
    s3.upload_file(file_path, bucket, key, ExtraArgs={'ACL': 'public-read', 'ContentType': 'image/png'})
    url = f"https://{bucket}.s3.{region}.amazonaws.com/{key}"
    return url

# === MAIN LOOP ===
restart_app()
while time.time() - start_time < max_duration:
    ensure_in_test_app()
    create_dump()
    clickables = extract_clickables(XML_PATH)

    if not clickables:
        print("❌ No clickables. Restarting.")
        restart_app()
        continue
    screen_sig = hashlib.md5("".join([c["res_id"] + c["bounds"] for c in clickables]).encode()).hexdigest()
    screen_visit_counts[screen_sig] += 1
    if screen_visit_counts[screen_sig] == 3:
        scroll_down()
    screen_scroll_attempts[screen_sig] += 1
    if screen_scroll_attempts[screen_sig] >= 2:
        print("🔁 Too many scrolls. Restarting app.")
        restart_app()
        continue
    if screen_visit_counts[screen_sig] > 5:
        print("🔁 Seen screen too many times. Restarting app.")
        restart_app()
        continue

    actionables = clickables
    # actionables = [c for c in clickables if is_actionable(c)]
    print('actionables count = ',len(clickables))
    if not actionables:
        print("❌ No actionable elements. Restarting.")
        restart_app()
        continue

    filtered_actionables = [c for c in actionables if c.get("text") or c.get("desc")]
    if not filtered_actionables:
        print("❌ No labeled buttons to send to LLM. Restarting.")
        restart_app()
        continue
    #upload a ss to AWS s3 --helper to upload to s3 and get url
    #Get a url from AWS
    try:
        local_path = take_screenshot()
        url = upload_to_s3(local_path)
        result_from_vision = selectReasonAndButtonFromImg(url,clickables,history)
    except Exception as e:
        url = ""
        result_from_vision = []    
    local_clickables = [
        f'{c["res_id"]}|{c["text"]}|{c["desc"]}|class={c["class"]}|parent={c["parent_class"]}|index={c["index"]}'
        for c in filtered_actionables
    ]
    local_history = [
        f'{h["res_id"]}|class={h["class"]}|parent={h["parent_class"]}' for h in history
    ]
    result_from_RAG = selectReasonAndButtonFromRAG(local_clickables,local_history,clickables,history)
    button = getButtonTobeClicked(result_from_vision,result_from_RAG,clickables,history)
    # button, reason = completion_model(filtered_actionables, history)
    # print("🔘 Button selected:", button)
    # print("🧠 Reason:", reason)
    selected = None
    for c in filtered_actionables:
        label = (c.get("text") or c.get("desc") or get_display_name_from_node_and_children(c["node"]) or c.get("class", "")).strip()
        if normalize(label) == normalize(button):
            selected = c
            print("Please give the result",selected)
            break

    if not selected and filtered_actionables:
        selected = filtered_actionables[0]
        print("⚠️ Fallback: Selecting first labeled button")

    if selected and tap(selected["bounds"]):
        history.append(selected)
        log_for_vectorization(clickables, history, button)
        time.sleep(3)
        create_dump()
    else:
        print("❌ Button not found or tap failed. Restarting.")
        restart_app()

    time.sleep(5)

print("✅ Done.")
