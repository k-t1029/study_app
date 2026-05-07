import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import json
from datetime import datetime

DATA_FILE = "grad_study_data.json"
global_prob_data = []

# --- 機能面 (保存・計算ロジックは維持) ---
def calculate_remaining_days(deadline_str):
    if not deadline_str or deadline_str == "なし": return None
    try:
        today = datetime.now().date()
        deadline_date = datetime.strptime(f"{today.year}{deadline_str}", "%Y%m%d").date()
        return (deadline_date - today).days
    except: return None

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
            delta = (exam_date.date() - datetime.now().date()).days
            label_countdown.config(text=f"✨ 試験まであと {delta} 日 ✨" if delta >= 0 else "")
        except: pass

def set_exam_date():
    date_val = entry_exam.get()
    try:
        formatted_date = f"{date_val[:4]}-{date_val[4:6]}-{date_val[6:8]}"
        datetime.strptime(formatted_date, "%Y-%m-%d")
        label_exam_raw.config(text=formatted_date)
        entry_exam.delete(0, tk.END)
        update_countdown(); save_all_data()
        messagebox.showinfo("設定完了", "試験日を登録しました！応援しています！")
    except:
        messagebox.showerror("エラー", "日付は「20260530」のように入力してね")

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            for item in data.get("todo", []): listbox_todo.insert(tk.END, item)
            global global_prob_data
            for item in data.get("good_probs", []):
                if " | " in item:
                    name, path = item.split(" | ", 1)
                    global_prob_data.append((name, path)); listbox_probs.insert(tk.END, name)
            label_exam_raw.config(text=data.get("exam_date", "未設定"))
            update_countdown()

def add_todo(event=None):
    task = entry_todo.get()
    deadline = entry_todo_date.get()
    if task:
        days_left = calculate_remaining_days(deadline)
        f_date = f"{deadline[:2]}/{deadline[2:4]}" if deadline else "なし"
        status = f"残り{days_left}日" if days_left is not None else ""
        if days_left == 0: status = "今日！"
        elif days_left is not None and days_left < 0: status = "期限切れ"
        
        display_text = f"[ ] {task} (期限:{f_date} {status})"
        listbox_todo.insert(tk.END, display_text)
        entry_todo.delete(0, tk.END); entry_todo_date.delete(0, tk.END)
        save_all_data()

def toggle_check_event(event):
    try:
        idx = listbox_todo.nearest(event.y)
        text = listbox_todo.get(idx)
        new_text = text.replace("[✓]", "[ ]") if "[✓]" in text else text.replace("[ ]", "[✓]")
        listbox_todo.delete(idx); listbox_todo.insert(idx, new_text); save_all_data()
    except: pass

def add_prob():
    name = entry_prob.get()
    path = label_prob_path.cget("text")
    if name and path != "未設定":
        global_prob_data.append((name, path)); listbox_probs.insert(tk.END, name)
        entry_prob.delete(0, tk.END); label_prob_path.config(text="未設定"); save_all_data()

def select_image():
    path = filedialog.askopenfilename(filetypes=[("Image", "*.jpg *.png *.gif")])
    if path: label_prob_path.config(text=path)

def open_prob_event(event):
    try:
        idx = listbox_probs.nearest(event.y)
        _, path = global_prob_data[idx]
        if os.path.exists(path): os.startfile(path)
    except: messagebox.showerror("エラー", "画像ファイルが見つかりません")

def delete_item(lb, is_prob=False):
    try:
        idx = lb.curselection()[0]
        if messagebox.askyesno("確認", "この項目を削除してもいいですか？"):
            lb.delete(idx)
            if is_prob: global_prob_data.pop(idx)
            save_all_data()
    except: pass

# --- UI リニューアル ---
root = tk.Tk()
root.title("🌸 院試対策マネージャー 🌸")
root.geometry("650x780")
root.configure(bg="#f0f4f8") # 全体の背景を優しいグレーブルーに

# カスタムスタイル
style = ttk.Style()
style.theme_use('clam')
style.configure("TNotebook", background="#f0f4f8", borderwidth=0)
style.configure("TNotebook.Tab", background="#d1d9e6", padding=[10, 5], font=("", 10))
style.map("TNotebook.Tab", background=[("selected", "#ffffff")])

# カウントダウン
label_countdown = tk.Label(root, text="", font=("MS Gothic", 16, "bold"), fg="#e63946", bg="#f0f4f8")
label_countdown.pack(pady=10)
label_exam_raw = tk.Label(root, text="未設定")

notebook = ttk.Notebook(root)
tab1 = ttk.Frame(notebook); tab2 = ttk.Frame(notebook); tab3 = ttk.Frame(notebook)
notebook.add(tab1, text="  やること  "); notebook.add(tab2, text="  良問集  "); notebook.add(tab3, text="  設定  ")
notebook.pack(expand=True, fill="both", padx=10, pady=10)

# --- Tab 1: やること ---
frame_input1 = tk.Frame(tab1, pady=15); frame_input1.pack()
tk.Label(frame_input1, text="なにをする？").grid(row=0, column=0, padx=5)
entry_todo = tk.Entry(frame_input1, width=25); entry_todo.grid(row=0, column=1, padx=5)
tk.Label(frame_input1, text="期限(0530)").grid(row=1, column=0, padx=5, pady=5)
entry_todo_date = tk.Entry(frame_input1, width=15); entry_todo_date.grid(row=1, column=1, padx=5, sticky="w")

tk.Button(tab1, text="リストに追加 ➕", command=add_todo, bg="#a8dadc", relief="flat").pack(pady=5)
listbox_todo = tk.Listbox(tab1, width=60, height=18, font=("Courier", 11), borderwidth=0, highlightthickness=1, highlightcolor="#a8dadc")
listbox_todo.pack(pady=10, padx=10); listbox_todo.bind("<Double-Button-1>", toggle_check_event)
tk.Button(tab1, text="削除する 🗑", command=lambda: delete_item(listbox_todo), fg="#457b9d", relief="flat").pack()

# --- Tab 2: 良問集 ---
frame_input2 = tk.Frame(tab2, pady=15); frame_input2.pack()
tk.Label(frame_input2, text="問題の名前:").pack()
entry_prob = tk.Entry(frame_input2, width=35); entry_prob.pack(pady=5)
tk.Button(frame_input2, text="📸 画像を選ぶ", command=select_image, bg="#f1faee").pack()
label_prob_path = tk.Label(frame_input2, text="未設定", fg="#457b9d", font=("", 8)); label_prob_path.pack()

tk.Button(tab2, text="良問集に追加 ✨", command=add_prob, bg="#a8dadc", relief="flat").pack(pady=10)
listbox_probs = tk.Listbox(tab2, width=50, height=14, font=("", 11), borderwidth=0)
listbox_probs.pack(pady=5); listbox_probs.bind("<Double-Button-1>", open_prob_event)
tk.Button(tab2, text="削除する 🗑", command=lambda: delete_item(listbox_probs, True), fg="#457b9d", relief="flat").pack()

# --- Tab 3: 設定 ---
tk.Label(tab3, text="試験日はいつ？", font=("", 12)).pack(pady=30)
entry_exam = tk.Entry(tab3, width=20, font=("", 12), justify="center"); entry_exam.pack()
tk.Label(tab3, text="(例: 20260825)", fg="gray").pack(pady=5)
tk.Button(tab3, text="試験日をセット 🏁", command=set_exam_date, bg="#e63946", fg="white", font=("", 10, "bold")).pack(pady=20)

load_data()
root.mainloop()