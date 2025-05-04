import tkinter as tk
from tkinter import messagebox
import app  # Your app.py file

# Retro terminal look
BG_COLOR = "#1e1e1e"  # Deep gray
FG_COLOR = "#00ff00"  # Terminal green
FONT = ("Courier", 10)

# Create main window
root = tk.Tk()
root.title("Expense Manager - Users")
root.geometry("800x500")
root.configure(bg=BG_COLOR)

# Entry fields
username_entry = tk.Entry(root, bg=BG_COLOR, fg=FG_COLOR, font=FONT, insertbackground=FG_COLOR)
first_name_entry = tk.Entry(root, bg=BG_COLOR, fg=FG_COLOR, font=FONT, insertbackground=FG_COLOR)
last_name_entry = tk.Entry(root, bg=BG_COLOR, fg=FG_COLOR, font=FONT, insertbackground=FG_COLOR)
email_entry = tk.Entry(root, bg=BG_COLOR, fg=FG_COLOR, font=FONT, insertbackground=FG_COLOR)

# Layout
tk.Label(root, text="Username", bg=BG_COLOR, fg=FG_COLOR, font=FONT).pack()
username_entry.pack()

tk.Label(root, text="First Name", bg=BG_COLOR, fg=FG_COLOR, font=FONT).pack()
first_name_entry.pack()

tk.Label(root, text="Last Name", bg=BG_COLOR, fg=FG_COLOR, font=FONT).pack()
last_name_entry.pack()

tk.Label(root, text="Email", bg=BG_COLOR, fg=FG_COLOR, font=FONT).pack()
email_entry.pack()

# Display box for users
tk.Label(root, text="Users:", bg=BG_COLOR, fg=FG_COLOR, font=FONT).pack(pady=(10, 0))
user_listbox = tk.Listbox(root, width=60, bg=BG_COLOR, fg=FG_COLOR, font=FONT, highlightthickness=0, borderwidth=0)
user_listbox.pack(pady=10)

# Functions
def create_user():
    username = username_entry.get()
    if not username:
        messagebox.showerror("Error", "Username is required")
        return

    user_id = app.create_user(
        username=username,
        first_name=first_name_entry.get(),
        last_name=last_name_entry.get(),
        email=email_entry.get()
    )
    if user_id:
        messagebox.showinfo("Success", f"User created with ID {user_id}")
        update_user_list()
    else:
        messagebox.showerror("Error", "Failed to create user (maybe duplicate?)")

def update_user_list():
    user_listbox.delete(0, tk.END)
    users = app.get_all_users()
    for user in users:
        user_listbox.insert(tk.END, f"{user.id}: {user.username} ({user.first_name} {user.last_name})")

# Button
tk.Button(root, text="Create User", command=create_user,
          bg=BG_COLOR, fg=FG_COLOR, font=FONT, activebackground="#333", activeforeground=FG_COLOR).pack(pady=5)

# Initial load
update_user_list()

# Run the app
root.mainloop()