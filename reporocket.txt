import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import subprocess
import requests
import time

class RepoTinker:
    def __init__(self, root):
        self.root = root
        self.root.title("Repo-Rocket")
        self.root.geometry("1000x600")
        self.root.configure(bg="#000000")

        # Variables for all fields
        self.repo_name = tk.StringVar()
        self.access_token = tk.StringVar()
        self.repo_url = tk.StringVar()
        self.branch_name = tk.StringVar()
        self.description = tk.StringVar()
        self.template = tk.StringVar(value="empty")
        self.is_private = tk.BooleanVar()
        self.ssh_key_path = tk.StringVar()
        self.ssh_key_content = tk.StringVar()
        self.clone_command = tk.StringVar()
        self.remote_name = tk.StringVar()
        self.username = tk.StringVar()
        self.email = tk.StringVar()
        self.last_commit = tk.StringVar()
        self.notes = tk.StringVar()
        self.new_directory = tk.StringVar()
        self.selected_file = None
        self.commit_message = tk.StringVar(value="Update via Repo-Rocket")
        self.repo_status = tk.StringVar(value="Status: Not Loaded")

        # Session credentials
        self.username_val = None
        self.access_token_val = None
        self.repo_owner = None

        # Reference to the Notes tk.Text widget
        self.notes_text_widget = None

        # Load logo
        self.logo = None
        logo_path = os.path.join(os.path.dirname(__file__), "logo.png")
        try:
            if os.path.exists(logo_path):
                self.logo = tk.PhotoImage(file=logo_path)
            else:
                messagebox.showwarning("Logo Missing", "logo.png not found! Place a 300x100px PNG in the same directory as repotinker.py.")
        except tk.TclError as e:
            messagebox.showerror("Logo Error", f"Failed to load logo.png: {e}\nEnsure it's a 300x100px PNG file.")

        # GUI Setup
        self.setup_ui()

    def setup_ui(self):
        # Styles for black backgrounds
        style = ttk.Style()
        style.configure("Black.TFrame", background="#000000")
        style.configure("Black.TLabelframe", background="#000000", foreground="#ffeb3b")
        style.configure("Black.TLabelframe.Label", background="#000000", foreground="#ffeb3b")
        style.configure("TLabel", background="#000000", foreground="#ffeb3b")
        style.configure("TEntry", fieldbackground="#333333", foreground="#ffffff")
        style.configure("TCombobox", fieldbackground="#333333", foreground="#ffffff")
        style.configure("TButton", background="#4CAF50", foreground="#ffffff")
        style.map("TButton", background=[("active", "#45a049")])
        style.configure("StatusClean.TLabel", background="#000000", foreground="#4CAF50")
        style.configure("StatusPending.TLabel", background="#000000", foreground="#ffeb3b")
        style.configure("StatusError.TLabel", background="#000000", foreground="#ff0000")

        # Create context menu for right-click paste
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Paste", command=self.paste_from_clipboard)

        # Main Frame
        main_frame = ttk.Frame(self.root, padding=10, style="Black.TFrame")
        main_frame.pack(fill="both", expand=True)

        # Left: Form Frame (Scrollable)
        form_frame = ttk.LabelFrame(main_frame, text="Create Repo", padding=10, style="Black.TLabelframe")
        form_frame.pack(side="left", fill="y", padx=5)

        # Create a canvas and scrollbar for scrolling
        canvas = tk.Canvas(form_frame, bg="#000000", highlightthickness=0)
        scrollbar = ttk.Scrollbar(form_frame, orient="vertical", command=canvas.yview)
        inner_form_frame = ttk.Frame(canvas, style="Black.TFrame")

        # Configure the canvas
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Add the inner frame to the canvas
        canvas_frame = canvas.create_window((0, 0), window=inner_form_frame, anchor="nw")

        # Update scroll region when the inner frame size changes
        def configure_scroll_region(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        inner_form_frame.bind("<Configure>", configure_scroll_region)

        # Update canvas width when the form frame resizes
        def configure_canvas_width(event):
            canvas.itemconfig(canvas_frame, width=event.width)

        canvas.bind("<Configure>", configure_canvas_width)

        # Add logo if it exists
        if self.logo:
            logo_label = tk.Label(inner_form_frame, image=self.logo, bg="#000000")
            logo_label.pack(pady=5)

        fields = [
            ("Repo Name *", self.repo_name, "entry"),
            ("Access Token *", self.access_token, "entry", True),
            ("Repo URL", self.repo_url, "entry"),
            ("Branch Name", self.branch_name, "entry"),
            ("Description", self.description, "text"),
            ("Template", self.template, "combo", ["empty", "python", "nodejs"]),
            ("Private Repository", self.is_private, "check"),
            ("SSH Key Path", self.ssh_key_path, "entry"),
            ("SSH Key Content", self.ssh_key_content, "text"),
            ("Clone Command", self.clone_command, "entry"),
            ("Remote Name", self.remote_name, "entry"),
            ("Username", self.username, "entry"),
            ("Email", self.email, "entry"),
            ("Last Commit Hash", self.last_commit, "entry"),
            ("Notes", self.notes, "text"),
            ("New Directory Path *", self.new_directory, "entry"),
        ]

        for label, var, widget_type, *extra in fields:
            ttk.Label(inner_form_frame, text=label, style="TLabel").pack(anchor="w")
            if widget_type == "entry":
                entry = ttk.Entry(inner_form_frame, textvariable=var, width=30, style="TEntry", show="*" if extra and extra[0] else "")
                entry.pack(fill="x", pady=2)
                entry.bind("<Button-3>", self.show_context_menu)
            elif widget_type == "text":
                text = tk.Text(inner_form_frame, height=3, width=30, bg="#333333", fg="#ffffff", insertbackground="white")
                text.pack(fill="x", pady=2)
                text.bind("<Button-3>", self.show_context_menu)
                if label == "Notes":
                    self.notes_text_widget = text
            elif widget_type == "combo":
                ttk.Combobox(inner_form_frame, textvariable=var, values=extra[0], state="readonly", style="TCombobox").pack(fill="x", pady=2)
            elif widget_type == "check":
                ttk.Checkbutton(inner_form_frame, variable=var).pack(anchor="w", pady=2)

        ttk.Button(inner_form_frame, text="Launch Repo", command=self.launch_repo, style="TButton").pack(side="top", pady=5)
        ttk.Button(inner_form_frame, text="Clear Form", command=self.clear_form, style="TButton").pack(side="top", pady=5)
        # New: Add "Show Git Commands" button
        ttk.Button(inner_form_frame, text="Show Git Commands", command=self.show_git_commands, style="TButton").pack(side="top", pady=5)

        # Middle: Editor Frame
        editor_frame = ttk.LabelFrame(main_frame, text="Edit Repo", padding=10, style="Black.TLabelframe")
        editor_frame.pack(side="left", fill="both", expand=True, padx=5)

        ttk.Label(editor_frame, text="Repo Directory:", style="TLabel").pack(anchor="w")
        self.dir_entry = ttk.Entry(editor_frame, textvariable=self.new_directory, width=50, style="TEntry")
        self.dir_entry.pack(fill="x", pady=2)
        self.dir_entry.bind("<Button-3>", self.show_context_menu)
        ttk.Button(editor_frame, text="Browse", command=self.browse_dir, style="TButton").pack(pady=2)

        self.status_label = ttk.Label(editor_frame, textvariable=self.repo_status, style="StatusClean.TLabel")
        self.status_label.pack(anchor="w", pady=2)

        ttk.Label(editor_frame, text="Files:", style="TLabel").pack(anchor="w")
        self.file_list = tk.Listbox(editor_frame, height=5, bg="#333333", fg="#ffffff", selectbackground="#4CAF50")
        self.file_list.pack(fill="x", pady=2)
        self.file_list.bind("<<ListboxSelect>>", self.load_file)

        self.text_editor = tk.Text(editor_frame, height=10, bg="#333333", fg="#ffffff", insertbackground="white")
        self.text_editor.pack(fill="both", expand=True, pady=2)
        self.text_editor.bind("<Button-3>", self.show_context_menu)

        ttk.Label(editor_frame, text="Commit Message:", style="TLabel").pack(anchor="w")
        self.commit_entry = ttk.Entry(editor_frame, textvariable=self.commit_message, width=50, style="TEntry")
        self.commit_entry.pack(fill="x", pady=2)
        self.commit_entry.bind("<Button-3>", self.show_context_menu)

        btn_frame = ttk.Frame(editor_frame, style="Black.TFrame")
        btn_frame.pack(fill="x")
        ttk.Button(btn_frame, text="Save File", command=self.save_file, style="TButton").pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Commit & Push", command=self.commit_push, style="TButton").pack(side="left", padx=5)

        # Right Side: Commit History Frame
        history_frame = ttk.LabelFrame(main_frame, text="Commit History", padding=5, style="Black.TLabelframe")
        history_frame.pack(side="right", fill="y", padx=5)
        self.commit_history = tk.Listbox(history_frame, width=30, height=15, bg="#333333", fg="#ffeb3b", selectbackground="#4CAF50")
        self.commit_history.pack(fill="y")

    # New: Show Git commands in a new window
    def show_git_commands(self):
        # Create a new Toplevel window
        git_window = tk.Toplevel(self.root)
        git_window.title("Common Git Commands")
        git_window.geometry("600x500")
        git_window.configure(bg="#000000")

        # Create a frame for the text and scrollbar
        text_frame = ttk.Frame(git_window, style="Black.TFrame")
        text_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Create a Text widget with a scrollbar
        text_scroll = ttk.Scrollbar(text_frame, orient="vertical")
        text_area = tk.Text(
            text_frame,
            wrap="word",
            height=25,
            width=60,
            bg="#333333",
            fg="#ffeb3b",
            insertbackground="white",
            yscrollcommand=text_scroll.set,
            state="normal"
        )
        text_scroll.config(command=text_area.yview)
        text_scroll.pack(side="right", fill="y")
        text_area.pack(side="left", fill="both", expand=True)

        # Git commands content
        git_commands = (
            "**Getting and Creating Projects:**\n"
            "* `git init`: Create a new Git repository.\n"
            "* `git clone <repository_url>`: Clone a repository into a new directory.\n\n"

            "**Basic Snapshotting:**\n"
            "* `git add <file(s)>`: Add file contents to the index.\n"
            "* `git commit -m \"<message>\"`: Record changes to the repository.\n"
            "* `git status`: Show the working tree status.\n"
            "* `git diff`: Show changes between commits, commit and working tree, etc.\n"
            "* `git diff --staged`: Show changes between index and last commit.\n"
            "* `git restore <file(s)>`: Restore working tree files.\n"
            "* `git restore --staged <file(s)>`: Unstage file(s).\n"
            "* `git rm <file(s)>`: Remove files from the working tree and index.\n"
            "* `git mv <old_file> <new_file>`: Move or rename a file, a directory, or a symlink.\n\n"

            "**Branching and Merging:**\n"
            "* `git branch`: List, create, or delete branches.\n"
            "* `git branch <branch_name>`: Create a new branch.\n"
            "* `git branch -d <branch_name>`: Delete a branch.\n"
            "* `git checkout <branch_name>`: Switch branches or restore working tree files.\n"
            "* `git checkout -b <branch_name>`: Create and switch to a new branch.\n"
            "* `git merge <branch_name>`: Join two or more development histories together.\n"
            "* `git mergetool`: Run merge conflict resolution tools to resolve merge conflicts.\n"
            "* `git log --graph --oneline --decorate --all`: Display commits as a graph.\n"
            "* `git stash`: Temporarily save modified, tracked files.\n"
            "* `git stash pop`: Restore saved stash.\n"
            "* `git rebase <branch_name>`: Reapply commits on top of another base tip.\n\n"

            "**Sharing and Updating Projects:**\n"
            "* `git remote`: Manage set of tracked repositories.\n"
            "* `git remote add <name> <url>`: Add a remote repository.\n"
            "* `git remote -v`: View remote repositories.\n"
            "* `git fetch <remote>`: Download objects and refs from another repository.\n"
            "* `git pull <remote> <branch>`: Fetch from and integrate with another repository or a local branch.\n"
            "* `git push <remote> <branch>`: Update remote refs along with associated objects.\n\n"

            "**Inspection and History:**\n"
            "* `git log`: Show commit logs.\n"
            "* `git log --oneline`: Show a condensed one-line version of commits.\n"
            "* `git log -p`: Show the patch introduced with each commit.\n"
            "* `git log --stat`: Show statistics of changes in each commit.\n"
            "* `git show <commit>`: Show various types of objects.\n"
            "* `git tag`: Create, list, delete or verify a tag object signed with GPG.\n"
            "* `git tag -a <tag_name> -m \"<message>\"`: Create an annotated tag.\n"
            "* `git tag <tag_name>`: Create a lightweight tag.\n"
            "* `git reset <commit>`: Reset current HEAD to the specified state.\n"
            "* `git reset --hard <commit>`: Reset working directory and index to match. (Use with caution!)\n"
            "* `git reset --soft <commit>`: Resets the head branch to the commit and preserves the staging area.\n"
            "* `git reset --mixed <commit>`: Resets the head branch to the commit and resets the staging area. This is the default reset mode.\n"
            "* `git revert <commit>`: Create a new commit that undoes the changes made in a previous commit.\n"
            "* `git blame <file>`: Show what revision and author last modified each line of a file.\n"
            "* `git bisect`: Use binary search to find the commit that introduced a bug.\n"
            "* `git reflog`: Manage reflog information.\n\n"

            "**Configuration:**\n"
            "* `git config --global user.name \"<name>\"`: Set your name.\n"
            "* `git config --global user.email \"<email>\"`: Set your email.\n"
            "* `git config --global --list`: List all git configuration settings.\n"
            "* `git config --global core.editor <editor>`: Set your default editor.\n\n"

            "**Advanced Commands:**\n"
            "* `git submodule`: Initialize, update or inspect submodules.\n"
            "* `git filter-branch`: Rewrite branches. (Use with caution!)\n"
            "* `git cherry-pick <commit>`: Apply the changes introduced by some existing commits.\n"
            "* `git clean`: Remove untracked files from the working tree.\n\n"

            "This list covers the most frequently used Git commands.\n"
        )

        # Insert the content into the Text widget
        text_area.insert(tk.END, git_commands)

        # Make the Text widget read-only
        text_area.config(state="disabled")

    def show_context_menu(self, event):
        self.context_menu.post(event.x_root, event.y_root)

    def paste_from_clipboard(self):
        try:
            focused_widget = self.root.focus_get()
            if isinstance(focused_widget, (ttk.Entry, tk.Text)):
                focused_widget.event_generate("<<Paste>>")
        except tk.TclError:
            pass

    def update_commit_history(self):
        self.commit_history.delete(0, tk.END)
        dir_path = self.new_directory.get()
        if not dir_path or not os.path.isdir(dir_path):
            self.commit_history.insert(tk.END, "No directory selected")
            return

        try:
            result = subprocess.run(
                ['git', 'log', '--pretty=format:%h|%an|%ad|%s', '-n', '5'],
                cwd=dir_path,
                capture_output=True,
                text=True,
                check=True
            )
            commits = result.stdout.strip().split('\n')
            if not commits or commits == ['']:
                self.commit_history.insert(tk.END, "No commits found")
                return

            for commit in commits:
                if commit:
                    hash_val, author, date, message = commit.split('|', 3)
                    message = (message[:20] + '...') if len(message) > 20 else message
                    display = f"[{date}] {message} ({hash_val}) by {author}"
                    self.commit_history.insert(tk.END, display)
        except subprocess.CalledProcessError:
            self.commit_history.insert(tk.END, "No history available")

    def launch_repo(self):
        repo_name = self.repo_name.get()
        access_token = self.access_token.get()
        new_directory = self.new_directory.get()

        if not repo_name or not access_token or not new_directory:
            messagebox.showerror("Error", "Repo Name, Access Token, and New Directory are required!")
            return

        self.username_val = self.username.get() or "unknown"
        self.access_token_val = access_token

        headers = {'Authorization': f'token {access_token}', 'Accept': 'application/vnd.github.v3+json'}
        data = {
            'name': repo_name,
            'description': self.description.get(),
            'private': self.is_private.get()
        }

        try:
            os.makedirs(new_directory, exist_ok=True)
            with open(os.path.join(new_directory, 'README.md'), 'w') as f:
                f.write(f"# {repo_name}\nCreated by Repo-Rocket on {time.ctime()}.")

            templates = {
                'python': [
                    ('README.md', f"# {repo_name}\nA Python project template by Repo-Rocket."),
                    ('.gitignore', "__pycache__\n*.pyc\nvenv/")
                ],
                'nodejs': [
                    ('README.md', f"# {repo_name}\nA Node.js project template by Repo-Rocket."),
                    ('.gitignore', "node_modules/\n*.log")
                ]
            }
            template = self.template.get()
            if template in templates:
                for filename, content in templates[template]:
                    with open(os.path.join(new_directory, filename), 'w') as f:
                        f.write(content)

            subprocess.run(['git', 'init', '--initial-branch=main'], cwd=new_directory, check=True)
            subprocess.run(['git', 'add', '.'], cwd=new_directory, check=True)
            subprocess.run(['git', 'commit', '-m', 'Initial commit by RepoTinker'], cwd=new_directory, check=True)

            response = requests.post('https://api.github.com/user/repos', headers=headers, json=data)
            response.raise_for_status()
            repo_data = response.json()

            self.repo_owner = repo_data['owner']['login']
            push_url = f"https://{self.access_token_val}@github.com/{self.repo_owner}/{repo_name}.git"
            subprocess.run(['git', 'remote', 'add', 'origin', push_url], cwd=new_directory, check=True)

            # Create <repo_name>_details.txt with detailed repo info
            notes_content = self.notes_text_widget.get("1.0", tk.END).strip() if self.notes_text_widget else "None"
            description = self.description.get() or "N/A"
            branch_name = self.branch_name.get() or "main"
            ssh_key_path = self.ssh_key_path.get() or "Not set"
            ssh_key_content = self.ssh_key_content.get() or "Not set"
            remote_name = self.remote_name.get() or "origin"
            username = self.username.get() or "Not set"
            email = self.email.get() or "Not set"
            last_commit = self.last_commit.get() or "N/A"
            github_url = repo_data['html_url']
            clone_command = f"git clone {github_url}.git"
            access_token_display = f"***HIDDEN*** (Original: {len(access_token)} chars)"

            repo_details = (
                f"RepoTinker - Repository Details:\n"
                f"Name: {repo_name}\n"
                f"URL: {github_url}\n"
                f"Branch Name: {branch_name}\n"
                f"Access Token: {access_token_display}\n"
                f"Description: {description}\n"
                f"Template: {template}\n"
                f"Private: {self.is_private.get()}\n"
                f"SSH Key Path: {ssh_key_path}\n"
                f"SSH Key Content: {ssh_key_content}\n"
                f"Clone Command: {clone_command}\n"
                f"Remote Name: {remote_name}\n"
                f"Username: {username}\n"
                f"Email: {email}\n"
                f"Last Commit Hash: {last_commit}\n"
                f"Notes: {notes_content}\n"
                f"GitHub Created URL: {github_url}\n"
                f"Local Directory: {new_directory}\n"
                f"Git Status: Your new directory is a Git repo, synced with GitHub—edit, commit, and push as needed!\n"
            )
            details_filename = f"{repo_name}_details.txt"
            with open(os.path.join(new_directory, details_filename), 'w') as f:
                f.write(repo_details)

            # Add the new file to the Git commit and push
            subprocess.run(['git', 'add', details_filename], cwd=new_directory, check=True)
            subprocess.run(['git', 'commit', '-m', f'Add {details_filename} with creation details'], cwd=new_directory, check=True)
            subprocess.run(['git', 'push', 'origin', 'main'], cwd=new_directory, check=True)
            subprocess.run(['git', 'remote', 'set-url', 'origin', repo_data['clone_url']], cwd=new_directory, check=True)

            messagebox.showinfo("Success", f"Repo launched at {repo_data['html_url']}!\nDir: {new_directory}")
            self.load_files()
            self.update_commit_history()

        except (requests.RequestException, subprocess.CalledProcessError, OSError) as e:
            error_msg = e.response.json().get('message', 'Unknown error') if isinstance(e, requests.RequestException) else str(e)
            messagebox.showerror("Error", f"Failed to launch repo: {error_msg}")

    def browse_dir(self):
        dir_path = filedialog.askdirectory(initialdir=os.path.expanduser("~"), title="Select Repo Directory")
        if dir_path:
            self.new_directory.set(dir_path)
            self.load_files()
            self.update_commit_history()

    def load_files(self):
        dir_path = self.new_directory.get()
        if not dir_path or not os.path.isdir(dir_path):
            messagebox.showerror("Error", "Select a valid directory!")
            return
        self.file_list.delete(0, tk.END)
        for root, _, files in os.walk(dir_path):
            for file in files:
                if file != ".git":
                    rel_path = os.path.relpath(os.path.join(root, file), dir_path)
                    self.file_list.insert(tk.END, rel_path)
        self.update_repo_status()

    def load_file(self, event):
        selection = self.file_list.curselection()
        if not selection:
            return
        file_name = self.file_list.get(selection[0])
        self.selected_file = os.path.join(self.new_directory.get(), file_name)
        try:
            with open(self.selected_file, "r") as f:
                content = f.read()
            self.text_editor.delete("1.0", tk.END)
            self.text_editor.insert("1.0", content)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file: {e}")

    def save_file(self):
        if not self.selected_file:
            messagebox.showerror("Error", "No file selected!")
            return
        try:
            with open(self.selected_file, "w") as f:
                f.write(self.text_editor.get("1.0", tk.END).strip())
            messagebox.showinfo("Success", "File saved!")
            self.update_repo_status()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file: {e}")

    def commit_push(self):
        dir_path = self.new_directory.get()
        if not dir_path or not os.path.isdir(dir_path):
            messagebox.showerror("Error", "Select a valid directory!")
            return
        if not self.access_token_val or not self.repo_owner:
            messagebox.showerror("Error", "Launch a repo first to set credentials!")
            return

        try:
            result = subprocess.run(['git', 'status', '--porcelain'], cwd=dir_path, capture_output=True, text=True, check=True)
            if not result.stdout:
                messagebox.showinfo("Info", "No changes to commit!")
                return

            repo_name = self.repo_name.get()
            push_url = f"https://{self.access_token_val}@github.com/{self.repo_owner}/{repo_name}.git"
            subprocess.run(['git', 'remote', 'set-url', 'origin', push_url], cwd=dir_path, check=True)
            subprocess.run(['git', 'add', '.'], cwd=dir_path, check=True)
            commit_msg = self.commit_message.get().strip()
            if not commit_msg:
                commit_msg = "Update via RepoTinker"
            subprocess.run(['git', 'commit', '-m', commit_msg], cwd=dir_path, check=True)
            subprocess.run(['git', 'push', 'origin', 'main'], cwd=dir_path, check=True)
            clean_url = f"https://github.com/{self.repo_owner}/{repo_name}.git"
            subprocess.run(['git', 'remote', 'set-url', 'origin', clean_url], cwd=dir_path, check=True)

            messagebox.showinfo("Success", "Changes committed and pushed to GitHub!")
            self.update_repo_status()
            self.update_commit_history()
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Git operation failed: {e.stderr}")

    def update_repo_status(self):
        dir_path = self.new_directory.get()
        if not dir_path or not os.path.isdir(dir_path):
            self.repo_status.set("Status: Not Loaded")
            self.status_label.configure(style="StatusError.TLabel")
            return

        try:
            result = subprocess.run(['git', 'status', '--porcelain'], cwd=dir_path, capture_output=True, text=True, check=True)
            if result.stdout:
                self.repo_status.set("Status: Changes Pending")
                self.status_label.configure(style="StatusPending.TLabel")
            else:
                self.repo_status.set("Status: Clean")
                self.status_label.configure(style="StatusClean.TLabel")
        except subprocess.CalledProcessError:
            self.repo_status.set("Status: Error (Not a Git Repo)")
            self.status_label.configure(style="StatusError.TLabel")

    def clear_form(self):
        for var in [self.repo_name, self.access_token, self.repo_url, self.branch_name, self.description,
                    self.template, self.is_private, self.ssh_key_path, self.ssh_key_content, self.clone_command,
                    self.remote_name, self.username, self.email, self.last_commit, self.notes, self.new_directory]:
            var.set("")
        self.template.set("empty")
        self.is_private.set(False)
        self.text_editor.delete("1.0", tk.END)
        self.file_list.delete(0, tk.END)
        self.selected_file = None
        self.username_val = None
        self.access_token_val = None
        self.repo_owner = None
        self.commit_message.set("Update via Repo-Rocket")
        self.repo_status.set("Status: Not Loaded")
        self.status_label.configure(style="StatusError.TLabel")
        if self.notes_text_widget:
            self.notes_text_widget.delete("1.0", tk.END)
        self.commit_history.delete(0, tk.END)
        self.commit_history.insert(tk.END, "No directory selected")
        messagebox.showinfo("Info", "Form and credentials cleared!")

if __name__ == "__main__":
    root = tk.Tk()
    app = RepoTinker(root)
    root.mainloop()
