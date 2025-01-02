import os
import tkinter as tk
from tkinter import ttk, filedialog
import configparser

def get_steam_workshop_dir():
    """Tries to determine the Steam Workshop directory path."""
    steam_install_dir = os.getenv("STEAM_INSTALL_PATH") 
    if steam_install_dir:
        return os.path.join(steam_install_dir, "steamapps", "workshop", "content", "1286220")  # Replace 1286220 with the correct AppID

    # If STEAM_INSTALL_PATH is not set, try common locations
    common_steam_dirs = [
        "C:\\Program Files (x86)\\Steam",
        "C:\\Program Files\\Steam",
        "D:\\Games\\Steam"  # Add other potential locations
    ]
    for dir in common_steam_dirs:
        if os.path.exists(os.path.join(dir, "steamapps")):
            return os.path.join(dir, "steamapps", "workshop", "content", "1286220")

    # If not found, prompt the user to select the directory
    root.withdraw()  # Hide the main window temporarily
    steam_workshop_dir = filedialog.askdirectory(title="Select Steam Workshop Directory")
    root.deiconify()  # Show the main window again

    # Save the selected directory to the settings file
    save_settings(steam_workshop_dir)

    return steam_workshop_dir

def get_user_settings_path():
    """Gets the path to the usersettings.ini file."""
    user_profile = os.getenv("USERPROFILE")
    return os.path.join(user_profile, "AppData", "LocalLow", "Triassic Games", "Sea Power", "usersettings.ini")

def get_script_dir():
    """Gets the directory of the current script."""
    return os.path.dirname(os.path.abspath(__file__))

def load_settings():
    """Loads the Steam Workshop directory from the settings.cfg file."""
    settings_path = os.path.join(get_script_dir(), "settings.cfg")
    config = configparser.ConfigParser()

    try:
        with open(settings_path, 'r') as f:
            config.read_file(f)
            global steam_workshop_dir
            steam_workshop_dir = config.get('Settings', 'SteamWorkshopDir', fallback=None)
    except FileNotFoundError:
        # Create a new settings file if it doesn't exist
        steam_workshop_dir = None  # Initialize steam_workshop_dir with None
        save_settings(steam_workshop_dir)

def save_settings(steam_workshop_dir):
    """Saves the current Steam Workshop directory to the settings file."""
    settings_path = os.path.join(get_script_dir(), "settings.cfg")
    config = configparser.ConfigParser()
    config['Settings'] = {'SteamWorkshopDir': steam_workshop_dir}

    with open(settings_path, 'w') as f:
        config.write(f)

def reorder_mods():
    """Reorders mods based on the listbox selection."""

    global mod_list, mod_paths

    # Get selected mods
    selected_indices = list(listbox.curselection())

    # Create a new list to store the reordered mod paths
    reordered_mod_paths = []

    # Add selected mods to the new list
    for index in selected_indices:
        reordered_mod_paths.append(mod_paths[index])

    # Add unselected mods to the new list
    for i in range(len(mod_paths)):
        if i not in selected_indices:
            reordered_mod_paths.append(mod_paths[i])

    # Update usersettings.ini
    update_usersettings(reordered_mod_paths)

    # Update listbox
    listbox.delete(0, tk.END)
    for path in reordered_mod_paths:
        listbox.insert(tk.END, os.path.basename(path))

def update_usersettings(mod_paths):
    """Updates the usersettings.ini file with the new mod order."""

    usersettings_path = get_user_settings_path()

    with open(usersettings_path, "r+") as f:
        lines = f.readlines()
        f.seek(0)  # Move cursor to the beginning of the file

        # Find the [LoadOrder] section
        start_index = lines.index("[LoadOrder]\n")
        end_index = lines.index("\n", start_index)

        # Replace mod directories with the new order
        new_lines = []
        for i, line in enumerate(lines[start_index:end_index]):
            if "Mod" in line:
                new_lines.append(f"Mod{i+1}Directory={mod_paths[i]}\n")
            else:
                new_lines.append(line)

        # Update the file with the new lines
        lines[start_index:end_index] = new_lines
        f.writelines(lines)

def load_mods():
    """Loads the list of installed mods."""

    global mod_list, mod_paths

    steam_workshop_dir = get_steam_workshop_dir()

    if steam_workshop_dir:
        mod_list = []
        mod_paths = []

        for filename in os.listdir(steam_workshop_dir):
            if os.path.isdir(os.path.join(steam_workshop_dir, filename)):
                mod_list.append(filename)
                mod_paths.append(os.path.join(steam_workshop_dir, filename))

        listbox.delete(0, tk.END)
        for mod in mod_list:
            listbox.insert(tk.END, mod)
    else:
        listbox.insert(tk.END, "Error: Steam Workshop directory not found.")

# Load settings before loading mods
load_settings()

# Create the main window
root = tk.Tk()
root.title("Sea Power Mod Manager")

# Create a listbox to display mods
listbox = tk.Listbox(root)
listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Create buttons
reorder_button = tk.Button(root, text="Reorder Mods", command=reorder_mods)
reorder_button.pack(side=tk.RIGHT, fill=tk.Y)

load_button = tk.Button(root, text="Load Mods", command=load_mods)
load_button.pack(side=tk.RIGHT, fill=tk.Y)

# Load initial list of mods
load_mods()

root.mainloop()