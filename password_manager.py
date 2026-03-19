import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import random
import string
import base64
from datetime import datetime

DATA_FILE = "passwords.json"
MASTER_PASSWORD = "k2003"


# ---------------- ENCODE / DECODE ----------------
def encode_password(password):
    return base64.b64encode(password.encode()).decode()


def decode_password(encoded_password):
    return base64.b64decode(encoded_password.encode()).decode()


# ---------------- DATA HANDLING ----------------
def load_data():
    try:
        with open(DATA_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        return {}
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load data.\n{e}")
        return {}


def save_data_to_file(data):
    try:
        with open(DATA_FILE, "w") as file:
            json.dump(data, file, indent=4)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save data.\n{e}")


# ---------------- UI HELPERS ----------------
def set_status(message):
    status_label.config(text=message)


def add_hover_effect(button, normal_color, hover_color):
    button.bind("<Enter>", lambda e: button.config(bg=hover_color))
    button.bind("<Leave>", lambda e: button.config(bg=normal_color))


def refresh_website_dropdown():
    data = load_data()
    website_list = sorted(list(data.keys()))
    website_dropdown["values"] = website_list


# ---------------- PASSWORD STRENGTH ----------------
def check_password_strength(password):
    score = 0

    if len(password) >= 8:
        score += 1
    if len(password) >= 12:
        score += 1
    if any(ch.islower() for ch in password):
        score += 1
    if any(ch.isupper() for ch in password):
        score += 1
    if any(ch.isdigit() for ch in password):
        score += 1
    if any(ch in string.punctuation for ch in password):
        score += 1

    if score <= 2:
        return "Weak"
    elif score <= 4:
        return "Medium"
    else:
        return "Strong"


def update_strength_label(event=None):
    password = password_entry.get().strip()

    if password == "":
        strength_label.config(text="Strength: -")
        return

    strength = check_password_strength(password)
    strength_label.config(text=f"Strength: {strength}")


# ---------------- PASSWORD GENERATOR ----------------
def generate_password():
    try:
        chars = string.ascii_letters + string.digits + string.punctuation
        password = "".join(random.choice(chars) for _ in range(14))
        password_entry.delete(0, tk.END)
        password_entry.insert(0, password)
        update_strength_label()
        set_status("Strong password generated.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to generate password.\n{e}")


# ---------------- MAIN FEATURES ----------------
def clear_fields():
    website_var.set("")
    username_entry.delete(0, tk.END)
    password_entry.delete(0, tk.END)
    strength_label.config(text="Strength: -")
    info_label.config(text="Created: -    |    Updated: -")
    set_status("Fields cleared.")


def save_password():
    website = website_var.get().strip()
    username = username_entry.get().strip()
    password = password_entry.get().strip()

    if website == "" or username == "" or password == "":
        messagebox.showwarning("Input Error", "All fields are required.")
        return

    data = load_data()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if website in data:
        created_at = data[website].get("created_at", now)
    else:
        created_at = now

    data[website] = {
        "username": username,
        "password": encode_password(password),
        "created_at": created_at,
        "updated_at": now
    }

    save_data_to_file(data)
    refresh_website_dropdown()
    update_strength_label()
    info_label.config(text=f"Created: {created_at}    |    Updated: {now}")
    set_status(f"Credentials saved for {website}.")
    messagebox.showinfo("Success", "Credentials saved successfully.")


def search_password():
    website = website_var.get().strip()

    if website == "":
        messagebox.showwarning("Input Error", "Enter or select website/app name.")
        return

    data = load_data()

    if website in data:
        username = data[website]["username"]
        password = decode_password(data[website]["password"])
        created_at = data[website].get("created_at", "-")
        updated_at = data[website].get("updated_at", "-")

        username_entry.delete(0, tk.END)
        username_entry.insert(0, username)

        password_entry.delete(0, tk.END)
        password_entry.insert(0, password)

        update_strength_label()
        info_label.config(text=f"Created: {created_at}    |    Updated: {updated_at}")

        set_status(f"Credentials loaded for {website}.")
        messagebox.showinfo("Found", "Credentials found and loaded.")
    else:
        messagebox.showwarning("Not Found", "No credentials found for this website.")
        set_status("Search failed. Website not found.")


def autofill_fields(event=None):
    website = website_var.get().strip()
    data = load_data()

    if website in data:
        username = data[website]["username"]
        password = decode_password(data[website]["password"])
        created_at = data[website].get("created_at", "-")
        updated_at = data[website].get("updated_at", "-")

        username_entry.delete(0, tk.END)
        username_entry.insert(0, username)

        password_entry.delete(0, tk.END)
        password_entry.insert(0, password)

        update_strength_label()
        info_label.config(text=f"Created: {created_at}    |    Updated: {updated_at}")
        set_status(f"Autofilled credentials for {website}.")


def update_password():
    website = website_var.get().strip()
    username = username_entry.get().strip()
    password = password_entry.get().strip()

    if website == "" or username == "" or password == "":
        messagebox.showwarning("Input Error", "All fields are required to update.")
        return

    data = load_data()

    if website in data:
        created_at = data[website].get("created_at", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        data[website] = {
            "username": username,
            "password": encode_password(password),
            "created_at": created_at,
            "updated_at": now
        }

        save_data_to_file(data)
        update_strength_label()
        info_label.config(text=f"Created: {created_at}    |    Updated: {now}")
        set_status(f"Credentials updated for {website}.")
        messagebox.showinfo("Updated", "Credentials updated successfully.")
    else:
        messagebox.showwarning("Not Found", "Website not found. Use Save to add new credentials.")


def delete_password():
    website = website_var.get().strip()

    if website == "":
        messagebox.showwarning("Input Error", "Enter or select website/app name to delete.")
        return

    data = load_data()

    if website in data:
        confirm = messagebox.askyesno("Confirm Delete", f"Delete credentials for {website}?")
        if confirm:
            del data[website]
            save_data_to_file(data)
            refresh_website_dropdown()
            clear_fields()
            set_status(f"Credentials deleted for {website}.")
            messagebox.showinfo("Deleted", "Credentials deleted successfully.")
    else:
        messagebox.showwarning("Not Found", "No credentials found for this website.")


def copy_password():
    password = password_entry.get().strip()

    if password == "":
        messagebox.showwarning("Copy Error", "No password to copy.")
        return

    root.clipboard_clear()
    root.clipboard_append(password)
    root.update()
    set_status("Password copied to clipboard.")
    messagebox.showinfo("Copied", "Password copied to clipboard.")


def toggle_password():
    if password_entry.cget("show") == "*":
        password_entry.config(show="")
        toggle_btn.config(text="🙈 Hide")
        set_status("Password visible.")
    else:
        password_entry.config(show="*")
        toggle_btn.config(text="👁 Show")
        set_status("Password hidden.")


# ---------------- BACKUP FEATURES ----------------
def export_backup():
    try:
        data = load_data()

        if not data:
            messagebox.showwarning("No Data", "No credentials available to export.")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json")],
            title="Export Backup"
        )

        if not file_path:
            return

        with open(file_path, "w") as file:
            json.dump(data, file, indent=4)

        set_status("Backup exported successfully.")
        messagebox.showinfo("Export Success", "Backup exported successfully.")
    except Exception as e:
        messagebox.showerror("Export Error", f"Failed to export backup.\n{e}")


def import_backup():
    try:
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON Files", "*.json")],
            title="Import Backup"
        )

        if not file_path:
            return

        with open(file_path, "r") as file:
            imported_data = json.load(file)

        if not isinstance(imported_data, dict):
            messagebox.showerror("Import Error", "Invalid backup format.")
            return

        current_data = load_data()
        current_data.update(imported_data)
        save_data_to_file(current_data)
        refresh_website_dropdown()

        set_status("Backup imported successfully.")
        messagebox.showinfo("Import Success", "Backup imported successfully.")
    except Exception as e:
        messagebox.showerror("Import Error", f"Failed to import backup.\n{e}")


