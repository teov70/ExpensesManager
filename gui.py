import tkinter as tk
from tkinter import messagebox
import app
import re

# === Theme Settings ===
THEMES = {
    "Classic": {"bg": "#1e1e1e", "fg": "#00ff00", "oh": "#4d824d"},   # Hacker default
    "Accent": {"bg": "#281e36", "fg": "#00ffae", "oh": "#574275"},    # Subtle hacker
    "BSOD": {"bg": "#000088", "fg": "#ffffff", "oh": "#858585"},      # Blue Screen of Death
    "Barbie": {"bg": "#fcb8eb", "fg": "#ff1493", "oh": "#ffd4e6"},    # Pink paradise

    "Commodore64": {"bg": "#40318d", "fg": "#a5a5ff", "oh": "#7869c4"},  # Retro 8-bit
    "Matrix": {"bg": "#000000", "fg": "#00ff00", "oh": "#003b00"},       # Neo-approved
    "Vaporwave": {"bg": "#ff71ce", "fg": "#05ffa1", "oh": "#b967ff"},    # Neon nostalgia
    "FrutigerAero": {"bg": "#93e046", "fg": "#007ca6", "oh": "#a2cfe0"},  # Fresh 2000s aesthetic
    "PumpkinSpice": {"bg": "#331800", "fg": "#ffa500", "oh": "#663300"}, # Autumn vibes
    "Fallout": {"bg": "#003b3b", "fg": "#18ff00", "oh": "#007070"},      # Vault-tec terminal
    "Coffee": {"bg": "#4b3621", "fg": "#d2b48c", "oh": "#6e5534"},       # Late-night coding
    "Cyberpunk": {"bg": "#2a2139", "fg": "#ff2a6d", "oh": "#5c3b6e"},    # Night City
    "Windows95": {"bg": "#c3c7cb", "fg": "#000080", "oh": "#e7e8ea"},    # Nostalgia overload
    "AmericanPsycho": {"bg": "#edebdd", "fg": "#1f1e1d", "oh": "#d65747"}
}

FONTS = {
    "Default":  None,
    "Courier":  "Courier New",
    "Consolas": "Consolas",
    "Cascadia": "Cascadia Mono",
    "Segoe":    "Segoe UI Mono",
    "Helvetica": "Helvetica",
    "Verdana": "Verdana"
}
FONT_SIZES = {"S": 10, "M": 11, "L": 12, "XL": 14}

BG_COLOR = THEMES["Classic"]["bg"]
FG_COLOR = THEMES["Classic"]["fg"]
OH_COLOR = THEMES["Classic"]["oh"]

FONT_FAMILY = None
FONT_SIZE   = 11

class ExpenseManagerApp:
    def __init__(self, root):
        self.root = root
        self.apply_theme()
        self.apply_font()
        self.root.title("Expense Manager v1")
        self.root.iconbitmap("icon_black_multi.ico")
        self.root.geometry("800x650")
        self.root.configure(bg=BG_COLOR)

        self.frames = {}
        self.init_frames()
        # Names of frames that should keep the menubar visible
        self.static_frames = {"home", "user", "group", "all_groups"}
        self.build_menubar()
        self.root.config(menu=self.menubar)
        self.show_frame("home")

        self.dynamic_builders = {
            "selected_group": self.build_open_group_frame,
            "add_users": self.build_add_users_frame,
            "create_expense": self.build_create_expense_frame,
            # more to be added...
        }

# ── SETTINGS MENU ───────────────────────────────────────────
    def build_menubar(self):
        self.menubar = tk.Menu(self.root)

        # Theme submenu
        theme_menu = tk.Menu(self.menubar, tearoff=0)
        for name in THEMES:
            theme_menu.add_command(
                label=name,
                command=lambda n=name: self.set_theme(n)
            )
        self.menubar.add_cascade(label="Theme", menu=theme_menu)

        # Font‑family submenu
        font_menu = tk.Menu(self.menubar, tearoff=0)
        for name in FONTS:
            font_menu.add_command(
                label=name,
                command=lambda n=name: self.set_font_family(n)
            )
        self.menubar.add_cascade(label="Font", menu=font_menu)

        # Font‑size submenu
        size_menu = tk.Menu(self.menubar, tearoff=0)
        for label, size in FONT_SIZES.items():
            size_menu.add_command(
                label=label,
                command=lambda s=size: self.set_font_size(s)
            )
        self.menubar.add_cascade(label="Size", menu=size_menu)

        self.root.config(menu=self.menubar)

