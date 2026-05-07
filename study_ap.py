import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import json

DATA_FILE = "grad_study_data.json"

def save_data():
    data = {
        "todo": [listbox_todo.get(i) for i in range(listbox_todo.size())],
        "good_probs": [listbox_probs.get(i) for i in range(listbox_probs.size())]
    }
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            for item in data.get("todo", []):
                listbox_todo.insert(tk.END, item)
            for item in data.get("good_probs", []):
                listbox_probs.insert(tk.END, item)

def add_todo():
    task = entry_todo.get()
    if task:
        listbox_todo.insert(tk.END, f"□ {task}")
        entry_todo.delete(0, tk.END)
        save_data()

# --- 改良したクリック切替機能 ---
def on_todo_click(event):
    try:
        # クリックされた項目のインデックスを取得
        idx = listbox_todo.curselection()[0]
        text = listbox_todo.get(idx)
        
        # チェック状態を反転
        if "□" in text:
            new_text = text.replace("□", "■")
        else:
            new_text = text.replace("■", "□")
            
        listbox_todo.delete(idx)
        listbox_todo.insert(idx, new_text)
        
        # 選択状態を解除（連続クリックしやすくするため）
        listbox_todo.selection_clear(idx)
        save_data()
    except:
        pass
# ------------------------------

def add_prob():
    name = entry_prob.get()
    path = label_prob_path.cget("text")
    if name and path != "未選択":
        listbox_probs.insert(tk.END, f"{name} | {path}")
        entry_prob.delete(0, tk.END)
        label_prob_path.config(text="未選択")
        save_data()

def select_image():
    path = filedialog.askopenfilename(filetypes=[("Image", "*.jpg *.png *.gif")])
    if path: label_prob_path.config(text=path)

def open_prob():
    try:
        path = listbox_probs.get(listbox_probs.curselection()).split(" | ")[1]
        os.startfile(path)
    except: pass

def delete_selected(lb):
    try:
        lb.delete(lb.curselection()[0])
        save_data()
    except: pass

root = tk.Tk()
root.title("院試対策マネージャー")
root.geometry("600x650")

notebook = ttk.Notebook(root)
tab1 = ttk.Frame(notebook)
tab2 = ttk.Frame(notebook)
notebook.add(tab1, text=" やることリスト ")
notebook.add(tab2, text=" 良問リスト ")
notebook.pack(expand=True, fill="both")

# --- Tab 1: やること ---
tk.Label(tab1, text="試験までにやるべきこと:", font=("", 10, "bold")).pack(pady=10)
entry_todo = tk.Entry(tab1, width=40)
entry_todo.pack()
tk.Button(tab1, text="追加", command=add_todo).pack(pady=5)

listbox_todo = tk.Listbox(tab1, width=50, height=15, font=("", 12))
listbox_todo.pack(pady=5)

# クリックイベントを紐付け（改良ポイント）
listbox_todo.bind('<<ListboxSelect>>', on_todo_click)

tk.Button(tab1, text="削除", command=lambda: delete_selected(listbox_todo), fg="red").pack(pady=10)

# --- Tab 2: 良問 ---
# (Tab 2 の内容は前回と同様)
tk.Label(tab2, text="良問アーカイブ (画像管理):", font=("", 10, "bold")).pack(pady=10)
entry_prob = tk.Entry(tab2, width=40)
entry_prob.pack()
tk.Button(tab2, text="画像を選択", command=select_image).pack(pady=2)
label_prob_path = tk.Label(tab2, text="未選択", fg="blue")
label_prob_path.pack()
tk.Button(tab2, text="良問リストに追加", command=add_prob).pack(pady=5)
listbox_probs = tk.Listbox(tab2, width=50, height=12, font=("", 12))
listbox_probs.pack(pady=5)
tk.Button(tab2, text="選択した問題を開く", command=open_prob).pack(pady=2)
tk.Button(tab2, text="削除", command=lambda: delete_selected(listbox_probs), fg="red").pack()

load_data()
root.mainloop()