# ---------------- LOGIN ----------------
def check_master_login():
    entered_password = master_entry.get().strip()

    if entered_password == MASTER_PASSWORD:
        login_window.destroy()
        open_main_app()
    else:
        messagebox.showerror("Login Failed", "Incorrect master password.")


# ---------------- MAIN APP ----------------
def open_main_app():
    global root
    global website_var, website_dropdown, username_entry, password_entry
    global toggle_btn, status_label, strength_label, info_label

    root = tk.Tk()
    root.title("Advanced Password Manager")
    root.geometry("1050x630+250+90")
    root.config(bg="#0f172a")
    root.resizable(False, False)

    # ---------- TITLE ----------
    title_frame = tk.Frame(root, bg="#0f172a")
    title_frame.pack(pady=15)

    title_label = tk.Label(
        title_frame,
        text="🔐 Advanced Password Manager",
        font=("Segoe UI", 22, "bold"),
        bg="#0f172a",
        fg="white"
    )
    title_label.pack()

    subtitle_label = tk.Label(
        title_frame,
        text="Securely save, search, update, and manage credentials",
        font=("Segoe UI", 10),
        bg="#0f172a",
        fg="#cbd5e1"
    )
    subtitle_label.pack(pady=4)

    # ---------- CARD ----------
    card = tk.Frame(root, bg="#1e293b")
    card.pack(padx=25, pady=10, fill="both", expand=True)

    # ---------- WEBSITE SECTION ----------
    website_section = tk.Frame(card, bg="#1e293b")
    website_section.pack(fill="x", padx=20, pady=(20, 10))

    tk.Label(
        website_section,
        text="Website / App",
        font=("Segoe UI", 11, "bold"),
        bg="#1e293b",
        fg="white"
    ).grid(row=0, column=0, sticky="w", pady=(0, 6))

    website_var = tk.StringVar()
    website_dropdown = ttk.Combobox(
        website_section,
        textvariable=website_var,
        font=("Segoe UI", 11),
        width=32
    )
    website_dropdown.grid(row=1, column=0, padx=(0, 10), pady=5, sticky="w")
    website_dropdown.bind("<<ComboboxSelected>>", autofill_fields)

    search_btn = tk.Button(
        website_section,
        text="🔍 Search",
        command=search_password,
        width=14,
        font=("Segoe UI", 10, "bold"),
        bg="#f59e0b",
        fg="white",
        bd=0,
        cursor="hand2"
    )
    search_btn.grid(row=1, column=1, padx=6)

    refresh_btn = tk.Button(
        website_section,
        text="🔄 Refresh",
        command=refresh_website_dropdown,
        width=14,
        font=("Segoe UI", 10, "bold"),
        bg="#3b82f6",
        fg="white",
        bd=0,
        cursor="hand2"
    )
    refresh_btn.grid(row=1, column=2, padx=6)

    # ---------- FORM SECTION ----------
    form_section = tk.Frame(card, bg="#1e293b")
    form_section.pack(fill="x", padx=20, pady=10)

    tk.Label(
        form_section,
        text="Username / Email",
        font=("Segoe UI", 11, "bold"),
        bg="#1e293b",
        fg="white"
    ).grid(row=0, column=0, sticky="w", pady=(0, 6))

    username_entry = tk.Entry(
        form_section,
        width=38,
        font=("Segoe UI", 11),
        bg="#f8fafc",
        fg="#0f172a"
    )
    username_entry.grid(row=1, column=0, padx=(0, 10), pady=5, sticky="w")

    tk.Label(
        form_section,
        text="Password",
        font=("Segoe UI", 11, "bold"),
        bg="#1e293b",
        fg="white"
    ).grid(row=2, column=0, sticky="w", pady=(14, 6))

    password_row = tk.Frame(form_section, bg="#1e293b")
    password_row.grid(row=3, column=0, sticky="w")

    password_entry = tk.Entry(
        password_row,
        width=30,
        font=("Segoe UI", 11),
        show="*",
        bg="#f8fafc",
        fg="#0f172a"
    )
    password_entry.grid(row=0, column=0, padx=(0, 8))
    password_entry.bind("<KeyRelease>", update_strength_label)

    toggle_btn = tk.Button(
        password_row,
        text="👁 Show",
        command=toggle_password,
        width=10,
        font=("Segoe UI", 10, "bold"),
        bg="#22c55e",
        fg="white",
        bd=0,
        cursor="hand2"
    )
    toggle_btn.grid(row=0, column=1, padx=4)

    copy_btn = tk.Button(
        password_row,
        text="📋 Copy",
        command=copy_password,
        width=10,
        font=("Segoe UI", 10, "bold"),
        bg="#8b5cf6",
        fg="white",
        bd=0,
        cursor="hand2"
    )
    copy_btn.grid(row=0, column=2, padx=4)

    generate_btn = tk.Button(
        password_row,
        text="⚡ Generate",
        command=generate_password,
        width=12,
        font=("Segoe UI", 10, "bold"),
        bg="#06b6d4",
        fg="white",
        bd=0,
        cursor="hand2"
    )
    generate_btn.grid(row=0, column=3, padx=4)

    # ---------- STRENGTH + DATES ----------
    meta_section = tk.Frame(card, bg="#1e293b")
    meta_section.pack(fill="x", padx=20, pady=10)

    strength_label = tk.Label(
        meta_section,
        text="Strength: -",
        font=("Segoe UI", 10, "bold"),
        bg="#1e293b",
        fg="#cbd5e1"
    )
    strength_label.pack(anchor="w", pady=3)

    info_label = tk.Label(
        meta_section,
        text="Created: -    |    Updated: -",
        font=("Segoe UI", 10),
        bg="#1e293b",
        fg="#cbd5e1"
    )
    info_label.pack(anchor="w", pady=3)

    # ---------- ACTION SECTION ----------
    action_section = tk.Frame(card, bg="#1e293b")
    action_section.pack(fill="x", padx=20, pady=20)

    save_btn = tk.Button(
        action_section,
        text="💾 Save",
        command=save_password,
        width=15,
        font=("Segoe UI", 11, "bold"),
        bg="#16a34a",
        fg="white",
        bd=0,
        cursor="hand2"
    )
    save_btn.grid(row=0, column=0, padx=8, pady=8)

    update_btn = tk.Button(
        action_section,
        text="✏ Update",
        command=update_password,
        width=15,
        font=("Segoe UI", 11, "bold"),
        bg="#2563eb",
        fg="white",
        bd=0,
        cursor="hand2"
    )
    update_btn.grid(row=0, column=1, padx=8, pady=8)

    delete_btn = tk.Button(
        action_section,
        text="🗑 Delete",
        command=delete_password,
        width=15,
        font=("Segoe UI", 11, "bold"),
        bg="#dc2626",
        fg="white",
        bd=0,
        cursor="hand2"
    )
    delete_btn.grid(row=0, column=2, padx=8, pady=8)

    clear_btn = tk.Button(
        action_section,
        text="🧹 Clear",
        command=clear_fields,
        width=15,
        font=("Segoe UI", 11, "bold"),
        bg="#475569",
        fg="white",
        bd=0,
        cursor="hand2"
    )
    clear_btn.grid(row=0, column=3, padx=8, pady=8)

    # ---------- BACKUP SECTION ----------
    backup_section = tk.Frame(card, bg="#1e293b")
    backup_section.pack(fill="x", padx=20, pady=10)

    export_btn = tk.Button(
        backup_section,
        text="📤 Export Backup",
        command=export_backup,
        width=18,
        font=("Segoe UI", 11, "bold"),
        bg="#0ea5e9",
        fg="white",
        bd=0,
        cursor="hand2"
    )
    export_btn.grid(row=0, column=0, padx=8, pady=8)

    import_btn = tk.Button(
        backup_section,
        text="📥 Import Backup",
        command=import_backup,
        width=18,
        font=("Segoe UI", 11, "bold"),
        bg="#9333ea",
        fg="white",
        bd=0,
        cursor="hand2"
    )
    import_btn.grid(row=0, column=1, padx=8, pady=8)

    # ---------- STATUS ----------
    status_label = tk.Label(
        root,
        text="Ready.",
        font=("Segoe UI", 10),
        bg="#0f172a",
        fg="#cbd5e1",
        anchor="w"
    )
    status_label.pack(fill="x", padx=28, pady=(0, 10))

    # ---------- HOVER EFFECTS ----------
    add_hover_effect(search_btn, "#f59e0b", "#d97706")
    add_hover_effect(refresh_btn, "#3b82f6", "#2563eb")
    add_hover_effect(toggle_btn, "#22c55e", "#16a34a")
    add_hover_effect(copy_btn, "#8b5cf6", "#7c3aed")
    add_hover_effect(generate_btn, "#06b6d4", "#0891b2")
    add_hover_effect(save_btn, "#16a34a", "#15803d")
    add_hover_effect(update_btn, "#2563eb", "#1d4ed8")
    add_hover_effect(delete_btn, "#dc2626", "#b91c1c")
    add_hover_effect(clear_btn, "#475569", "#334155")
    add_hover_effect(export_btn, "#0ea5e9", "#0284c7")
    add_hover_effect(import_btn, "#9333ea", "#7e22ce")

    refresh_website_dropdown()
    root.mainloop()