# ── APPLY FUNCTIONS ────────────────────────────────────────
    def set_theme(self, name):
        global BG_COLOR, FG_COLOR, OH_COLOR
        BG_COLOR = THEMES[name]["bg"]
        FG_COLOR = THEMES[name]["fg"]
        OH_COLOR = THEMES[name]["oh"]
        self.apply_theme()
        self.repaint_static_frames()

    def set_font_family(self, name):
        global FONT_FAMILY
        FONT_FAMILY = FONTS[name]
        self.apply_font()
        self.repaint_static_frames()

    def set_font_size(self, size):
        global FONT_SIZE
        FONT_SIZE = size
        self.apply_font()
        self.repaint_static_frames()

    def apply_theme(self):
        # root + future widgets
        self.root.configure(bg=BG_COLOR)
        # update global FONT tuple
        self.base_font = (FONT_FAMILY or "Courier", FONT_SIZE)
        global FONT
        FONT = self.base_font

    def apply_font(self):
        self.base_font = (FONT_FAMILY or "Courier", FONT_SIZE)
        global FONT
        FONT = self.base_font

    # Stub – repaint existing static frames if you like
    def repaint_static_frames(self):
        # loop through self.frames and configure backgrounds / fg where needed
        for f in self.frames.values():
            f.configure(bg=BG_COLOR)
            for child in f.winfo_children():
                try:
                    child.configure(bg=BG_COLOR, fg=FG_COLOR, font=FONT)
                except tk.TclError:
                    pass

                if isinstance(child, tk.OptionMenu):
                    child.configure(bg=BG_COLOR, fg=FG_COLOR, font=FONT, activebackground=OH_COLOR)
