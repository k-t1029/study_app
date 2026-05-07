import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import json
from datetime import datetime

DATA_FILE = "grad_study_data.json"

def save_all_data():
    """全データ（試験日含む）を保存する"""
    data = {
        "todo": [listbox_todo.get(i) for i in range(listbox_todo.size())],
        "good_probs": [f"{name} | {path}" for name, path in global_prob_data],
        "exam_date": label_exam_raw.cget("text") # 試験日を保存
    }
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)

def update_countdown():
    """試験日までの残り日数を計算して表示を更新する"""
    exam_date_str = label_exam_raw.cget("text")
    if exam_date_str and exam_date_str != "未設定":
        try:
            exam_date = datetime.strptime(exam_date_str, "%Y-%m-%d")
            today = datetime.now()
            # 時間を切り捨てて日付のみで計算
            delta = (exam_date.date() - today.date()).days
            
            if delta >= 0:
                label_countdown.config(text=f"試験まで残り {delta} 日")
            else:
                # 試験日が過ぎたら表示を消し、設定もリセット
                label_countdown.config(text="")
                label_exam_raw.config(text="未設定")
                save_all_data()
        except:
            label_countdown.config(text="")
    else:
        label_countdown.config(text="")

def set_exam_date():
    """入力された日付を試験日として設定する"""
    date_val = entry_exam.get() # 例: 20260530
    try:
        # 入力形式を整える (例: 20260530 -> 2026-05-30)
        formatted_date = f"{date_val[:4]}-{date_val[4:6]}-{date_val[6:8]}"
        datetime.strptime(formatted_date, "%Y-%m-%d") # 有効な日付かチェック
        label_exam_raw.config(text=formatted_date)
        entry_exam.delete(0, tk.END)
        update_countdown()
        save_all_data()
    except:
        messagebox.showerror("エラー", "日付は「20260530」のように8桁で入力してください")

# --- 既存の読み込み処理を拡張 ---
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            # 既存のリスト読み込み...
            for item in data.get("todo", []): listbox_todo.insert(tk.END, item)
            global global_prob_data
            global_prob_data = []
            for item in data.get("good_probs", []):
                if " | " in item:
                    name, path = item.split(" | ", 1)
                    global_prob_data.append((name, path))
                    listbox_probs.insert(tk.END, name)
            # 試験日の読み込み
            saved_date = data.get("exam_date", "未設定")
            label_exam_raw.config(text=saved_date)
            update_countdown()

# --- (他の既存機能: add_todo, toggle_check, select_image 等は維持) ---
global_prob_data = []

# --- GUI構築 ---
root = tk.Tk()
root.title("院試対策マネージャー")
root.geometry("600x650")

# 【新規】左上のカウントダウン表示 (赤色)
label_countdown = tk.Label(root, text="", font=("MS Gothic", 14, "bold"), fg="red")
label_countdown.place(x=10, y=5) # placeを使って左上に固定

# 試験日を保持しておく隠しラベル
label_exam_raw = tk.Label(root, text="未設定") 

notebook = ttk.Notebook(root)
tab1 = ttk.Frame(notebook)
tab2 = ttk.Frame(notebook)
tab3 = ttk.Frame(notebook) # 試験設定用タブ
notebook.add(tab1, text=" やることリスト ")
notebook.add(tab2, text=" 良問リスト ")
notebook.add(tab3, text=" 試験日設定 ")
notebook.pack(expand=True, fill="both", pady=(40, 0)) # カウントダウンの場所を空ける

# --- Tab 3: 試験日設定 (新規) ---
tk.Label(tab3, text="試験日を入力してください:", font=("", 10, "bold")).pack(pady=20)
tk.Label(tab3, text="(例: 20260530)", fg="gray").pack()
entry_exam = tk.Entry(tab3, width=20, font=("", 12))
entry_exam.pack(pady=10)
tk.Button(tab3, text="試験日を設定する", command=set_exam_date).pack(pady=10)

# --- Tab 1 & 2 の内容は以前のコードと同様 ---
# (リストボックスや追加ボタンなど)
# ... [中略: 以前のタブ1, 2のUIコード] ...

# 便宜上、簡単な削除・追加関数のみ再定義
def add_todo(event=None):
    task = entry_todo.get(); 
    if task: listbox_todo.insert(tk.END, f"[ ] {task}"); entry_todo.delete(0, tk.END); save_all_data()

# --- Tab 1 UI ---
tk.Label(tab1, text="試験までにやるべきこと:").pack(pady=10)
entry_todo = tk.Entry(tab1, width=40); entry_todo.pack()
tk.Button(tab1, text="追加", command=add_todo).pack(pady=5)
listbox_todo = tk.Listbox(tab1, width=50, height=15); listbox_todo.pack()

load_data()
root.mainloop()