# ---------------- LOGIN WINDOW ----------------
login_window = tk.Tk()
login_window.title("Master Login")
login_window.geometry("1050x630+250+90")
login_window.config(bg="#0f172a")
login_window.resizable(False, False)

login_card = tk.Frame(login_window, bg="#1e293b")
login_card.pack(expand=True, fill="both", padx=25, pady=25)

tk.Label(
    login_card,
    text="🔐 Secure Master Login",
    font=("Segoe UI", 18, "bold"),
    bg="#1e293b",
    fg="white"
).pack(pady=(25, 10))

tk.Label(
    login_card,
    text="Enter your master password to continue",
    font=("Segoe UI", 10),
    bg="#1e293b",
    fg="#cbd5e1"
).pack(pady=(0, 15))

master_entry = tk.Entry(
    login_card,
    width=25,
    font=("Segoe UI", 12),
    show="*",
    justify="center",
    bg="#f8fafc",
    fg="#0f172a"
)
master_entry.pack(pady=8)

login_btn = tk.Button(
    login_card,
    text="🔓 Login",
    width=13,height=1,
    font=("Segoe UI", 13, "bold"),
    bg="#22c55e",
    fg="white",
    bd=0,
    cursor="hand2",
    command=check_master_login
)
login_btn.pack(pady=18)

add_hover_effect(login_btn, "#22c55e", "#16a34a")

login_window.mainloop()
