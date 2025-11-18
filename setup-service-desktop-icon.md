# ⚙️ Repo Rocket Setup Guide (Simplified)

[cite_start]This guide provides simplified steps to set up **Repo Rocket** (a GitHub repo launcher and editor) as a background service on a Linux system with a GNOME desktop (e.g., Ubuntu 22.04 or later) and to add a convenient desktop icon[cite: 1, 2].

**Note:** In this simplified guide, we assume the main application script is located at `/opt/reporocket/reporocket.py` and the application icon is simply named `reporocket.png`.

## 1. Set Up Repo Rocket as a Service

[cite_start]This step ensures Repo Rocket runs reliably in the background upon system startup[cite: 4, 5].

1.  [cite_start]**Create the systemd service file**[cite: 5]:
    ```bash
    sudo nano /etc/systemd/system/reporocket.service
    ```
2.  [cite_start]**Add the following content** (Remember to replace `yourusername` with your actual Linux username)[cite: 7, 8, 9]:
    ```ini
    [Unit]
    Description=RepoRocket - A GitHub Repo Launcher and Editor
    After=network.target

    [Service]
    Type=simple
    # Simplified ExecStart path
    ExecStart=/usr/bin/python3 /opt/reporocket/reporocket.py
    WorkingDirectory=/opt/reporocket
    Restart=always
    RestartSec=10
    User=yourusername
    Environment="DISPLAY=:0"
    Environment="XAUTHORITY=/home/yourusername/.Xauthority"

    [Install]
    WantedBy=multi-user.target
    ```
3.  [cite_start]**Save and exit** the editor (Ctrl+O, Enter, Ctrl+X in nano)[cite: 15].
4.  [cite_start]**Reload systemd, enable, and start the service**[cite: 16, 17, 18]:
    ```bash
    sudo systemctl daemon-reload
    sudo systemctl enable reporocket.service
    sudo systemctl start reporocket.service
    ```
5.  [cite_start]**Verify the service is running**[cite: 19, 20]:
    ```bash
    systemctl status reporocket.service
    ```
    > [cite_start]If errors occur (e.g., GUI not showing), check your `$DISPLAY` and the path to `~/.Xauthority`[cite: 21, 22].

## 2. Add a GNOME Desktop Icon

[cite_start]This allows easy access to Repo Rocket from your application menu or desktop[cite: 23].

1.  **Place the Icon:**
    * [cite_start]Ensure your `reporocket.png` is resized to $48\times48$ pixels for best display[cite: 25].
    * [cite_start]Copy the icon to the appropriate directory for your system[cite: 26, 27].
2.  [cite_start]**Create a `.desktop` File**[cite: 28, 29, 30]:
    ```bash
    nano ~/.local/share/applications/reporocket.desktop
    ```
3.  [cite_start]**Add the following content**[cite: 32, 33, 34]:
    ```ini
    [Desktop Entry]
    Name=RepoRocket
    Comment=A GitHub Repo Launcher and Editor
    # Simplified Exec path
    Exec=/usr/bin/python3 /opt/reporocket/reporocket.py
    Icon=reporocket
    Terminal=false
    Type=Application
    Categories=Development;Utility;
    StartupNotify=true
    ```
4.  [cite_start]**Save and exit**[cite: 40].
5.  [cite_start]**Make it executable**[cite: 41, 42]:
    ```bash
    chmod +x ~/.local/share/applications/reporocket.desktop
    ```
6.  [cite_start]**Add the Icon to the Desktop** (Optional)[cite: 47, 48]:
    ```bash
    cp ~/.local/share/applications/reporocket.desktop ~/Desktop/
    ```
7.  [cite_start]**Mark it as trusted and executable**[cite: 50, 51, 52]:
    ```bash
    gio set ~/Desktop/reporocket.desktop metadata::trusted true
    chmod +x ~/Desktop/reporocket.desktop
    ```

## 3. Test the Setup

1.  [cite_start]**Service Test:** Restart your system to confirm the RepoRocket service starts automatically[cite: 55].
    * [cite_start]Check the service status: `systemctl status reporocket.service`[cite: 56].
    * [cite_start]The service should be **active (running)**, and the RepoRocket GUI should appear[cite: 57].
2.  **Desktop Icon Test:**
    * [cite_start]Check your desktop—you should see the RepoRocket icon[cite: 59].
    * [cite_start]Double-click the icon to launch RepoRocket[cite: 60].
    * [cite_start]Check the GNOME application menu (search for "RepoRocket"); it should appear under "Development" or "Utility"[cite: 61].

---

## 🛑 Troubleshooting

| Issue | Recommended Action |
| :--- | :--- |
| [cite_start]**Service Not Starting** [cite: 63] | [cite_start]Check logs: `journalctl -u reporocket.service -f`[cite: 64]. [cite_start]Verify `DISPLAY` and `XAUTHORITY` settings in the service file[cite: 65]. |
| [cite_start]**Icon Not Showing** [cite: 66] | [cite_start]Ensure the icon path is correct and it is $48\times48$ pixels[cite: 67]. [cite_start]Refresh the icon cache: `sudo gtk-update-icon-cache /usr/share/icons/hicolor`[cite: 68]. |
| [cite_start]**App Not Launching from Icon** [cite: 69] | [cite_start]Verify the `Exec` path in `reporocket.desktop` is correct[cite: 70]. [cite_start]Test the command manually: `/usr/bin/python3 /opt/reporocket/reporocket.py`[cite: 71]. |

[cite_start]Happy coding with Repo Rocket! [cite: 75]
