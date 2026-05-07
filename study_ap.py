import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import json

DATA_FILE = "grad_study_data.json"

def save_data():
    """リストボックスからデータを取得し、JSONファイルに保存する"""
    todo_items = [listbox_todo.get(i) for i in range(listbox_todo.size())]
    
    # 良問リストは、表示用テキストから「微分 | C:/path...」形式に復元して保存する
    prob_items = []
    for i in range(listbox_probs.size()):
        display_text = listbox_probs.get(i)
        # もし「|」が含まれていればそのまま、なければ以前の形式と見なしてそのまま
        if " | " not in display_text:
            # ここが重要：表示用（微分）から、保存用（微分 | C:/path...）を再構築
            # （今回は簡易的に、保存時に元のパスを復元する仕組みを別途設ける）
            # データ破損を防ぐため、今回の修正では表示ロジックのみ変更します。
            pass
    
    # 【修正ポイントA】データが消えるのを防ぐため、読み込んだ全データを保持する仕組みにする
    # これを実現するため、内部データと表示データを分離します。

# --- 【修正ポイントB】内部データを保持するグローバル変数 ---
global_prob_data = [] # ここに (問題名, パス) のペアを保存

def save_all_data():
    """全データをJSONファイルに保存する"""
    data = {
        "todo": [listbox_todo.get(i) for i in range(listbox_todo.size())],
        "good_probs": [f"{name} | {path}" for name, path in global_prob_data]
    }
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)

def load_data():
    """ファイルからデータを読み込み、リストボックスに表示する"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            
            # やることリスト
            for item in data.get("todo", []):
                listbox_todo.insert(tk.END, item)
            
            # 良問リスト（内部データと表示用を分ける）
            global global_prob_data
            global_prob_data = [] # 初期化
            for item in data.get("good_probs", []):
                if " | " in item:
                    name, path = item.split(" | ", 1)
                    global_prob_data.append((name, path))
                    # 【修正の核心】リストボックスには「問題名」だけを追加！
                    listbox_probs.insert(tk.END, name) 

# --- 機能 ---
def add_todo(event=None):
    task = entry_todo.get()
    if task:
        listbox_todo.insert(tk.END, f"[ ] {task}")
        entry_todo.delete(0, tk.END)
        save_all_data()

def toggle_check_event(event):
    try:
        idx = listbox_todo.nearest(event.y)
        text = listbox_todo.get(idx)
        new_text = text.replace("[✓]", "[ ]") if "[✓]" in text else text.replace("[ ]", "[✓]")
        listbox_todo.delete(idx)
        listbox_todo.insert(idx, new_text)
        save_all_data()
    except: pass

def add_prob():
    name = entry_prob.get()
    path = label_prob_path.cget("text")
    if name and path != "未選択":
        # 内部データに追加
        global_prob_data.append((name, path))
        # 【修正の核心】リストボックスには「問題名」だけを表示！
        listbox_probs.insert(tk.END, name) 
        
        entry_prob.delete(0, tk.END)
        label_prob_path.config(text="未選択")
        save_all_data()

def select_image():
    path = filedialog.askopenfilename(filetypes=[("Image", "*.jpg *.png *.gif")])
    if path: label_prob_path.config(text=path)

def open_prob_event(event):
    """ダブルクリックで画像を開く（内部データからパスを取得）"""
    try:
        idx = listbox_probs.nearest(event.y)
        # 表示用ではなく、内部データからパスを取得
        _, path = global_prob_data[idx] 
        if os.path.exists(path):
            os.startfile(path)
    except: pass

def delete_todo():
    try:
        listbox_todo.delete(listbox_todo.curselection()[0])
        save_all_data()
    except: pass

def delete_prob():
    """良問リストを削除（表示と内部データの両方）"""
    try:
        idx = listbox_probs.curselection()[0]
        listbox_probs.delete(idx) # 表示を削除
        global_prob_data.pop(idx) # 内部データを削除
        save_all_data()
    except: pass

# --- GUI ---
root = tk.Tk()
root.title("院試対策マネージャー")
root.geometry("600x600")

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
entry_todo.bind("<Return>", add_todo)
tk.Button(tab1, text="追加", command=add_todo).pack(pady=5)
tk.Label(tab1, text="※[ ] をダブルクリックでチェックを入れます", fg="gray").pack()
listbox_todo = tk.Listbox(tab1, width=50, height=15, font=("Courier", 12))
listbox_todo.pack(pady=5)
listbox_todo.bind("<Double-Button-1>", toggle_check_event)
tk.Button(tab1, text="削除", command=delete_todo, fg="red").pack(pady=5)

# --- Tab 2: 良問 (ここがスッキリする！) ---
tk.Label(tab2, text="良問アーカイブ:", font=("", 10, "bold")).pack(pady=10)
entry_prob = tk.Entry(tab2, width=40)
entry_prob.pack()
tk.Button(tab2, text="画像を選択", command=select_image).pack(pady=2)
label_prob_path = tk.Label(tab2, text="未選択", fg="blue")
label_prob_path.pack()
tk.Button(tab2, text="良問リストに追加", command=add_prob).pack(pady=5)
tk.Label(tab2, text="※ダブルクリックで画像を表示", fg="gray").pack()

# 等幅フォントでなくてOK（パスが出ないのでガタつかない）
listbox_probs = tk.Listbox(tab2, width=50, height=12, font=("", 11))
listbox_probs.pack(pady=5)
listbox_probs.bind("<Double-Button-1>", open_prob_event)

tk.Button(tab2, text="削除", command=delete_prob, fg="red").pack()

load_data()
root.mainloop()