import json
import os
import subprocess
import threading
import time
from pynput import keyboard, mouse

CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "keybi.json")

with open(CONFIG_PATH, encoding="utf-8") as f:
    cfg = json.load(f)

mouse_ctrl = mouse.Controller()
kb_ctrl = keyboard.Controller()

MODIFIER = getattr(keyboard.Key, cfg.get("modifier", "alt_gr"))
REPEAT_DELAY = cfg.get("repeat_delay", 0.3)
REPEAT_RATE = cfg.get("repeat_rate", 0.05)

# VK-коды (US-раскладка). Работают в любой раскладке.
VK_MAP = {
    0x41: "a",   # A
    0x44: "d",   # D
    0x57: "w",   # W
    0x53: "s",   # S
    0x51: "q",   # Q
    0x45: "e",   # E
    0x52: "r",   # R
    0x46: "f",   # F
    0x5A: "z",   # Z
    0x58: "x",   # X
    0x43: "c",   # C
    0x56: "v",   # V
}

modifier_down = False
held_repeat = {}   # kid -> [key, action, last_time]
held_mouse = set() # зажатые кнопки мыши (для drag & drop)

def key_id(key):
    return str(key)

def get_char(key):
    try:
        return key.char.lower() if key.char else None
    except AttributeError:
        return None

def key_names(key):
    """Возможные имена клавиши для поиска в конфиге."""
    names = []
    vk = getattr(key, "vk", None)
    if vk in VK_MAP:
        names.append(VK_MAP[vk])
    ch = get_char(key)
    if ch:
        names.append(ch)
    if hasattr(key, "name"):
        names.append(key.name)
    return names

def find_bind(key):
    for name in key_names(key):
        if name in cfg["binds"]:
            return cfg["binds"][name]
    return None

def do_action(action, press_only=False):
    t = action.get("action")

    if t == "mouse_move":
        x, y = mouse_ctrl.position
        mouse_ctrl.position = (x + action.get("dx", 0), y + action.get("dy", 0))

    elif t == "mouse_click":
        btn = getattr(mouse.Button, action.get("button", "left"))
        mouse_ctrl.click(btn)

    elif t == "mouse_press":
        btn = getattr(mouse.Button, action.get("button", "left"))
        mouse_ctrl.press(btn)
        held_mouse.add(btn)

    elif t == "mouse_release":
        btn = getattr(mouse.Button, action.get("button", "left"))
        if btn in held_mouse:
            mouse_ctrl.release(btn)
            held_mouse.discard(btn)

    elif t == "mouse_scroll":
        mouse_ctrl.scroll(action.get("dx", 0), action.get("dy", 0))

    elif t == "key":
        k = action["key"]
        k_obj = getattr(keyboard.Key, k, None)
        if k_obj is not None:
            kb_ctrl.press(k_obj)
            kb_ctrl.release(k_obj)
        else:
            kb_ctrl.type(k)

    elif t == "run":
        try:
            subprocess.Popen(action["command"], shell=True)
        except Exception as e:
            print(f"[keybi] Ошибка запуска {action['command']}: {e}")

    else:
        print(f"[keybi] Неизвестное действие: {t}")

def on_press(key):
    global modifier_down

    if key == MODIFIER:
        modifier_down = True
        return

    if not modifier_down:
        return

    action = find_bind(key)
    if not action:
        return

    kid = key_id(key)
    if kid in held_repeat:
        return  # уже обрабатывается (защита от автоповтора ОС)

    if action.get("repeat"):
        held_repeat[kid] = [key, action, time.time()]
        do_action(action)
    else:
        do_action(action)
        held_repeat[kid] = [key, action, time.time()]  # не спамим

def on_release(key):
    global modifier_down

    if key == MODIFIER:
        modifier_down = False
        # Отпускаем все зажатые кнопки мыши при отпускании модификатора
        for btn in list(held_mouse):
            mouse_ctrl.release(btn)
            held_mouse.discard(btn)

    # Для drag & drop: если бинд был mouse_press — отпускаем при отпускании клавиши
    action = find_bind(key)
    if action and action.get("action") == "mouse_press":
        btn = getattr(mouse.Button, action.get("button", "left"))
        if btn in held_mouse:
            mouse_ctrl.release(btn)
            held_mouse.discard(btn)

    held_repeat.pop(key_id(key), None)

def repeater():
    while True:
        now = time.time()
        for kid, (key, action, last) in list(held_repeat.items()):
            if action.get("repeat") and modifier_down:
                if now - last > REPEAT_DELAY:
                    do_action(action)
                    held_repeat[kid][2] = now - REPEAT_DELAY + REPEAT_RATE
        time.sleep(0.01)

threading.Thread(target=repeater, daemon=True).start()

if __name__ == "__main__":
    print("Keybi запущен.")
    print(f"Модификатор: {cfg.get('modifier')}")
    print("Бинды:", ", ".join(cfg["binds"].keys()))
    print("Ctrl+C — выход.")
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()
