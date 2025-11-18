# 🚀 Repo Rocket - Launch Your GitHub Repositories Like a Pro

**Repo Rocket** is a sleek, user-friendly, cross-platform desktop application built with Python to dramatically streamline your GitHub workflow. Stop wrestling with the command line! Launch, edit, commit, and push with the speed of a rocket, all from one modern interface.

## ✨ Key Features

Repo Rocket is designed to be a miracle of simplicity and power, giving developers, hobbyists, and small business owners the ability to launch and manage repos effortlessly.

* **⚡ One-Click Repo Creation:** Create a new GitHub repository, complete with a local directory, Git initialization, and an initial commit, all with a single click.
* **💻 Integrated File Editor:** Edit files directly within the app, then save, commit, and push changes to GitHub—all without leaving the interface.
* **🎨 Visually Striking GUI:** Manage your repos with a modern, black-themed GUI featuring yellow text and bright green buttons for a visually striking and productive experience.
* **🛠️ Templates Included:** Choose from **Empty**, **Python**, or **Node.js** templates for pre-filled initial files (like `.gitignore`) to get started instantly.

## ⚙️ How It Works: Features in Detail

Repo Rocket is divided into two primary workflows: **Create Repo** and **Edit Repo**.

### 1. Create Repo Workflow (Launch)

The launch phase handles the end-to-end creation of a new repository on both your local machine and GitHub.

| Field / Step | Description | Example / Details |
| :--- | :--- | :--- |
| **Repo Name** | Enter a unique name for your new repository. | `reporocket-test-13000` |
| **Access Token (PAT)** | Your GitHub Personal Access Token is required to authenticate and create the remote repository. | Paste your GitHub PAT here. |
| **New Directory Path** | Specify the local path where the repository folder will be created. | `/home/user/reporocket-test-13000` |
| **Template** | Choose a pre-defined file structure. | `empty`, `python`, or `nodejs` |
| **Private Repository** | Check this box to make the new GitHub repository private. | Toggle for privacy. |
| **Username/Email** | Used for Git commit authorship. | Defaults to `unknown` if left blank. |
| **Launch Process** | 1. Create local directory. 2. Initialize Git repo with `README.md`. 3. Apply selected template. 4. Create GitHub repo using PAT. 5. Push initial commit to GitHub. | Success message displays the repo URL. |

### 2. Edit Repo Workflow (Commit & Push)

The edit phase allows you to manage and update your local repository and sync changes back to GitHub.

1.  **Browse Directory:** Click "Browse" in the "Edit Repo" section to select the local directory of your repository. Files (excluding the `.git` directory) appear in the "Files" list.
2.  **Edit Files:** Select a file (e.g., `README.md`) to load its contents into the integrated text editor. Make your changes directly.
3.  **Save Changes:** Click **"Save File"** to write your edits to the local file system.
4.  **Commit & Push:** Click **"Commit & Push"**—Repo Rocket will handle the following:
    * `git add .` (Stage all changes).
    * `git commit` with a default message ("Update via RepoTinker").
    * `git push` to GitHub using your stored PAT—no prompts!

A success message confirms the push to your remote GitHub repository.


**Get Started With Repo Rocket and Git, Commit, and Submit!**

Launch your REPO'S with ease!

© 2025 Repo-Rocket
