import tkinter as tk
from tkinter import messagebox
import app
import re

# === Theme Settings ===
BG_COLOR = "#1e1e1e"
FG_COLOR = "#00ff00"
FONT = ("Courier", 10)

# === Reusable Widgets ===
def labeled_entry(parent, label_text):
    tk.Label(parent, text=label_text, bg=BG_COLOR, fg=FG_COLOR, font=FONT).pack()
    entry = tk.Entry(parent, bg=BG_COLOR, fg=FG_COLOR, font=FONT, insertbackground=FG_COLOR)
    entry.pack()
    return entry

class ExpenseManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Expense Manager v1")
        self.root.geometry("600x500")
        self.root.configure(bg=BG_COLOR)

        self.frames = {}
        self.init_frames()
        self.show_frame("home")

    def init_frames(self):
        self.frames["home"] = self.build_home_frame()
        self.frames["user"] = self.build_user_frame()
        self.frames["group"] = self.build_group_frame()
        self.frames["all_groups"] = self.build_all_groups_frame()

    def show_frame(self, name):
        for frame in self.frames.values():
            frame.pack_forget()
        self.frames[name].pack(fill="both", expand=True)

    def build_home_frame(self):
        frame = tk.Frame(self.root, bg=BG_COLOR)

        tk.Label(frame, text="Expense Manager v1", font=("Courier", 14, "bold"), bg=BG_COLOR, fg=FG_COLOR).pack(pady=20)

        tk.Button(frame, text="Create User", command=lambda: self.show_frame("user"),
                  bg=BG_COLOR, fg=FG_COLOR, font=FONT, width=25).pack(pady=10)
        tk.Button(frame, text="Create Group", command=lambda: self.show_frame("group"),
                  bg=BG_COLOR, fg=FG_COLOR, font=FONT, width=25).pack(pady=10)
        tk.Button(frame, text="View All Groups", command=lambda: self.show_frame("all_groups"),
                  bg=BG_COLOR, fg=FG_COLOR, font=FONT, width=25).pack(pady=10)

        return frame

    def build_user_frame(self):
        frame = tk.Frame(self.root, bg=BG_COLOR)

        tk.Label(frame, text="Create New User", bg=BG_COLOR, fg=FG_COLOR, font=FONT).pack()

        username_entry = labeled_entry(frame, "Username")
        first_name_entry = labeled_entry(frame, "First Name")
        last_name_entry = labeled_entry(frame, "Last Name")
        email_entry = labeled_entry(frame, "Email")

        def submit_user():
            username = username_entry.get().strip()
            first_name = first_name_entry.get().strip()
            last_name = last_name_entry.get().strip()
            email = email_entry.get().strip()
            
            if not username or not re.match(r'^[a-zA-Z0-9._-]+$', username):
                messagebox.showerror("Validation Error", "Username must contain only letters, numbers, dots, dashes or underscores — no spaces.")
                return
            
            if not all(name and re.match(r'^[a-zA-Z]+$', name) for name in (first_name, last_name)):
                messagebox.showerror("Validation Error", "Name must contain only letters.")
                return
            
            if email and not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
                messagebox.showerror("Validation Error", "Email not valid.")
                return
            
            user_id = app.create_user(
                username=username,
                first_name=first_name,
                last_name=last_name,
                email=email
            )
            if user_id:
                messagebox.showinfo("Success", f"User created with ID {user_id}")
                load_users()
            else:
                messagebox.showerror("Error", "Failed to create user")

        tk.Button(frame, text="Submit", command=submit_user, bg=BG_COLOR, fg=FG_COLOR, font=FONT).pack(pady=5)

        tk.Label(frame, text="Existing Users:", bg=BG_COLOR, fg=FG_COLOR, font=FONT).pack(pady=(10, 0))
        self.user_listbox = tk.Listbox(frame, width=60, bg=BG_COLOR, fg=FG_COLOR, font=FONT)
        self.user_listbox.pack(pady=5)

        def load_users():
            self.user_listbox.delete(0, tk.END)
            users = app.get_all_users()
            for user in users:
                self.user_listbox.insert(tk.END, f"{user.id}: {user.username} ({user.first_name} {user.last_name})")

        load_users()

        tk.Button(frame, text="Back", command=lambda: self.show_frame("home"), bg=BG_COLOR, fg=FG_COLOR, font=FONT).pack(pady=5)
        return frame

    def build_group_frame(self):
        frame = tk.Frame(self.root, bg=BG_COLOR)

        tk.Label(frame, text="Create New Group", bg=BG_COLOR, fg=FG_COLOR, font=FONT).pack()

        name_entry = labeled_entry(frame, "Group Name")
        desc_entry = labeled_entry(frame, "Description")

        creator_var = tk.StringVar(frame)
        creator_dropdown = tk.OptionMenu(frame, creator_var, "")
        creator_dropdown.config(bg=BG_COLOR, fg=FG_COLOR, font=FONT, highlightthickness=0)
        tk.Label(frame, text="Creator (Username)", bg=BG_COLOR, fg=FG_COLOR, font=FONT).pack()
        creator_dropdown.pack()

        self.group_listbox = tk.Listbox(frame, width=60, bg=BG_COLOR, fg=FG_COLOR, font=FONT)
        self.group_listbox.pack(pady=5)

        def load_users_for_dropdown():
            users = app.get_all_users()
            creator_dropdown['menu'].delete(0, 'end')
            if users:
                for user in users:
                    label = f"{user.username} ({user.first_name} {user.last_name})"
                    creator_dropdown['menu'].add_command(label=label, command=tk._setit(creator_var, label))
                creator_var.set(f"{users[0].username} ({users[0].first_name} {users[0].last_name})")

        def submit_group():
            selected_label = creator_var.get()
            users = app.get_all_users()
            selected_user = next((u for u in users if f"{u.username} ({u.first_name} {u.last_name})" == selected_label), None)
            created_by = selected_user.id if selected_user else None

            name = name_entry.get().strip()
            description = desc_entry.get().strip()

            if not name or not re.match(r'^[a-zA-Z0-9._- ]+$', name):
                messagebox.showerror("Validation Error", "Group name must contain only letters, numbers, spaces or . - _")
                return

            group_id = app.create_group(
                name=name,
                description=description,
                created_by=created_by
            )
            if group_id:
                messagebox.showinfo("Success", f"Group created with ID {group_id}")
                self.load_groups_listbox(self.group_listbox)
            else:
                messagebox.showerror("Error", "Failed to create group")

        def load_groups_listbox():
            self.group_listbox.delete(0, tk.END)
            groups = app.get_all_groups()
            for group in groups:
                self.group_listbox.insert(tk.END, f"{group.id}: {group.name} (created by {group.created_by})")

        load_users_for_dropdown()
        load_groups_listbox()

        tk.Button(frame, text="Submit", command=submit_group, bg=BG_COLOR, fg=FG_COLOR, font=FONT).pack(pady=5)
        tk.Button(frame, text="Back", command=lambda: self.show_frame("home"), bg=BG_COLOR, fg=FG_COLOR, font=FONT).pack(pady=5)
        return frame

    def build_all_groups_frame(self):
        frame = tk.Frame(self.root, bg=BG_COLOR)

        tk.Label(frame, text="All Expense Groups", bg=BG_COLOR, fg=FG_COLOR, font=FONT).pack(pady=10)

        self.group_listbox = tk.Listbox(frame, width=60, bg=BG_COLOR, fg=FG_COLOR, font=FONT)
        self.group_listbox.pack(pady=5)

        def load_groups_listbox():
            self.group_listbox.delete(0, tk.END)
            groups = app.get_all_groups()
            for group in groups:
                self.group_listbox.insert(tk.END, f"{group.id}: {group.name} (created by {group.created_by})")

        def access_selected_group():
            selected = self.group_listbox.get(tk.ACTIVE)
            if selected:
                group_id = int(selected.split(":")[0])
                self.open_group(group_id)

        load_groups_listbox()

        tk.Button(frame, text="Open Selected Group", command=access_selected_group,
                  bg=BG_COLOR, fg=FG_COLOR, font=FONT).pack(pady=5)
        tk.Button(frame, text="Back", command=lambda: self.show_frame("home"),
                  bg=BG_COLOR, fg=FG_COLOR, font=FONT).pack(pady=5)
        return frame

    def open_group(self, group_id):
        self.clear_screen()
        tk.Label(self.root, text=f"Group ID {group_id}", bg=BG_COLOR, fg=FG_COLOR, font=FONT).pack(pady=5)

        tk.Button(self.root, text="Add User to Group (WIP)", bg=BG_COLOR, fg=FG_COLOR, font=FONT).pack(pady=5)
        tk.Button(self.root, text="Create Expense (WIP)", bg=BG_COLOR, fg=FG_COLOR, font=FONT).pack(pady=5)
        tk.Button(self.root, text="Back", command=self.all_groups_menu,
                  bg=BG_COLOR, fg=FG_COLOR, font=FONT).pack(pady=5)


# Start app
if __name__ == "__main__":
    root = tk.Tk()
    app_ui = ExpenseManagerApp(root)
    root.mainloop()
