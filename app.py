import customtkinter as ctk
import tkinter as tk  
from tkinter import filedialog, messagebox
import tkinter.font as tkFont
import hashlib
import os
import json

HASH_FILE = 'hash_store.json'

def calculate_sha256(filepath):
    sha256 = hashlib.sha256()
    try:
        with open(filepath, 'rb') as f:
            while chunk := f.read(4096):
                sha256.update(chunk)
        return sha256.hexdigest()
    except FileNotFoundError:
        return None

def scan_directory(folder_path):
    hash_data = {}
    for root, dirs, files in os.walk(folder_path):
        for filename in files:
            filepath = os.path.join(root, filename)
            hash_value = calculate_sha256(filepath)
            if hash_value:
                hash_data[filepath] = hash_value
    return hash_data

def save_hashes(hash_data):
    with open(HASH_FILE, 'w') as f:
        json.dump(hash_data, f, indent=4)

def load_hashes():
    if not os.path.exists(HASH_FILE):
        return {}
    with open(HASH_FILE, 'r') as f:
        return json.load(f)

def check_integrity(current_hashes, old_hashes):
    results = []
    for filepath in old_hashes:
        if filepath not in current_hashes:
            results.append(f"[⚠️ DELETED] {filepath}")
        elif old_hashes[filepath] != current_hashes[filepath]:
            results.append(f"[❌ MODIFIED] {filepath}")
        else:
            results.append(f"[✅ OK     ] {filepath}")

    for filepath in current_hashes:
        if filepath not in old_hashes:
            results.append(f"[🆕 NEW     ] {filepath}")
    return results

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.geometry("750x550")
app.title("File Integrity Checker")

folder_path_var = ctk.StringVar()

def browse_folder():
    folder = filedialog.askdirectory()
    folder_path_var.set(folder)

def init_hash():
    folder = folder_path_var.get()
    if folder:
        hashes = scan_directory(folder)
        save_hashes(hashes)
        output_box.insert("end", f"✅ Hashes saved successfully for:\n{folder}\n\n")
        messagebox.showinfo("Done", "✅ Hash snapshot saved successfully!")

def check_hash():
    folder = folder_path_var.get()
    if folder:
        current_hashes = scan_directory(folder)
        saved_hashes = load_hashes()

        if not saved_hashes:
            messagebox.showwarning("No Data", "⚠️ No saved hashes found. Please run 'Save Hash Snapshot' first.")
            return

        results = check_integrity(current_hashes, saved_hashes)
        output_box.delete("1.0", "end")  
        output_box.insert("end", f"🔍 Scan Results for:\n{folder}\n\n")

        for line in results:
            if "[⚠️ DELETED]" in line:
                output_box.insert("end", line + "\n", "deleted")
            elif "[❌ MODIFIED]" in line:
                output_box.insert("end", line + "\n", "modified")
            elif "[🆕 NEW]" in line:
                output_box.insert("end", line + "\n", "new")
            elif "[✅ OK     ]" in line:
                output_box.insert("end", line + "\n", "ok")
            else:
                output_box.insert("end", line + "\n")

frame = ctk.CTkFrame(app)
frame.pack(pady=20)

folder_entry = ctk.CTkEntry(frame, textvariable=folder_path_var, width=450, placeholder_text="Select any folder to scan...")
folder_entry.pack(side="left", padx=10)

browse_btn = ctk.CTkButton(frame, text="Browse", command=browse_folder)
browse_btn.pack(side="left")

init_btn = ctk.CTkButton(app, text="📥 Save Hash Snapshot", command=init_hash)
init_btn.pack(pady=10)

check_btn = ctk.CTkButton(app, text="🔎 Check Integrity", command=check_hash)
check_btn.pack()

output_box = tk.Text(
    app,
    width=100,
    height=34,
    bg="#2c2f33",
    fg="white",
    insertbackground="white",
    borderwidth=0,
    highlightthickness=0,
    wrap="word"
)
output_box.pack(pady=20)

font_style = tkFont.Font(family="Consolas", size=11)
output_box.configure(font=font_style)

output_box.tag_configure("deleted", foreground="red")
output_box.tag_configure("modified", foreground="orange")
output_box.tag_configure("new", foreground="green")
output_box.tag_configure("ok", foreground="white")

app.mainloop()
