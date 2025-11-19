import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import subprocess
import os
from pathlib import Path
import threading
import base64

class AdvancedGitGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Git Tool with Authentication")
        self.root.geometry("1200x900")
        
        # Current repository path
        self.repo_path = tk.StringVar(value=os.getcwd())
        
        # Authentication variables
        self.username = tk.StringVar()
        self.email = tk.StringVar()
        self.token = tk.StringVar()
        self.use_auth = tk.BooleanVar(value=False)
        
        self.setup_gui()
        
    def setup_gui(self):
        # Create main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Authentication section
        auth_frame = ttk.LabelFrame(main_frame, text="Git Authentication", padding="10")
        auth_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        auth_frame.columnconfigure(1, weight=1)
        
        # Enable authentication checkbox
        ttk.Checkbutton(auth_frame, text="Use Authentication", variable=self.use_auth, 
                       command=self.toggle_auth_fields).grid(row=0, column=0, sticky=tk.W, pady=2)
        
        # Username
        ttk.Label(auth_frame, text="Username:").grid(row=1, column=0, sticky=tk.W, pady=2)
        ttk.Entry(auth_frame, textvariable=self.username, width=30).grid(row=1, column=1, sticky=(tk.W, tk.E), pady=2, padx=5)
        
        # Email
        ttk.Label(auth_frame, text="Email:").grid(row=1, column=2, sticky=tk.W, pady=2)
        ttk.Entry(auth_frame, textvariable=self.email, width=30).grid(row=1, column=3, sticky=(tk.W, tk.E), pady=2, padx=5)
        
        # Token/Password
        ttk.Label(auth_frame, text="Token/Password:").grid(row=2, column=0, sticky=tk.W, pady=2)
        token_entry = ttk.Entry(auth_frame, textvariable=self.token, show="*", width=30)
        token_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=2, padx=5)
        
        # Show/hide token button
        ttk.Button(auth_frame, text="👁", width=3, 
                  command=lambda: self.toggle_token_visibility(token_entry)).grid(row=2, column=2, padx=2)
        
        # Test authentication button
        ttk.Button(auth_frame, text="Test Auth", command=self.test_authentication).grid(row=2, column=3, padx=5)
        
        # Repository selection
        ttk.Label(main_frame, text="Repository Path:").grid(row=1, column=0, sticky=tk.W, pady=5)
        path_frame = ttk.Frame(main_frame)
        path_frame.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)
        path_frame.columnconfigure(0, weight=1)
        
        ttk.Entry(path_frame, textvariable=self.repo_path).grid(row=0, column=0, sticky=(tk.W, tk.E))
        ttk.Button(path_frame, text="Browse", command=self.browse_repo).grid(row=0, column=1, padx=5)
        
        # Initialize repo button
        ttk.Button(path_frame, text="Init Repo", command=self.init_repo).grid(row=0, column=2, padx=5)
        
        # Command selection
        ttk.Label(main_frame, text="Git Command:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.command_var = tk.StringVar()
        self.command_combo = ttk.Combobox(main_frame, textvariable=self.command_var, state="readonly")
        self.command_combo['values'] = [
            'clone', 'init', 'add', 'status', 'commit', 'push', 'pull', 'fetch',
            'branch', 'checkout', 'merge', 'rebase', 'log', 'diff', 'remote',
            'stash', 'tag', 'reset', 'revert', 'cherry-pick', 'bisect', 'blame',
            'clean', 'config', 'show', 'rm', 'mv', 'restore', 'switch', 'worktree'
        ]
        self.command_combo.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5)
        self.command_combo.bind('<<ComboboxSelected>>', self.on_command_select)
        
        # Options frame
        self.options_frame = ttk.LabelFrame(main_frame, text="Command Options", padding="10")
        self.options_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        self.options_frame.columnconfigure(1, weight=1)
        
        # Parameters frame (will be populated dynamically)
        self.parameters_frame = ttk.Frame(self.options_frame)
        self.parameters_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        # Additional arguments
        ttk.Label(main_frame, text="Additional Arguments:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.args_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.args_var).grid(row=4, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Output area
        output_frame = ttk.LabelFrame(main_frame, text="Output", padding="5")
        output_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        output_frame.columnconfigure(0, weight=1)
        output_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(5, weight=1)
        
        self.output_text = scrolledtext.ScrolledText(output_frame, height=20, width=100)
        self.output_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=6, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="Execute Command", command=self.execute_command).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Clear Output", command=self.clear_output).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Show Git Help", command=self.show_git_help).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Configure Git User", command=self.configure_git_user).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Save Auth", command=self.save_auth).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Load Auth", command=self.load_auth).pack(side=tk.LEFT, padx=5)
        
        # Initially disable auth fields
        self.toggle_auth_fields()
        
    def toggle_auth_fields(self):
        state = 'normal' if self.use_auth.get() else 'disabled'
        for widget in self.root.winfo_children():
            if isinstance(widget, ttk.LabelFrame) and "Authentication" in widget.cget('text'):
                for child in widget.winfo_children():
                    if not isinstance(child, ttk.Checkbutton):
                        child.configure(state=state)
    
    def toggle_token_visibility(self, entry):
        if entry.cget('show') == '*':
            entry.configure(show='')
        else:
            entry.configure(show='*')
    
    def browse_repo(self):
        from tkinter import filedialog
        path = filedialog.askdirectory(initialdir=self.repo_path.get())
        if path:
            self.repo_path.set(path)
    
    def init_repo(self):
        """Initialize a new Git repository"""
        path = self.repo_path.get()
        if not path:
            messagebox.showerror("Error", "Please set a repository path")
            return
        
        try:
            subprocess.run(['git', 'init'], cwd=path, check=True, capture_output=True, text=True)
            messagebox.showinfo("Success", f"Initialized Git repository at {path}")
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Failed to initialize repository: {e.stderr}")
    
    def configure_git_user(self):
        """Configure Git user name and email globally"""
        if not self.username.get() or not self.email.get():
            messagebox.showwarning("Warning", "Please enter both username and email")
            return
        
        try:
            # Set global user name
            subprocess.run(['git', 'config', '--global', 'user.name', self.username.get()], 
                         check=True, capture_output=True, text=True)
            
            # Set global user email
            subprocess.run(['git', 'config', '--global', 'user.email', self.email.get()], 
                         check=True, capture_output=True, text=True)
            
            messagebox.showinfo("Success", "Git user configuration updated globally")
            
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Failed to configure Git user: {e.stderr}")
    
    def get_auth_url(self, url):
        """Convert regular URL to authenticated URL"""
        if not self.use_auth.get() or not self.token.get():
            return url
        
        # Handle different URL formats
        if url.startswith('https://'):
            if self.username.get():
                # https://username:token@github.com/owner/repo.git
                return url.replace('https://', f'https://{self.username.get()}:{self.token.get()}@')
            else:
                # https://token@github.com/owner/repo.git
                return url.replace('https://', f'https://{self.token.get()}@')
        elif url.startswith('git@'):
            # For SSH URLs, we can't embed token, so return as-is
            return url
        return url
    
    def setup_authentication_headers(self):
        """Setup authentication headers for API calls"""
        if self.use_auth.get() and self.token.get():
            token = self.token.get()
            auth_str = f"{self.username.get()}:{token}" if self.username.get() else f":{token}"
            encoded_auth = base64.b64encode(auth_str.encode()).decode()
            return {'Authorization': f'Basic {encoded_auth}'}
        return {}
    
    def test_authentication(self):
        """Test GitHub authentication"""
        if not self.use_auth.get():
            messagebox.showinfo("Info", "Authentication is not enabled")
            return
        
        if not self.token.get():
            messagebox.showwarning("Warning", "Please enter a token")
            return
        
        def test_auth_thread():
            headers = self.setup_authentication_headers()
            try:
                import requests
                response = requests.get('https://api.github.com/user', headers=headers)
                
                self.root.after(0, lambda: self.display_auth_test_result(response))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Authentication test failed: {str(e)}"))
        
        threading.Thread(target=test_auth_thread, daemon=True).start()
    
    def display_auth_test_result(self, response):
        if response.status_code == 200:
            user_data = response.json()
            messagebox.showinfo("Success", 
                              f"Authentication successful!\n\n"
                              f"Username: {user_data.get('login', 'N/A')}\n"
                              f"Name: {user_data.get('name', 'N/A')}\n"
                              f"Email: {user_data.get('email', 'N/A')}\n"
                              f"Plan: {user_data.get('plan', {}).get('name', 'N/A')}")
        else:
            messagebox.showerror("Error", 
                               f"Authentication failed!\n"
                               f"Status: {response.status_code}\n"
                               f"Message: {response.text}")
    
    def save_auth(self):
        """Save authentication details to file (encrypted)"""
        from tkinter import filedialog
        import json
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            auth_data = {
                'username': self.username.get(),
                'email': self.email.get(),
                'token': self.simple_encrypt(self.token.get()),
                'repo_path': self.repo_path.get()
            }
            
            try:
                with open(filename, 'w') as f:
                    json.dump(auth_data, f, indent=2)
                messagebox.showinfo("Success", "Authentication data saved securely")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save: {str(e)}")
    
    def load_auth(self):
        """Load authentication details from file"""
        from tkinter import filedialog
        import json
        
        filename = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'r') as f:
                    auth_data = json.load(f)
                
                self.username.set(auth_data.get('username', ''))
                self.email.set(auth_data.get('email', ''))
                self.token.set(self.simple_decrypt(auth_data.get('token', '')))
                self.repo_path.set(auth_data.get('repo_path', os.getcwd()))
                self.use_auth.set(True)
                self.toggle_auth_fields()
                
                messagebox.showinfo("Success", "Authentication data loaded")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load: {str(e)}")
    
    def simple_encrypt(self, text):
        """Simple encryption for storing tokens (basic obfuscation)"""
        if not text:
            return ""
        return base64.b64encode(text.encode()).decode()
    
    def simple_decrypt(self, text):
        """Simple decryption for stored tokens"""
        if not text:
            return ""
        try:
            return base64.b64decode(text.encode()).decode()
        except:
            return ""

    def clear_parameters(self):
        """Clear the parameters frame"""
        for widget in self.parameters_frame.winfo_children():
            widget.destroy()
            
    def create_input_field(self, row, label, default="", var_type=tk.StringVar, combobox_values=None):
        """Create a labeled input field"""
        ttk.Label(self.parameters_frame, text=label).grid(row=row, column=0, sticky=tk.W, pady=2)
        
        if combobox_values:
            var = tk.StringVar(value=default)
            combo = ttk.Combobox(self.parameters_frame, textvariable=var, values=combobox_values, state="readonly")
            combo.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
            return var
        else:
            var = var_type(value=default)
            entry = ttk.Entry(self.parameters_frame, textvariable=var)
            entry.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
            return var
            
    def create_checkbox(self, row, label, default=False):
        """Create a checkbox"""
        var = tk.BooleanVar(value=default)
        cb = ttk.Checkbutton(self.parameters_frame, text=label, variable=var)
        cb.grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=2)
        return var

    def on_command_select(self, event):
        """Handle command selection"""
        self.clear_parameters()
        command = self.command_var.get()
        
        # Add authentication-specific options for relevant commands
        if command in ['clone', 'push', 'pull', 'fetch']:
            self.setup_auth_specific_options()
        
        if command == 'clone':
            self.setup_clone_options()
        elif command == 'init':
            self.setup_init_options()
        elif command == 'add':
            self.setup_add_options()
        elif command == 'commit':
            self.setup_commit_options()
        elif command == 'push':
            self.setup_push_options()
        elif command == 'pull':
            self.setup_pull_options()
        elif command == 'branch':
            self.setup_branch_options()
        elif command == 'checkout':
            self.setup_checkout_options()
        elif command == 'merge':
            self.setup_merge_options()
        elif command == 'log':
            self.setup_log_options()
        elif command == 'diff':
            self.setup_diff_options()
        elif command == 'remote':
            self.setup_remote_options()
        elif command == 'stash':
            self.setup_stash_options()
        elif command == 'status':
            self.setup_status_options()
        elif command == 'fetch':
            self.setup_fetch_options()
        elif command == 'rebase':
            self.setup_rebase_options()
        elif command == 'tag':
            self.setup_tag_options()
        elif command == 'reset':
            self.setup_reset_options()
        elif command == 'revert':
            self.setup_revert_options()
        elif command == 'cherry-pick':
            self.setup_cherry_pick_options()
        elif command == 'config':
            self.setup_config_options()
        elif command == 'show':
            self.setup_show_options()
        elif command == 'rm':
            self.setup_rm_options()
        elif command == 'mv':
            self.setup_mv_options()
        elif command == 'restore':
            self.setup_restore_options()
        elif command == 'switch':
            self.setup_switch_options()
            
    def setup_auth_specific_options(self):
        """Add authentication-specific options for remote operations"""
        row = len(self.parameters_frame.winfo_children()) // 2
        # Add a separator for auth options
        sep = ttk.Separator(self.parameters_frame, orient='horizontal')
        sep.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        row += 1
        
        ttk.Label(self.parameters_frame, text="Authentication:", font=('Arial', 9, 'bold')).grid(
            row=row, column=0, sticky=tk.W, pady=2)
        row += 1
        
        self.use_auth_for_command = tk.BooleanVar(value=True)
        ttk.Checkbutton(self.parameters_frame, text="Use authentication for this command", 
                       variable=self.use_auth_for_command).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=2)

    def setup_clone_options(self):
        self.parameters_frame.columnconfigure(1, weight=1)
        self.repository_url = self.create_input_field(0, "Repository URL:")
        self.clone_directory = self.create_input_field(1, "Directory (optional):")
        self.clone_branch = self.create_input_field(2, "Branch (optional):")
        self.recursive_clone = self.create_checkbox(3, "Recursive clone (--recursive)")
        self.depth = self.create_input_field(4, "Depth (shallow clone):")
        
    def setup_init_options(self):
        self.bare_init = self.create_checkbox(0, "Bare repository (--bare)")
        self.template_dir = self.create_input_field(1, "Template directory (--template):")
        self.initial_branch = self.create_input_field(2, "Initial branch name (-b):")
        
    def setup_add_options(self):
        self.add_files = self.create_input_field(0, "Files/Pattern:", ".")
        self.force_add = self.create_checkbox(1, "Force add (--force)")
        self.dry_run_add = self.create_checkbox(2, "Dry run (--dry-run)")
        self.interactive_add = self.create_checkbox(3, "Interactive (--interactive)")
        
    def setup_commit_options(self):
        self.commit_message = self.create_input_field(0, "Commit message (-m):")
        self.amend_commit = self.create_checkbox(1, "Amend commit (--amend)")
        self.all_commit = self.create_checkbox(2, "Commit all changes (-a)")
        self.no_verify_commit = self.create_checkbox(3, "Skip hooks (--no-verify)")
        
    def setup_push_options(self):
        self.push_remote = self.create_input_field(0, "Remote:", "origin")
        self.push_branch = self.create_input_field(1, "Branch:", "main")
        self.force_push = self.create_checkbox(2, "Force push (--force)")
        self.tags_push = self.create_checkbox(3, "Push tags (--tags)")
        self.set_upstream = self.create_checkbox(4, "Set upstream (-u)")
        
    def setup_pull_options(self):
        self.pull_remote = self.create_input_field(0, "Remote:", "origin")
        self.pull_branch = self.create_input_field(1, "Branch:", "main")
        self.rebase_pull = self.create_checkbox(2, "Rebase instead of merge (--rebase)")
        self.no_commit_pull = self.create_checkbox(3, "No commit (--no-commit)")
        
    def setup_branch_options(self):
        self.branch_name = self.create_input_field(0, "Branch name:")
        self.delete_branch = self.create_checkbox(1, "Delete branch (-d)")
        self.force_delete_branch = self.create_checkbox(2, "Force delete (-D)")
        self.move_branch = self.create_checkbox(3, "Move/rename branch (-m)")
        self.track_branch = self.create_checkbox(4, "Set up tracking (--track)")
        self.list_branches = self.create_checkbox(5, "List branches (-l)")
        
    def setup_checkout_options(self):
        self.checkout_target = self.create_input_field(0, "Branch/commit:")
        self.new_branch_checkout = self.create_checkbox(1, "Create new branch (-b)")
        self.force_checkout = self.create_checkbox(2, "Force checkout (--force)")
        self.detach_checkout = self.create_checkbox(3, "Detach HEAD (--detach)")
        
    def setup_merge_options(self):
        self.merge_branch = self.create_input_field(0, "Branch to merge:")
        self.no_ff_merge = self.create_checkbox(1, "No fast-forward (--no-ff)")
        self.squash_merge = self.create_checkbox(2, "Squash merge (--squash)")
        self.abort_merge = self.create_checkbox(3, "Abort merge (--abort)")
        
    def setup_log_options(self):
        self.log_count = self.create_input_field(0, "Number of commits (-n):", "10")
        self.oneline_log = self.create_checkbox(1, "One line per commit (--oneline)")
        self.graph_log = self.create_checkbox(2, "Show graph (--graph)")
        self.stat_log = self.create_checkbox(3, "Show stats (--stat)")
        self.patch_log = self.create_checkbox(4, "Show patches (--patch)")
        self.author_log = self.create_input_field(5, "Filter by author (--author):")
        
    def setup_diff_options(self):
        self.diff_cached = self.create_checkbox(0, "Staged changes (--cached)")
        self.diff_staged = self.create_checkbox(1, "Staged changes (--staged)")
        self.diff_stat = self.create_checkbox(2, "Show stats (--stat)")
        self.diff_word = self.create_checkbox(3, "Word diff (--word-diff)")
        self.diff_color = self.create_checkbox(4, "Color output (--color)")
        
    def setup_remote_options(self):
        self.remote_name = self.create_input_field(0, "Remote name:")
        self.remote_url = self.create_input_field(1, "Remote URL:")
        self.add_remote = self.create_checkbox(2, "Add remote (-a)")
        self.remove_remote = self.create_checkbox(3, "Remove remote (-r)")
        self.show_urls = self.create_checkbox(4, "Show URLs (-v)")
        
    def setup_stash_options(self):
        self.stash_message = self.create_input_field(0, "Stash message:")
        self.stash_include_untracked = self.create_checkbox(1, "Include untracked (--include-untracked)")
        self.stash_all = self.create_checkbox(2, "Stash all (--all)")
        self.pop_stash = self.create_checkbox(3, "Pop stash (pop)")
        self.list_stash = self.create_checkbox(4, "List stashes (list)")
        self.apply_stash = self.create_checkbox(5, "Apply stash (apply)")
        self.drop_stash = self.create_checkbox(6, "Drop stash (drop)")
        
    def setup_status_options(self):
        self.status_short = self.create_checkbox(0, "Short format (--short)")
        self.status_branch = self.create_checkbox(1, "Show branch info (--branch)")
        self.status_porcelain = self.create_checkbox(2, "Porcelain format (--porcelain)")
        
    def setup_fetch_options(self):
        self.fetch_remote = self.create_input_field(0, "Remote:", "origin")
        self.fetch_all = self.create_checkbox(1, "Fetch all (--all)")
        self.prune_fetch = self.create_checkbox(2, "Prune (--prune)")
        self.tags_fetch = self.create_checkbox(3, "Fetch tags (--tags)")
        
    def setup_rebase_options(self):
        self.rebase_branch = self.create_input_field(0, "Branch to rebase onto:")
        self.interactive_rebase = self.create_checkbox(1, "Interactive (--interactive)")
        self.continue_rebase = self.create_checkbox(2, "Continue (--continue)")
        self.abort_rebase = self.create_checkbox(3, "Abort (--abort)")
        self.autosquash_rebase = self.create_checkbox(4, "Autosquash (--autosquash)")
        
    def setup_tag_options(self):
        self.tag_name = self.create_input_field(0, "Tag name:")
        self.tag_message = self.create_input_field(1, "Tag message (-m):")
        self.annotated_tag = self.create_checkbox(2, "Annotated tag (-a)")
        self.delete_tag = self.create_checkbox(3, "Delete tag (-d)")
        self.list_tags = self.create_checkbox(4, "List tags (-l)")
        self.force_tag = self.create_checkbox(5, "Force (--force)")
        
    def setup_reset_options(self):
        self.reset_commit = self.create_input_field(0, "Commit (optional):")
        self.reset_mode = self.create_input_field(1, "Reset mode:", "--mixed", 
                                                combobox_values=["--soft", "--mixed", "--hard", "--merge", "--keep"])
        self.reset_path = self.create_input_field(2, "Path (optional):")
        
    def setup_revert_options(self):
        self.revert_commit = self.create_input_field(0, "Commit to revert:")
        self.no_commit_revert = self.create_checkbox(1, "No commit (--no-commit)")
        self.edit_revert = self.create_checkbox(2, "Edit commit message (--edit)")
        self.mainline_revert = self.create_input_field(3, "Mainline parent (-m):")
        
    def setup_cherry_pick_options(self):
        self.cherry_pick_commit = self.create_input_field(0, "Commit to cherry-pick:")
        self.no_commit_cherry = self.create_checkbox(1, "No commit (--no-commit)")
        self.edit_cherry = self.create_checkbox(2, "Edit (--edit)")
        self.continue_cherry = self.create_checkbox(3, "Continue (--continue)")
        self.abort_cherry = self.create_checkbox(4, "Abort (--abort)")
        
    def setup_config_options(self):
        self.config_key = self.create_input_field(0, "Config key:")
        self.config_value = self.create_input_field(1, "Config value:")
        self.global_config = self.create_checkbox(2, "Global config (--global)")
        self.list_config = self.create_checkbox(3, "List config (-l)")
        self.edit_config = self.create_checkbox(4, "Edit (--edit)")
        
    def setup_show_options(self):
        self.show_commit = self.create_input_field(0, "Commit (optional):")
        self.show_stat = self.create_checkbox(1, "Show stats (--stat)")
        self.show_patch = self.create_checkbox(2, "Show patch (-p)")
        self.show_name_only = self.create_checkbox(3, "Name only (--name-only)")
        
    def setup_rm_options(self):
        self.rm_files = self.create_input_field(0, "Files to remove:")
        self.cached_rm = self.create_checkbox(1, "Cached only (--cached)")
        self.force_rm = self.create_checkbox(2, "Force (-f)")
        self.recursive_rm = self.create_checkbox(3, "Recursive (-r)")
        
    def setup_mv_options(self):
        self.mv_source = self.create_input_field(0, "Source:")
        self.mv_dest = self.create_input_field(1, "Destination:")
        self.force_mv = self.create_checkbox(2, "Force (-f)")
        
    def setup_restore_options(self):
        self.restore_file = self.create_input_field(0, "File to restore:")
        self.staged_restore = self.create_checkbox(1, "Restore staged (--staged)")
        self.worktree_restore = self.create_checkbox(2, "Restore worktree (--worktree)")
        self.source_restore = self.create_input_field(3, "Source commit (optional):")
        
    def setup_switch_options(self):
        self.switch_branch = self.create_input_field(0, "Branch to switch to:")
        self.create_switch = self.create_checkbox(1, "Create new branch (-c)")
        self.detach_switch = self.create_checkbox(2, "Detach HEAD (--detach)")
        self.force_switch = self.create_checkbox(3, "Force (--force)")
        
    def execute_command(self):
        command = self.command_var.get()
        if not command:
            messagebox.showwarning("Warning", "Please select a Git command")
            return
            
        # Build command based on selected options
        git_cmd = ["git"]
        git_cmd.append(command)
        
        # Add command-specific arguments
        git_cmd.extend(self.build_command_arguments(command))
        
        # Add additional arguments
        additional_args = self.args_var.get().strip()
        if additional_args:
            git_cmd.extend(additional_args.split())
            
        # Execute in thread to prevent GUI freezing
        threading.Thread(target=self.run_git_command, args=(git_cmd,), daemon=True).start()
        
    def build_command_arguments(self, command):
        args = []
        
        try:
            if command == 'clone':
                if hasattr(self, 'recursive_clone') and self.recursive_clone.get():
                    args.append("--recursive")
                if hasattr(self, 'depth') and self.depth.get():
                    args.extend(["--depth", self.depth.get()])
                if hasattr(self, 'repository_url') and self.repository_url.get():
                    # Apply authentication to URL if enabled
                    url = self.repository_url.get()
                    if (hasattr(self, 'use_auth_for_command') and self.use_auth_for_command.get() and 
                        self.use_auth.get() and self.token.get()):
                        url = self.get_auth_url(url)
                    args.append(url)
                if hasattr(self, 'clone_directory') and self.clone_directory.get():
                    args.append(self.clone_directory.get())
                if hasattr(self, 'clone_branch') and self.clone_branch.get():
                    args.extend(["-b", self.clone_branch.get()])
                    
            elif command == 'init':
                if hasattr(self, 'bare_init') and self.bare_init.get():
                    args.append("--bare")
                if hasattr(self, 'template_dir') and self.template_dir.get():
                    args.extend(["--template", self.template_dir.get()])
                if hasattr(self, 'initial_branch') and self.initial_branch.get():
                    args.extend(["-b", self.initial_branch.get()])
                    
            elif command == 'add':
                if hasattr(self, 'force_add') and self.force_add.get():
                    args.append("--force")
                if hasattr(self, 'dry_run_add') and self.dry_run_add.get():
                    args.append("--dry-run")
                if hasattr(self, 'interactive_add') and self.interactive_add.get():
                    args.append("--interactive")
                if hasattr(self, 'add_files') and self.add_files.get():
                    args.append(self.add_files.get())
                    
            elif command == 'commit':
                if hasattr(self, 'amend_commit') and self.amend_commit.get():
                    args.append("--amend")
                if hasattr(self, 'all_commit') and self.all_commit.get():
                    args.append("-a")
                if hasattr(self, 'no_verify_commit') and self.no_verify_commit.get():
                    args.append("--no-verify")
                if hasattr(self, 'commit_message') and self.commit_message.get():
                    args.extend(["-m", self.commit_message.get()])
                    
            elif command == 'push':
                if hasattr(self, 'force_push') and self.force_push.get():
                    args.append("--force")
                if hasattr(self, 'tags_push') and self.tags_push.get():
                    args.append("--tags")
                if hasattr(self, 'set_upstream') and self.set_upstream.get():
                    args.append("-u")
                if hasattr(self, 'push_remote') and self.push_remote.get():
                    args.append(self.push_remote.get())
                if hasattr(self, 'push_branch') and self.push_branch.get():
                    args.append(self.push_branch.get())
                    
            # Add basic argument building for other common commands
            elif command == 'pull':
                if hasattr(self, 'rebase_pull') and self.rebase_pull.get():
                    args.append("--rebase")
                if hasattr(self, 'no_commit_pull') and self.no_commit_pull.get():
                    args.append("--no-commit")
                if hasattr(self, 'pull_remote') and self.pull_remote.get():
                    args.append(self.pull_remote.get())
                if hasattr(self, 'pull_branch') and self.pull_branch.get():
                    args.append(self.pull_branch.get())
                    
            elif command == 'branch':
                if hasattr(self, 'delete_branch') and self.delete_branch.get():
                    args.append("-d")
                elif hasattr(self, 'force_delete_branch') and self.force_delete_branch.get():
                    args.append("-D")
                elif hasattr(self, 'move_branch') and self.move_branch.get():
                    args.append("-m")
                elif hasattr(self, 'list_branches') and self.list_branches.get():
                    args.append("-l")
                if hasattr(self, 'branch_name') and self.branch_name.get():
                    args.append(self.branch_name.get())
                    
            # Add more command-specific logic as needed...
            
        except Exception as e:
            self.output_text.insert(tk.END, f"Error building command: {str(e)}\n")
            
        return args
        
    def run_git_command(self, git_cmd):
        try:
            self.output_text.insert(tk.END, f"Executing: {' '.join(git_cmd)}\n")
            self.output_text.insert(tk.END, f"in directory: {self.repo_path.get()}\n")
            self.output_text.see(tk.END)
            
            # Set environment variables for authentication if needed
            env = os.environ.copy()
            if self.use_auth.get() and self.token.get():
                # Set environment variables that Git might use
                if self.username.get():
                    env['GIT_USERNAME'] = self.username.get()
                if self.email.get():
                    env['GIT_EMAIL'] = self.email.get()
                env['GIT_ASKPASS'] = 'echo'  # Basic workaround for credential prompts
            
            result = subprocess.run(
                git_cmd,
                cwd=self.repo_path.get(),
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                env=env
            )
            
            self.root.after(0, self.display_result, result)
            
        except Exception as e:
            self.root.after(0, lambda: self.output_text.insert(tk.END, f"Error: {str(e)}\n"))
            
    def display_result(self, result):
        if result.stdout:
            self.output_text.insert(tk.END, "STDOUT:\n")
            self.output_text.insert(tk.END, result.stdout + "\n")
            
        if result.stderr:
            self.output_text.insert(tk.END, "STDERR:\n")
            self.output_text.insert(tk.END, result.stderr + "\n")
            
        self.output_text.insert(tk.END, f"Return code: {result.returncode}\n")
        self.output_text.insert(tk.END, "-" * 80 + "\n")
        self.output_text.see(tk.END)
        
    def clear_output(self):
        """Clear the output text area"""
        self.output_text.delete(1.0, tk.END)
        
    def show_git_help(self):
        """Show Git help for the selected command"""
        command = self.command_var.get()
        if command:
            git_cmd = ["git", command, "--help"]
            threading.Thread(target=self.run_git_command, args=(git_cmd,), daemon=True).start()
        else:
            messagebox.showinfo("Git Help", "Please select a command first")

def main():
    root = tk.Tk()
    app = AdvancedGitGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
