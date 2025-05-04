import tkinter as tk
from tkinter import messagebox
import app

# === Theme Settings ===
BG_COLOR = "#1e1e1e"
FG_COLOR = "#00ff00"
FONT = ("Courier", 10)

class ExpenseManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Expense Manager v1")
        self.root.geometry("600x500")
        self.root.configure(bg=BG_COLOR)

        self.create_home_screen()

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def create_home_screen(self):
        self.clear_screen()

        tk.Label(self.root, text="Expense Manager v1", font=("Courier", 14, "bold"),
                 bg=BG_COLOR, fg=FG_COLOR).pack(pady=20)

        tk.Button(self.root, text="Create User", command=self.user_menu,
                  bg=BG_COLOR, fg=FG_COLOR, font=FONT, width=25).pack(pady=10)
        tk.Button(self.root, text="Create Group", command=self.group_menu,
                  bg=BG_COLOR, fg=FG_COLOR, font=FONT, width=25).pack(pady=10)
        tk.Button(self.root, text="View All Groups", command=self.all_groups_menu,
                  bg=BG_COLOR, fg=FG_COLOR, font=FONT, width=25).pack(pady=10)

    def user_menu(self):
        self.clear_screen()

        tk.Label(self.root, text="Create New User", bg=BG_COLOR, fg=FG_COLOR, font=FONT).pack()

        username_entry = tk.Entry(self.root, bg=BG_COLOR, fg=FG_COLOR, font=FONT, insertbackground=FG_COLOR)
        first_name_entry = tk.Entry(self.root, bg=BG_COLOR, fg=FG_COLOR, font=FONT, insertbackground=FG_COLOR)
        last_name_entry = tk.Entry(self.root, bg=BG_COLOR, fg=FG_COLOR, font=FONT, insertbackground=FG_COLOR)
        email_entry = tk.Entry(self.root, bg=BG_COLOR, fg=FG_COLOR, font=FONT, insertbackground=FG_COLOR)

        for label, entry in zip(["Username", "First Name", "Last Name", "Email"],
                                [username_entry, first_name_entry, last_name_entry, email_entry]):
            tk.Label(self.root, text=label, bg=BG_COLOR, fg=FG_COLOR, font=FONT).pack()
            entry.pack()

        def submit_user():
            user_id = app.create_user(
                username=username_entry.get(),
                first_name=first_name_entry.get(),
                last_name=last_name_entry.get(),
                email=email_entry.get()
            )
            if user_id:
                messagebox.showinfo("Success", f"User created with ID {user_id}")
                self.user_menu()
            else:
                messagebox.showerror("Error", "Failed to create user")

        tk.Button(self.root, text="Submit", command=submit_user,
                  bg=BG_COLOR, fg=FG_COLOR, font=FONT).pack(pady=5)

        tk.Label(self.root, text="Existing Users:", bg=BG_COLOR, fg=FG_COLOR, font=FONT).pack(pady=(10, 0))
        self.user_listbox = tk.Listbox(self.root, width=60, bg=BG_COLOR, fg=FG_COLOR, font=FONT)
        self.user_listbox.pack(pady=5)

        def load_users():
            self.user_listbox.delete(0, tk.END)
            users = app.get_all_users()
            for user in users:
                self.user_listbox.insert(tk.END, f"{user.id}: {user.username} ({user.first_name} {user.last_name})")

        load_users()

        tk.Button(self.root, text="Back", command=self.create_home_screen,
                  bg=BG_COLOR, fg=FG_COLOR, font=FONT).pack(pady=5)

    def group_menu(self):
        self.clear_screen()
        tk.Label(self.root, text="Create New Group", bg=BG_COLOR, fg=FG_COLOR, font=FONT).pack()

        name_entry = tk.Entry(self.root, bg=BG_COLOR, fg=FG_COLOR, font=FONT, insertbackground=FG_COLOR)
        desc_entry = tk.Entry(self.root, bg=BG_COLOR, fg=FG_COLOR, font=FONT, insertbackground=FG_COLOR)

        creator_var = tk.StringVar(self.root)
        creator_dropdown = tk.OptionMenu(self.root, creator_var, "")
        creator_dropdown.config(bg=BG_COLOR, fg=FG_COLOR, font=FONT, highlightthickness=0)

        for label, widget in zip(["Group Name", "Description", "Creator (Username)"],
                                [name_entry, desc_entry, creator_dropdown]):
            tk.Label(self.root, text=label, bg=BG_COLOR, fg=FG_COLOR, font=FONT).pack()
            widget.pack()

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

            group_id = app.create_group(
                name=name_entry.get(),
                description=desc_entry.get(),
                created_by=created_by
            )
            if group_id:
                messagebox.showinfo("Success", f"Group created with ID {group_id}")
                load_groups()
            else:
                messagebox.showerror("Error", "Failed to create group")

        load_users_for_dropdown()

        tk.Button(self.root, text="Submit", command=submit_group,
                  bg=BG_COLOR, fg=FG_COLOR, font=FONT).pack(pady=5)

        tk.Label(self.root, text="Groups:", bg=BG_COLOR, fg=FG_COLOR, font=FONT).pack(pady=(10, 0))
        self.group_listbox = tk.Listbox(self.root, width=60, bg=BG_COLOR, fg=FG_COLOR, font=FONT)
        self.group_listbox.pack(pady=5)

        def load_groups():
            self.group_listbox.delete(0, tk.END)
            groups = app.get_all_groups()
            for group in groups:
                self.group_listbox.insert(tk.END, f"{group.id}: {group.name} (created by {group.created_by})")

        load_groups()

        tk.Button(self.root, text="Back", command=self.create_home_screen,
                  bg=BG_COLOR, fg=FG_COLOR, font=FONT).pack(pady=5)

    def all_groups_menu(self):
        self.clear_screen()

        tk.Label(self.root, text="All Expense Groups", bg=BG_COLOR, fg=FG_COLOR, font=FONT).pack(pady=10)

        self.group_listbox = tk.Listbox(self.root, width=60, bg=BG_COLOR, fg=FG_COLOR, font=FONT)
        self.group_listbox.pack(pady=5)

        def load_all_groups():
            self.group_listbox.delete(0, tk.END)
            groups = app.get_all_groups()
            for group in groups:
                self.group_listbox.insert(tk.END, f"{group.id}: {group.name} (created by {group.created_by})")

        def access_selected_group():
            selected = self.group_listbox.get(tk.ACTive)
            if selected:
                group_id = int(selected.split(":")[0])
                self.open_group(group_id)

        load_all_groups()

        tk.Button(self.root, text="Open Selected Group", command=access_selected_group,
                  bg=BG_COLOR, fg=FG_COLOR, font=FONT).pack(pady=5)

        tk.Button(self.root, text="Back", command=self.create_home_screen,
                  bg=BG_COLOR, fg=FG_COLOR, font=FONT).pack(pady=5)

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
