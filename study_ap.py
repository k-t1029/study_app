import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import json
from datetime import datetime

DATA_FILE = "grad_study_data.json"
global_prob_data = []

# --- 機能 ---
def calculate_remaining_days(deadline_str):
    """期限(MMDD)から残り日数を計算するヘルパー関数"""
    if not deadline_str or deadline_str == "なし":
        return None
    try:
        today = datetime.now().date()
        # 今年の日付として解釈
        year = today.year
        deadline_date = datetime.strptime(f"{year}{deadline_str}", "%Y%m%d").date()
        
        # もし期限が今日より前なら、来年の日付として扱う（例: 1月に12月の目標を立てる場合などへの配慮）
        # ただし今回はシンプルに今年の日付で計算します
        delta = (deadline_date - today).days
        return delta
    except:
        return None

def save_all_data():
    data = {
        "todo": [listbox_todo.get(i) for i in range(listbox_todo.size())],
        "good_probs": [f"{name} | {path}" for name, path in global_prob_data],
        "exam_date": label_exam_raw.cget("text")
    }
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)

def update_countdown():
    exam_date_str = label_exam_raw.cget("text")
    if exam_date_str and exam_date_str != "未設定":
        try:
            exam_date = datetime.strptime(exam_date_str, "%Y-%m-%d")
            today = datetime.now()
            delta = (exam_date.date() - today.date()).days
            label_countdown.config(text=f"試験まで残り {delta} 日" if delta >= 0 else "")
        except: pass
    else:
        label_countdown.config(text="")

def set_exam_date():
    date_val = entry_exam.get()
    try:
        formatted_date = f"{date_val[:4]}-{date_val[4:6]}-{date_val[6:8]}"
        datetime.strptime(formatted_date, "%Y-%m-%d")
        label_exam_raw.config(text=formatted_date)
        entry_exam.delete(0, tk.END)
        update_countdown()
        save_all_data()
    except:
        messagebox.showerror("エラー", "日付は「20260530」のように8桁で入力してください")

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            # やることリストの読み込み（残り日数を再計算して表示）
            for item in data.get("todo", []):
                # 保存されているテキストからタスク名と期限情報を抽出して再構築
                # シンプルにそのまま表示しても良いですが、起動時に日数を更新するのが理想です
                listbox_todo.insert(tk.END, item)
            
            global global_prob_data
            for item in data.get("good_probs", []):
                if " | " in item:
                    name, path = item.split(" | ", 1)
                    global_prob_data.append((name, path))
                    listbox_probs.insert(tk.END, name)
            saved_date = data.get("exam_date", "未設定")
            label_exam_raw.config(text=saved_date)
            update_countdown()

def add_todo(event=None):
    task = entry_todo.get()
    deadline = entry_todo_date.get()
    
    if task:
        if deadline:
            days_left = calculate_remaining_days(deadline)
            formatted_deadline = f"{deadline[:2]}/{deadline[2:4]}"
            if days_left is not None:
                if days_left > 0:
                    status = f"残り {days_left}日"
                elif days_left == 0:
                    status = "今日が期限！"
                else:
                    status = "期限切れ"
                display_text = f"[ ] {task} (期限: {formatted_deadline} {status})"
            else:
                display_text = f"[ ] {task} (期限: {formatted_deadline})"
        else:
            display_text = f"[ ] {task} (期限: なし)"
            
        listbox_todo.insert(tk.END, display_text)
        entry_todo.delete(0, tk.END)
        entry_todo_date.delete(0, tk.END)
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
    if name and path != "未設定":
        global_prob_data.append((name, path))
        listbox_probs.insert(tk.END, name)
        entry_prob.delete(0, tk.END)
        label_prob_path.config(text="未設定")
        save_all_data()

def select_image():
    path = filedialog.askopenfilename(filetypes=[("Image", "*.jpg *.png *.gif")])
    if path: label_prob_path.config(text=path)

def open_prob_event(event):
    try:
        idx = listbox_probs.nearest(event.y)
        _, path = global_prob_data[idx]
        if os.path.exists(path): os.startfile(path)
    except: pass

def delete_item(lb, is_prob=False):
    try:
        idx = lb.curselection()[0]
        lb.delete(idx)
        if is_prob: global_prob_data.pop(idx)
        save_all_data()
    except: pass

# --- GUI ---
root = tk.Tk()
root.title("院試対策マネージャー")
root.geometry("650x750")

label_countdown = tk.Label(root, text="", font=("MS Gothic", 14, "bold"), fg="red")
label_countdown.place(x=10, y=5)
label_exam_raw = tk.Label(root, text="未設定")

notebook = ttk.Notebook(root)
tab1 = ttk.Frame(notebook); tab2 = ttk.Frame(notebook); tab3 = ttk.Frame(notebook)
notebook.add(tab1, text=" やることリスト "); notebook.add(tab2, text=" 良問リスト "); notebook.add(tab3, text=" 試験日設定 ")
notebook.pack(expand=True, fill="both", pady=(40, 0))

# --- Tab 1: やること (残り日数表示付き) ---
tk.Label(tab1, text="内容:").pack(pady=(10, 0))
entry_todo = tk.Entry(tab1, width=40); entry_todo.pack()

tk.Label(tab1, text="期限 (例: 0530 / 空欄で期限なし):", fg="gray").pack(pady=(10, 0))
entry_todo_date = tk.Entry(tab1, width=20); entry_todo_date.pack()

entry_todo.bind("<Return>", add_todo)
entry_todo_date.bind("<Return>", add_todo)

tk.Button(tab1, text="追加", command=add_todo).pack(pady=10)

listbox_todo = tk.Listbox(tab1, width=65, height=18, font=("Courier", 11))
listbox_todo.pack(pady=5); listbox_todo.bind("<Double-Button-1>", toggle_check_event)
tk.Button(tab1, text="削除", command=lambda: delete_item(listbox_todo), fg="red").pack()

# --- Tab 2 & 3 は維持 ---
tk.Label(tab2, text="良問アーカイブ:").pack(pady=5)
entry_prob = tk.Entry(tab2, width=40); entry_prob.pack()
tk.Button(tab2, text="画像を選択", command=select_image).pack()
label_prob_path = tk.Label(tab2, text="未設定", fg="blue"); label_prob_path.pack()
tk.Button(tab2, text="追加", command=add_prob).pack(pady=5)
listbox_probs = tk.Listbox(tab2, width=50, height=12, font=("", 11))
listbox_probs.pack(pady=5); listbox_probs.bind("<Double-Button-1>", open_prob_event)
tk.Button(tab2, text="削除", command=lambda: delete_item(listbox_probs, True), fg="red").pack()

tk.Label(tab3, text="試験日を入力 (例: 20260530):").pack(pady=20)
entry_exam = tk.Entry(tab3, width=20, font=("", 12)); entry_exam.pack(pady=10)
tk.Button(tab3, text="設定する", command=set_exam_date).pack()

load_data()
root.mainloop()