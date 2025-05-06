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
        self.root.geometry("800x600")
        self.root.configure(bg=BG_COLOR)

        self.frames = {}
        self.init_frames()
        self.show_frame("home")

        self.dynamic_builders = {
            "selected_group": self.build_open_group_frame,
            "add_users": self.build_add_users_frame,
            "create_expense": self.build_create_expense_frame,
            # more to be added...
        }

    def init_frames(self):
        self.frames["home"] = self.build_home_frame()
        self.frames["user"] = self.build_user_frame()
        self.frames["group"] = self.build_group_frame()
        self.frames["all_groups"] = self.build_all_groups_frame()


    def show_frame(self, name):
        for frame in self.frames.values():
            frame.pack_forget()
        self.frames[name].pack(fill="both", expand=True)

        self.refresh_static_widgets()
    
    def refresh_static_widgets(self):
        if hasattr(self, "existing_groups_listbox"):
            self.load_groups_listbox(self.existing_groups_listbox)
        if hasattr(self, "all_groups_listbox"):
            self.load_groups_listbox(self.all_groups_listbox)
        if hasattr(self, "creator_dropdown") and hasattr(self, "creator_var"):
            self.load_users_dropdown(self.creator_dropdown, self.creator_var)       

    def load_groups_listbox(self, listbox):
        listbox.delete(0, tk.END)
        groups = app.get_all_groups()
        for group in groups:
            listbox.insert(tk.END, f"{group.id}: {group.name} (created by {group.created_by})")

    def load_users_dropdown(self, menu_widget, string_var):
            users = app.get_all_users()
            menu = menu_widget['menu']
            menu.delete(0, 'end')
            if users:
                for user in users:
                    label = f"{user.username} ({user.first_name} {user.last_name})"
                    menu.add_command(label=label, command=tk._setit(string_var, label))
                string_var.set(f"{users[0].username} ({users[0].first_name} {users[0].last_name})")
            else:
                placeholder = "No users available"
                menu.add_command(label=placeholder, state="disabled")
                string_var.set(placeholder)

    def open_dynamic_frame(self, frame_name, group_id=None, user_id=None, expense_id=None, share_id=None):
        if frame_name in self.frames:
            self.frames[frame_name].destroy()

        builder = self.dynamic_builders.get(frame_name)
        if builder:
            frame = builder(
                group_id=group_id,
                user_id=user_id,
                expense_id=expense_id,
                share_id=share_id
            )
            self.frames[frame_name] = frame
            self.show_frame(frame_name)
        else:
            print(f"No builder found for frame: {frame_name}")

    

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

        tk.Label(frame, text="New User", bg=BG_COLOR, fg=FG_COLOR, font=FONT).pack()

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
                username_entry.delete(0, tk.END)
                first_name_entry.delete(0, tk.END)
                last_name_entry.delete(0, tk.END)
                email_entry.delete(0, tk.END)
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

        def delete_selected_user():
            selected = self.user_listbox.get(tk.ACTIVE)
            if selected:
                user_id = int(selected.split(":")[0])
                if app.delete_user(user_id):
                    messagebox.showinfo("Success", f"User with ID {user_id} deleted.")
                    load_users()
                else:
                    messagebox.showerror("Error", "Failed to delete user.")
        
        tk.Button(frame, text="Delete Selected", command=delete_selected_user,
          bg=BG_COLOR, fg=FG_COLOR, font=FONT).pack(pady=5)

        tk.Button(frame, text="Back", command=lambda: self.show_frame("home"), bg=BG_COLOR, fg=FG_COLOR, font=FONT).pack(pady=5)
        return frame

    def build_group_frame(self):
        frame = tk.Frame(self.root, bg=BG_COLOR)

        tk.Label(frame, text="New Group", bg=BG_COLOR, fg=FG_COLOR, font=FONT).pack()

        name_entry = labeled_entry(frame, "Group Name")
        desc_entry = labeled_entry(frame, "Description")

        creator_var = tk.StringVar(frame)
        dropdown = tk.OptionMenu(frame, creator_var, "")
        dropdown.config(bg=BG_COLOR, fg=FG_COLOR, font=FONT, highlightthickness=0)
        
        tk.Label(frame, text="Creator (Username)", bg=BG_COLOR, fg=FG_COLOR, font=FONT).pack()
        dropdown.pack()

        self.creator_dropdown = dropdown
        self.creator_var = creator_var

        self.existing_groups_listbox = tk.Listbox(frame, width=60, bg=BG_COLOR, fg=FG_COLOR, font=FONT)
        self.existing_groups_listbox.pack(pady=5)

        def submit_group():
            selected_label = creator_var.get()
            users = app.get_all_users()
            selected_user = next((u for u in users if f"{u.username} ({u.first_name} {u.last_name})" == selected_label), None)
            created_by = selected_user.id if selected_user else None

            name = name_entry.get().strip()
            description = desc_entry.get().strip()

            if not name or not re.match(r'^[a-zA-Z0-9._ -]+$', name):
                messagebox.showerror("Validation Error", "Group name must contain only letters, numbers, spaces or . - _")
                return

            group_id = app.create_group(
                name=name,
                description=description,
                created_by=created_by
            )
            if group_id:
                messagebox.showinfo("Success", f"Group created with ID {group_id}")
                name_entry.delete(0, tk.END)
                desc_entry.delete(0, tk.END)
                self.load_groups_listbox(self.existing_groups_listbox)
            else:
                messagebox.showerror("Error", "Failed to create group")

        self.load_users_dropdown(self.creator_dropdown, self.creator_var)
        self.load_groups_listbox(self.existing_groups_listbox)

        tk.Button(frame, text="Submit", command=submit_group, bg=BG_COLOR, fg=FG_COLOR, font=FONT).pack(pady=5)
        tk.Button(frame, text="Back", command=lambda: self.show_frame("home"), bg=BG_COLOR, fg=FG_COLOR, font=FONT).pack(pady=5)
        return frame

    def build_all_groups_frame(self):
        frame = tk.Frame(self.root, bg=BG_COLOR)

        tk.Label(frame, text="All Expense Groups", bg=BG_COLOR, fg=FG_COLOR, font=FONT).pack(pady=10)

        self.all_groups_listbox = tk.Listbox(frame, width=60, bg=BG_COLOR, fg=FG_COLOR, font=FONT)
        self.all_groups_listbox.pack(pady=5)

        def access_selected_group():
            selected = self.all_groups_listbox.get(tk.ACTIVE)
            if selected:
                group_id = int(selected.split(":")[0])
                self.open_dynamic_frame("selected_group", group_id=group_id)

        def delete_selected_group():
            selected = self.all_groups_listbox.get(tk.ACTIVE)
            if selected:
                group_id = int(selected.split(":")[0])
                if app.delete_group(group_id):
                    messagebox.showinfo("Success", f"Group with ID {group_id} deleted.")
                    self.load_groups_listbox(self.all_groups_listbox)
                else:
                    messagebox.showerror("Error", "Failed to delete group.")

        self.load_groups_listbox(self.all_groups_listbox)

        tk.Button(frame, text="Open Selected", command=access_selected_group,
                  bg=BG_COLOR, fg=FG_COLOR, font=FONT).pack(pady=5)
        tk.Button(frame, text="Delete Selected", command=delete_selected_group,
                  bg=BG_COLOR, fg=FG_COLOR, font=FONT).pack(pady=5)
        tk.Button(frame, text="Back", command=lambda: self.show_frame("home"),
                  bg=BG_COLOR, fg=FG_COLOR, font=FONT).pack(pady=5)
        return frame

    def build_open_group_frame(self, group_id=None, **kwargs):
        frame = tk.Frame(self.root, bg=BG_COLOR)
        group_info = app.get_expense_group(group_id)
        tk.Label(frame, text=group_info.name, bg=BG_COLOR, fg=FG_COLOR, font=FONT).pack(pady=5)
        tk.Label(frame, text=group_info.description, bg=BG_COLOR, fg=FG_COLOR, font=FONT).pack(pady=5)

        # Fetch and show current group members, manage group members
        members = app.get_group_members(group_id)

        member_labels = [f"{u.username} ({u.first_name} {u.last_name})" for u in members]
        if not member_labels:
            member_labels = ["No members"]

        member_var = tk.StringVar(frame)
        member_var.set(member_labels[0])

        member_dropdown = tk.OptionMenu(frame, member_var, *member_labels)
        member_dropdown.config(bg=BG_COLOR, fg=FG_COLOR, font=FONT, highlightthickness=0)

        tk.Label(frame, text="Group Members", bg=BG_COLOR, fg=FG_COLOR, font=FONT).pack()
        member_dropdown.pack()

        tk.Button(frame, text="Manage Members", command =lambda: self.open_dynamic_frame("add_users", group_id=group_id),
                  bg=BG_COLOR, fg=FG_COLOR, font=FONT).pack(pady=5)
        
        # Show and manage expenses

        def load_expenses_listbox(listbox, group_id):
            listbox.delete(0, tk.END)
            expenses = app.get_group_expenses(group_id)
            if expenses:
                for expense in expenses:
                    payer = app.get_user(expense.paid_by)
                    listbox.insert(tk.END, f"{expense.date}  {expense.description} {expense.amount:.2f}€  Paid by: {payer.username}")


        tk.Label(frame, text="All Expenses", bg=BG_COLOR, fg=FG_COLOR, font=FONT).pack(pady=10)

        self.expenses_listbox = tk.Listbox(frame, width=80, bg=BG_COLOR, fg=FG_COLOR, font=FONT)
        self.expenses_listbox.pack(pady=5)
        load_expenses_listbox(self.expenses_listbox, group_id)

        tk.Button(frame, text="New Expense", 
                command=lambda: self.open_dynamic_frame("create_expense",group_id=group_id),
                bg=BG_COLOR, fg=FG_COLOR, font=FONT).pack(pady=5)
        tk.Button(frame, text="Back", command=lambda: self.show_frame("all_groups"),
                bg=BG_COLOR, fg=FG_COLOR, font=FONT).pack(pady=5)
    
        return frame

    def build_add_users_frame(self, group_id=None, **kwargs):
        frame = tk.Frame(self.root, bg=BG_COLOR)

        tk.Label(frame, text="Add Users to Group", bg=BG_COLOR, fg=FG_COLOR, font=FONT).pack(pady=10)

        # Dictionary to track checkbox variables by user_id
        self.user_check_vars = {}

        users = app.get_all_users()
        members = app.get_group_members(group_id)
        member_ids = {m.id for m in members}

        for user in users:
            var = tk.BooleanVar()
            var.set(user.id in member_ids)

            def on_toggle(u=user, v=var):
                if v.get():
                    app.add_member(group_id=group_id, user_id=u.id)
                else:
                    app.remove_member(group_id=group_id, user_id=u.id)

            cb = tk.Checkbutton(
                frame,
                text=f"{user.username} ({user.first_name} {user.last_name})",
                variable=var,
                command=on_toggle,
                bg=BG_COLOR,
                fg=FG_COLOR,
                font=FONT,
                selectcolor=BG_COLOR,
                activebackground=BG_COLOR,
                activeforeground=FG_COLOR
            )
            cb.pack(anchor="w")

        tk.Button(frame, text="Back", command=lambda: self.open_dynamic_frame("selected_group", group_id=group_id),
                  bg=BG_COLOR, fg=FG_COLOR, font=FONT).pack()

        return frame


# Start app
if __name__ == "__main__":
    root = tk.Tk()
    app_ui = ExpenseManagerApp(root)
    root.mainloop()