#===============================================================
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
        
        # Show menu on static frames; hide on dynamic ones
        if name in self.static_frames:
            self.root.config(menu=self.menubar)
        else:
            self.root.config(menu="")
    
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
            creator = app.get_user(group.created_by)
            listbox.insert(tk.END, f"{group.id}: {group.name} (created by {creator.username})")

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

    def labeled_entry(self, parent, label_text): 
        tk.Label(parent, text=label_text, bg=BG_COLOR, fg=FG_COLOR, font=FONT).pack()
        entry = tk.Entry(parent, bg=BG_COLOR, fg=FG_COLOR, font=FONT, insertbackground=FG_COLOR)
        entry.pack()
        return entry

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

        username_entry = self.labeled_entry(frame, "Username")
        first_name_entry = self.labeled_entry(frame, "First Name")
        last_name_entry = self.labeled_entry(frame, "Last Name")
        email_entry = self.labeled_entry(frame, "Email")

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

        name_entry = self.labeled_entry(frame, "Group Name")
        desc_entry = self.labeled_entry(frame, "Description")

        creator_var = tk.StringVar(frame)
        dropdown = tk.OptionMenu(frame, creator_var, "")
        dropdown.config(bg=BG_COLOR, fg=FG_COLOR, font=FONT, activebackground=OH_COLOR, highlightthickness=0)
        
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
            if not selected:
                return

            group_id = int(selected.split(":")[0])
            members = app.get_group_members(group_id)

            if members:
                confirm = messagebox.askyesno(
                    "Confirm Deletion",
                    "This group has members. Deleting it will also remove all expenses and shares.\nAre you sure you want to continue?"
                )
                if not confirm:
                    return

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
        member_dropdown.config(bg=BG_COLOR, fg=FG_COLOR, activebackground=OH_COLOR, font=FONT, highlightthickness=0)

        tk.Label(frame, text="Group Members", bg=BG_COLOR, fg=FG_COLOR, font=FONT).pack()
        member_dropdown.pack()

        tk.Button(frame, text="Manage Members", command =lambda: self.open_dynamic_frame("add_users", group_id=group_id),
                  bg=BG_COLOR, fg=FG_COLOR, font=FONT).pack(pady=5)
        
        # Show and manage expenses

        expense_ids = [] # Local list to track hidden expense IDs
        def load_expenses_listbox(listbox, group_id):
            listbox.delete(0, tk.END)
            expense_ids.clear()

            expenses = app.get_group_expenses(group_id)
            if expenses:
                def format(text, width):
                    return (text[:width - 1] + '…') if len(text) > width else text.ljust(width)

                for expense in expenses:
                    payer_user = app.get_user(expense.paid_by)
                    payer = format(payer_user.username, 11)
                    desc = format(expense.description, 11)
                    amount = f"{expense.amount:6.2f}€"

                    shares = app.get_expense_shares(expense.id)
                    unpaid = sum(share.amount for share in shares if not share.is_paid)
                    
                    owed_summary = f"{payer} is owed:" if unpaid > 0 else ""
                    owed_total = f"{unpaid:6.2f}€" if unpaid > 0 else ""

                    display = f" {expense.date}  {desc} | {payer} paid: {amount} | {owed_summary} {owed_total}"
                    listbox.insert(tk.END, display)
                    expense_ids.append(expense.id)

        def open_create_expense():
            if not app.get_group_members(group_id):
                messagebox.showerror(
                    "Error",
                    "Group has no members - add users first."
                )
                return
            self.open_dynamic_frame("create_expense", group_id=group_id)

        def delete_selected_expense():
            selected = self.expenses_listbox.curselection()
            if not selected:
                return
            idx = int(selected[0])
            expense_id = expense_ids[idx]

            if messagebox.askyesno("Confirm", "Delete this expense and all its shares?"):
                if app.delete_expense(expense_id):
                    messagebox.showinfo("Deleted", "Expense deleted.")
                    load_expenses_listbox(self.expenses_listbox, group_id)
                else:
                    messagebox.showerror("Error", "Could not delete expense.")

        tk.Label(frame, text="All Expenses", bg=BG_COLOR, fg=FG_COLOR, font=FONT).pack(pady=10)

        self.expenses_listbox = tk.Listbox(frame, width=85, bg=BG_COLOR, fg=FG_COLOR, font=FONT)
        self.expenses_listbox.pack(pady=10)
        load_expenses_listbox(self.expenses_listbox, group_id)

        button_row = tk.Frame(frame, bg=BG_COLOR)
        button_row.pack(pady=10, padx=35, fill="x")

        # Left side container
        left_buttons = tk.Frame(button_row, bg=BG_COLOR)
        left_buttons.pack(side="left")

        # Right side container
        right_buttons = tk.Frame(button_row, bg=BG_COLOR)
        right_buttons.pack(side="right")

        tk.Button(left_buttons, text="New Expense", command=open_create_expense,
                bg=BG_COLOR, fg=FG_COLOR, font=FONT).pack(side="left", padx=5)
        tk.Button(left_buttons, text="Delete Selected", command=delete_selected_expense,
                bg=BG_COLOR, fg=FG_COLOR, font=FONT).pack(side="left", padx=5)
        tk.Button(right_buttons, text="Back", command=lambda: self.show_frame("all_groups"),
                bg=BG_COLOR, fg=FG_COLOR, font=FONT).pack(side="right", padx=5)
    
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

    def build_create_expense_frame(self, group_id=None, **kwargs):
        frame = tk.Frame(self.root, bg=BG_COLOR)

        # ---------- Data ----------
        group   = app.get_expense_group(group_id)
        members = app.get_group_members(group_id)

        tk.Label(frame, text=f"New Expense for '{group.name}'",
                bg=BG_COLOR, fg=FG_COLOR, font=FONT).pack(pady=10)

        description_entry = self.labeled_entry(frame, "Description")
        amount_entry      = self.labeled_entry(frame, "Total Amount (€)")

        # payer dropdown -------------------------------------------------
        payer_labels = [f"{u.username} ({u.first_name} {u.last_name})" for u in members]
        payer_var = tk.StringVar(frame); payer_var.set(payer_labels[0])
        label_to_uid = {label: u.id for label, u in zip(payer_labels, members)}

        tk.Label(frame, text="Paid by", bg=BG_COLOR, fg=FG_COLOR, font=FONT).pack()
        payer_dropdown = tk.OptionMenu(frame, payer_var, *payer_labels)
        payer_dropdown.config(bg=BG_COLOR, fg=FG_COLOR, activebackground=OH_COLOR, font=FONT, highlightthickness=0)
        payer_dropdown.pack(pady=5)
        # ------------- Split mode ---------------------------------------
        split_mode = tk.StringVar(value="even")   # "even" or "custom"
        tk.Frame(frame, bg=BG_COLOR).pack()  # spacer
        radio_row = tk.Frame(frame, bg=BG_COLOR)
        radio_row.pack()
        tk.Radiobutton(radio_row, text="Even split", variable=split_mode,
                    value="even", bg=BG_COLOR, fg=FG_COLOR,
                    selectcolor=BG_COLOR, command=lambda: toggle_custom(False)).pack(side="left")
        tk.Radiobutton(radio_row, text="Custom split", variable=split_mode,
                    value="custom", bg=BG_COLOR, fg=FG_COLOR,
                    selectcolor=BG_COLOR, command=lambda: toggle_custom(True)).pack(side="left", padx=10)

        # percent / amount toggle (only in custom mode)
        amount_type = tk.StringVar(value="amount")  # "amount" or "percent"
        type_row = tk.Frame(frame, bg=BG_COLOR)
        tk.Radiobutton(type_row, text="Amount",  variable=amount_type,
                    value="amount",  bg=BG_COLOR, fg=FG_COLOR,
                    selectcolor=BG_COLOR).pack(side="left")
        tk.Radiobutton(type_row, text="Percent", variable=amount_type,
                    value="percent", bg=BG_COLOR, fg=FG_COLOR,
                    selectcolor=BG_COLOR).pack(side="left", padx=10)

        # ------------- Members list -------------------------------------
        members_frame = tk.Frame(frame, bg=BG_COLOR)
        members_frame.pack(pady=5)
        check_vars, entry_vars = {}, {}

        def format(text, width):
            return (text[:width - 1] + '…') if len(text) > width else text.ljust(width)
        
        for u in members:
            username = format(u.username, 10)
            row = tk.Frame(members_frame, bg=BG_COLOR)
            row.pack(anchor="w")
            chk_var = tk.BooleanVar(value=True)
            ent_var = tk.StringVar(value="")
            tk.Checkbutton(row, text=username, variable=chk_var, width=15, anchor="w",
                        bg=BG_COLOR, fg=FG_COLOR, selectcolor=BG_COLOR,
                        command=lambda v=chk_var,e=ent_var: e.set("" if v.get() else ""))\
                        .pack(side="left")
            ent = tk.Entry(row, textvariable=ent_var, width=8,
                        bg=BG_COLOR, fg=FG_COLOR, insertbackground=FG_COLOR, state="disabled")
            ent.pack(side="left", padx=5)
            check_vars[u.id] = chk_var
            entry_vars[u.id] = (ent_var, ent)

        # helper to toggle entry widgets
        def toggle_custom(show):
            for uid, (var, entry) in entry_vars.items():
                entry.configure(state="normal" if show else "disabled")
            type_row.pack_forget()
            if show:
                type_row.pack()

        # ---------- submit ----------------------------------------------
        def submit_expense():
            desc = description_entry.get().strip()
            amt_str = amount_entry.get().strip()
            payer_id = label_to_uid[payer_var.get()]

            if not desc:
                messagebox.showerror("Validation", "Description is required."); return
            try:
                amount = float(amt_str)
            except ValueError:
                messagebox.showerror("Validation", "Amount must be numeric."); return
            if amount <= 0:
                messagebox.showerror("Validation", "Amount must be positive."); return

            # build shares_dict ----------------------
            shares_dict = {}
            if split_mode.get() == "even":
                shares_dict = {uid: 0 for uid in check_vars if check_vars[uid].get()}
            else:  # custom mode
                for uid in check_vars:
                    if not check_vars[uid].get():    # box unticked
                        continue
                    val = entry_vars[uid][0].get().strip()
                    if not val:
                        messagebox.showerror("Validation", "Custom split missing values."); return
                    try:
                        val_f = float(val)
                    except ValueError:
                        messagebox.showerror("Validation", "Custom values must be numeric."); return
                    shares_dict[uid] = val_f

                # validate totals --------------------
                total_input = sum(shares_dict.values())
                if amount_type.get() == "amount" and abs(total_input - amount) > 1e-2:
                    messagebox.showerror("Validation", "Shares must sum to total amount."); return
                if amount_type.get() == "percent" and abs(total_input - 100) > 1e-2:
                    messagebox.showerror("Validation", "Percent split must add up to 100%."); return

            # create expense -------------------------
            expense_id = app.create_expense_with_shares(
                description=desc,
                amount=amount,
                paid_by=payer_id,
                group_id=group_id,
                shares_dict=shares_dict
            )
            if not expense_id:
                messagebox.showerror("Error", "Failed to create expense."); return

            messagebox.showinfo("Success", "Expense added!")
            self.open_dynamic_frame("selected_group", group_id=group_id)

        tk.Button(frame, text="Add Expense", command=submit_expense,
                bg=BG_COLOR, fg=FG_COLOR, font=FONT).pack(pady=10)
        tk.Button(frame, text="Back",
                command=lambda: self.open_dynamic_frame("selected_group", group_id=group_id),
                bg=BG_COLOR, fg=FG_COLOR, font=FONT).pack(pady=5)

        return frame


# Start app
if __name__ == "__main__":
    root = tk.Tk()
    app_ui = ExpenseManagerApp(root)
    root.mainloop()
