import os
import tkinter as tk
from tkinter import ttk, filedialog, simpledialog
import configparser

def get_steam_workshop_dir():
    """Tries to determine the Steam Workshop directory path."""
    global steam_workshop_dir
    if steam_workshop_dir:
        return steam_workshop_dir

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
    """Saves the Steam Workshop directory to the settings.cfg file."""
    settings_path = os.path.join(get_script_dir(), "settings.cfg")
    config = configparser.ConfigParser()
    config['Settings'] = {'SteamWorkshopDir': steam_workshop_dir}
    with open(settings_path, 'w') as f:
        config.write(f)


def reorder_mods():
    """Reorders mods based on the listbox selection and user input."""

    global mod_list, mod_paths

    # Get the current order from the listbox
    current_order = list(treeview.get_children())

    # Create a dictionary to map mod names to their paths
    mod_name_to_path = {treeview.item(item, "values")[1]: mod_paths[i] for i, item in enumerate(current_order)}

    # Get the new order from the user
    new_order = []
    for item in current_order:
        mod_name = treeview.item(item, "values")[1]
        new_position = simpledialog.askinteger("Reorder Mod", f"Enter new position for {mod_name} (1-{len(mod_list)}):", initialvalue=int(treeview.item(item, "values")[0]))
        new_order.append((new_position, mod_name))

    # Sort the new order based on the user input
    new_order.sort()

    # Create a new list to store the reordered mod paths
    reordered_mod_paths = [mod_name_to_path[mod_name] for _, mod_name in new_order]

    # Update usersettings.ini
    update_usersettings(reordered_mod_paths)

    # Update treeview
    treeview.delete(*treeview.get_children())
    for i, path in enumerate(reordered_mod_paths):
        mod_id = os.path.basename(path)
        mod_name = mod_list[mod_paths.index(path)]
        treeview.insert("", "end", values=(i+1, mod_id, mod_name))

def on_mod_order_change(event):
    """Handles changes to the mod order."""
    item = treeview.focus()
    new_order = treeview.item(item, "values")[0]
    try:
        new_order = int(new_order)
        if new_order < 1 or new_order > len(mod_list):
            raise ValueError()
    except ValueError:
        tk.messagebox.showerror("Invalid Input", "Please enter a valid mod order number.")
        return

    mod_name = treeview.item(item, "values")[1]
    current_order = [treeview.item(child, "values")[1] for child in treeview.get_children()]
    mod_name_to_path = {os.path.basename(path): path for path in mod_paths}
    reordered_mod_paths = [mod_name_to_path[mod_name] for mod_name in current_order]
    reordered_mod_paths.insert(new_order - 1, reordered_mod_paths.pop(current_order.index(mod_name)))

    # Update usersettings.ini
    update_usersettings(reordered_mod_paths)

    # Update treeview
    treeview.delete(*treeview.get_children())
    for i, path in enumerate(reordered_mod_paths):
        mod_id = os.path.basename(path)
        mod_name = mod_list[mod_paths.index(path)]
        treeview.insert("", "end", values=(i+1, mod_id, mod_name))

def update_usersettings(mod_paths):
    """Updates the usersettings.ini file with the new mod order."""

    usersettings_path = get_user_settings_path()

    with open(usersettings_path, "r+") as f:
        lines = f.readlines()
        f.seek(0)  # Move cursor to the beginning of the file

        # Find the [LoadOrder] section
        start_index = lines.index("[LoadOrder]\n") + 1
        end_index = start_index
        while end_index < len(lines) and lines[end_index].strip():
            end_index += 1

        # Replace mod directories with the new order
        new_lines = []
        for i, mod_path in enumerate(mod_paths):
            new_lines.append(f"Mod{i+1}Directory={os.path.basename(mod_path)}\n")

        # Update the file with the new lines
        lines[start_index:end_index] = new_lines
        f.seek(0)
        f.writelines(lines)
        f.truncate()

def load_mods():
    """Loads the list of installed mods."""

    global mod_list, mod_paths

    steam_workshop_dir = get_steam_workshop_dir()

    if steam_workshop_dir:
        mod_list = []
        mod_paths = []

        for filename in os.listdir(steam_workshop_dir):
            mod_dir = os.path.join(steam_workshop_dir, filename)
            if os.path.isdir(mod_dir):
                mod_paths.append(mod_dir)
                user_ini_path = os.path.join(mod_dir, "_user.ini")
                if os.path.exists(user_ini_path):
                    config = configparser.ConfigParser()
                    config.read(user_ini_path)
                    mod_name = config.get("Settings", "Name", fallback=filename)
                else:
                    mod_name = filename
                mod_list.append(mod_name)

        treeview.delete(*treeview.get_children())
        for i, mod in enumerate(mod_list):
            mod_id = os.path.basename(mod_paths[i])
            treeview.insert("", "end", values=(i+1, mod_id, mod))
    else:
        treeview.insert("", "end", values=("Error", "Steam Workshop directory not found."))

def on_double_click(event):
    """Handles double-click event to edit the Order field."""
    item = treeview.selection()
    if item:
        item = item[0]
        if treeview.exists(item):
            column = treeview.identify_column(event.x)
            if column == '#1':  # Check if the clicked column is "Order"
                old_value = treeview.item(item, "values")[0]
                new_value = simpledialog.askinteger("Edit Order", "Enter new order:", initialvalue=old_value)
                if new_value is not None:
                    treeview.set(item, column, new_value)
                    if treeview.exists(item):  # Ensure the item still exists before updating
                        on_mod_order_change(event)

if __name__ == "__main__":
    # Load settings before loading mods
    load_settings()

    # Create the main window
    root = tk.Tk()
    root.title("Sea Power Mod Manager")

    # Create a treeview to display mods with editable order
    treeview = ttk.Treeview(root, columns=("Order", "SteamWorkshop_ID", "Name"), show="headings")
    treeview.heading("Order", text="Order")
    treeview.heading("SteamWorkshop_ID", text="SteamWorkshop_ID")
    treeview.heading("Name", text="Name")
    treeview.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Bind the cell edit event
    treeview.bind("<FocusOut>", on_mod_order_change)

    # Bind the double-click event to the treeview
    treeview.bind("<Double-1>", on_double_click)

    # Create buttons
    save_button = tk.Button(root, text="Save", command=lambda: update_usersettings(mod_paths))
    save_button.pack(side=tk.RIGHT, fill=tk.Y)

    close_button = tk.Button(root, text="Close", command=root.quit)
    close_button.pack(side=tk.RIGHT, fill=tk.Y)

    # Load initial list of mods
    load_mods()

    root.mainloop()