import tkinter as tk
from tkinter import filedialog, messagebox
import os

def add_item():
    task = entry_task.get()
    img_path = label_path.cget("text")
    if task:
        # リストに「タスク内容 | 画像パス」の形式で追加
        listbox.insert(tk.END, f"{task} | {img_path}")
        entry_task.delete(0, tk.END)
        label_path.config(text="画像未選択")
    else:
        messagebox.showwarning("警告", "タスクを入力してください")

def select_image():
    # 画像ファイルを選択する
    file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.png *.gif")])
    if file_path:
        label_path.config(text=file_path)

def open_image():
    # 選択した項目の画像を表示する
    try:
        selected = listbox.get(listbox.curselection())
        path = selected.split(" | ")[1]
        if os.path.exists(path):
            os.startfile(path) # Windowsで画像を開く
        else:
            messagebox.showerror("エラー", "画像が見つかりません")
    except:
        messagebox.showwarning("警告", "リストから項目を選択してください")

root = tk.Tk()
root.title("院試対策 共有ToDo & 問題集")
root.geometry("500x400")

# 入力部
tk.Label(root, text="やるべきこと・共有したい問題名:").pack()
entry_task = tk.Entry(root, width=50)
entry_task.pack(pady=5)

# 画像選択部
tk.Button(root, text="問題を写真で追加(ファイル選択)", command=select_image).pack()
label_path = tk.Label(root, text="画像未選択", fg="blue")
label_path.pack()

tk.Button(root, text="リストに追加", command=add_item).pack(pady=10)

# リスト表示部
listbox = tk.Listbox(root, width=60, height=10)
listbox.pack(padx=20)

tk.Button(root, text="選択した問題の写真を見る", command=open_image).pack(pady=10)

root.mainloop()