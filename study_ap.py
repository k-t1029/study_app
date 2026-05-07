import tkinter as tk
from tkinter import filedialog, messagebox
import os
import json # データを保存するためのライブラリ

# 保存先ファイル名
DATA_FILE = "study_data.json"

def save_data():
    """リストボックスの内容をファイルに保存する"""
    items = listbox.get(0, tk.END)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False)

def load_data():
    """ファイルからデータを読み込んでリストボックスに表示する"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            items = json.load(f)
            for item in items:
                listbox.insert(tk.END, item)

def add_item():
    task = entry_task.get()
    img_path = label_path.cget("text")
    if task:
        listbox.insert(tk.END, f"{task} | {img_path}")
        entry_task.delete(0, tk.END)
        label_path.config(text="画像未選択")
        save_data() # 追加したら保存
    else:
        messagebox.showwarning("警告", "タスクを入力してください")

def delete_item():
    try:
        selected_index = listbox.curselection()[0]
        listbox.delete(selected_index)
        save_data() # 削除したら保存
    except IndexError:
        messagebox.showwarning("警告", "削除する項目を選択してください")

def select_image():
    file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.png *.gif")])
    if file_path:
        label_path.config(text=file_path)

def open_image():
    try:
        selected = listbox.get(listbox.curselection())
        path = selected.split(" | ")[1]
        if os.path.exists(path):
            os.startfile(path)
        else:
            messagebox.showerror("エラー", "画像が見つかりません")
    except:
        messagebox.showwarning("警告", "リストから項目を選択してください")

root = tk.Tk()
root.title("院試対策 共有ToDo & 問題集")
root.geometry("500x450")

tk.Label(root, text="やるべきこと・共有したい問題名:").pack()
entry_task = tk.Entry(root, width=50)
entry_task.pack(pady=5)

tk.Button(root, text="問題を写真で追加(ファイル選択)", command=select_image).pack()
label_path = tk.Label(root, text="画像未選択", fg="blue")
label_path.pack()

tk.Button(root, text="リストに追加", command=add_item).pack(pady=10)

listbox = tk.Listbox(root, width=60, height=10)
listbox.pack(padx=20)

tk.Button(root, text="選択した問題の写真を見る", command=open_image).pack(pady=5)
tk.Button(root, text="選択した項目を削除する", command=delete_item, fg="red").pack(pady=5)

# アプリ起動時にデータを読み込む
load_data()

root.mainloop()