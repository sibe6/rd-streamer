import json

history_file = 'history.json'

def load_history():
    try:
        with open(history_file, 'r') as file:
            history = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        history = []
    return history

def save_history(new_entry):
    try:
        try:
            with open(history_file, 'r') as file:
                history = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            history = []
        history.append(new_entry)
        with open(history_file, 'w') as file:
            json.dump(history, file, indent=4)
    except Exception as e:
        print(f"Error saving history: {e}")

def delete_history_entry(history_data, history_listbox):
    try:
        selected_index = history_listbox.curselection()[0]
        del history_data[selected_index]
        save_deletion(history_data)
        history_listbox.delete(selected_index)
        refresh_listbox(history_listbox, history_data)
    except IndexError:
        print("No selection made")

def save_deletion(history_data):
    try:
        with open(history_file, 'w') as file:
            json.dump(history_data, file, indent=4)
    except Exception as e:
        print(f"Error saving history: {e}")

def refresh_listbox(history_listbox, history_data):
    history_listbox.delete(0, 'end')
    for entry in history_data:
        history_listbox.insert('end', entry['torrent_name'])