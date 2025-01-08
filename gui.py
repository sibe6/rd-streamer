from tkinter import Frame, Button, Label, Entry, Radiobutton, StringVar, constants, Scrollbar, Toplevel, Listbox
from ttkbootstrap.scrolled import ScrolledFrame
from ttkbootstrap.constants import *
from PIL import Image, ImageTk
from collections import deque
import constants as c
import ttkbootstrap as ttk
import helpers as h
import requests
import history
import io
import os


class MainWindow:
    def __init__(self, root, on_callback):
        self._root = root
        self._root.geometry("700x700")
        self._root.title("rd-streamer")

        ttk.Style().theme_use("darkly")

        self._header = None
        self._middle = None
        self._footer = None
        self._on_callback = on_callback
        self._list_window_stack = deque()
        self._context_manager = ContextManager()

        self._setup_layout()

    def _setup_layout(self):
        self._header = Header(self._root, self._on_callback, self.new_middle_callback, self.go_back)
        self._middle = Frame(self._root, width=650, bg="white")
        self._middle.pack(fill=constants.BOTH, expand=True, side=constants.TOP)
        self._footer = Footer(self._root, self._context_manager)

    def footer_callback(self, download_link):
        print(f"Updating footer with link: {download_link}")
        self._context_manager.set_download_link(download_link)
        self._footer.display_link(download_link)

    def new_middle_callback(self, action, items=None):
        if action == "search_movie" or action == "search_series":
            print("\tSearch pressed, clearing the stack and destroying all windows.")

            while self._list_window_stack:
                window = self._list_window_stack.pop()
                window.destroy()

            self._context_manager.reset()
            self._list_window_stack = []

        if len(self._list_window_stack) > 0:
            previous = self._list_window_stack[-1]
            previous.hide()

        if action == c.SEARCH_SOURCES:
            list_window = ListWindow(self._middle, self._on_callback, self.new_middle_callback,
                                     self._context_manager, self.footer_callback)
            list_window.display_sources(items)
            self._list_window_stack.append(list_window)
        else:
            list_window = ListWindow(self._middle, self._on_callback, self.new_middle_callback,
                                     self._context_manager, self.footer_callback)
            list_window.display(items)
            self._list_window_stack.append(list_window)

    def go_back(self):
        if len(self._list_window_stack) > 0:
            current_window = self._list_window_stack.pop()
            current_window.destroy()
            if len(self._list_window_stack) >= 1:
                previous_window = self._list_window_stack[-1]
                previous_window.show()
        else:
            print("No previous window to go back to.")

    def start(self):
        self._root.mainloop()

class Header:
    def __init__(self, parent, on_callback, new_middle_callback, on_back_click):
        self._frame = Frame(parent, height=200, bg="lightblue")
        self._frame.pack(fill=constants.X, side=constants.TOP)

        self._on_callback = on_callback
        self._new_middle_callback = new_middle_callback
        self._on_back_click = on_back_click
        self._search_var = StringVar()
        self._radio_var = StringVar(value=c.SEARCH_SERIES)
        self._history_data = []

        self._setup_header()

    def _setup_header(self):
        search_entry = Entry(self._frame, textvariable=self._search_var)
        search_entry.pack(side=constants.LEFT, padx=5, pady=5)

        search_entry.focus_set()

        search_entry.bind("<Return>", self._on_search_enter)

        Button(self._frame, text="Search", command=self._on_search_click).pack(side=constants.LEFT, padx=5, pady=5)

        Radiobutton(self._frame, text="Shows", variable=self._radio_var, value=c.SEARCH_SERIES).pack(side=constants.LEFT, padx=5, pady=5)
        Radiobutton(self._frame, text="Movies", variable=self._radio_var, value=c.SEARCH_MOVIES).pack(side=constants.LEFT, padx=5, pady=5)

        Button(self._frame, text="Back", command=self._on_back_click).pack(side=constants.RIGHT, padx=5, pady=5)
        Button(self._frame, text="History", command=self._show_history_window).pack(side=constants.RIGHT, padx=5, pady=5)

    def _on_search_enter(self, event):
        self._on_search_click()

    def _on_search_click(self):
        search_term = self._search_var.get()
        callback_type = self._radio_var.get()

        print("CALLBACK", callback_type)
        if self._on_callback:
            self._on_callback(callback_type, search_term, self._new_middle_callback)

    def _show_history_window(self):
        self._history_data = history.load_history()
        if self._history_data:
            self._create_history_window(self._history_data)
        else:
            self._create_history_window([])

    def _create_history_window(self, history_data):
        history_window = Toplevel(self._frame)
        history_window.title("History")
        history_window.geometry("400x300")

        history_listbox = Listbox(history_window, width=50, height=15)
        history_listbox.pack(padx=10, pady=10)

        for index, entry in enumerate(history_data):
            history_listbox.insert('end', f"{entry['show']} - Season {entry['season']}, Episode {entry['episode']} - {entry['torrent_name']}")

        scrollbar = Scrollbar(history_window, orient="vertical", command=history_listbox.yview)
        scrollbar.pack(side="right", fill="y")
        history_listbox.config(yscrollcommand=scrollbar.set)

        button_frame = Frame(history_window)
        button_frame.pack(side="bottom", pady=10)

        delete_button = Button(button_frame, text="Delete Selected",
                               command=lambda: self._delete_history_entry(history_listbox, history_data))
        delete_button.pack(side="left", padx=5)

        open_button = Button(button_frame, text="Open Video",
                             command=lambda: self._open_video(history_listbox, history_data))
        open_button.pack(side="right", padx=5)

        close_button = Button(history_window, text="Close", command=history_window.destroy)
        close_button.pack(pady=10)

    def _delete_history_entry(self, history_listbox, history_data):
        history.delete_history_entry(history_data, history_listbox)

    def _open_video(self, history_listbox, history_data):
        try:
            selected_index = history_listbox.curselection()
            if not selected_index:
                print("No item selected.")
                return
            selected_index = selected_index[0]
            entry = history_data[selected_index]
            print(f"Opening video for {entry['torrent_name']}...")
            h.open_in_player(entry['download_link'])
        except Exception as e:
            print(f"Error opening video: {e}")

class Footer:
    def __init__(self, parent, context_manager):
        self._frame = Frame(parent, height=50, bg="lightgray")
        self._frame.pack(fill=constants.X, side=constants.BOTTOM)
        self._root = parent
        self._context = context_manager

    def display_link(self, download_link):
        history.save_history(self._context.get_context())

        for widget in self._frame.winfo_children():
            widget.destroy()
        max_length = 50

        if len(download_link) > max_length:
            download_link = download_link[:max_length] + "..."

        link_label = Label(self._frame, text=download_link, fg="blue", cursor="hand2", width=50, anchor="w")
        link_label.pack(side=constants.LEFT, padx=10)

        copy_button = Button(self._frame, text="Copy Link", command=lambda: self.copy_to_clipboard(download_link))
        copy_button.pack(side=constants.LEFT, padx=10)

        empty_button = Button(self._frame, text="TODO", state=constants.DISABLED)
        empty_button.pack(side=constants.LEFT, padx=10)

    def copy_to_clipboard(self, link):
        self._root.clipboard_clear()
        self._root.clipboard_append(link)
        self._root.update()
        print(f"Copied link to clipboard: {link}")

    def open_player(self):
        pass

class ListWindow:
    def __init__(self, parent, on_callback, new_middle_callback, context_manager, footer_callback):
        self._parent = parent

        self._new_middle_callback = new_middle_callback
        self._on_callback = on_callback
        self._context_manager = context_manager
        self._footer_callback = footer_callback

        self._scrollable_frame = ScrolledFrame(self._parent, autohide=True)
        self._scrollable_frame.pack(fill=BOTH, expand=YES, padx=10, pady=10)

        self._frame = ttk.Frame(self._scrollable_frame)
        self._frame.pack(fill=BOTH, expand=YES)

    def display(self, items):
        self.clear()

        for item in items:
            title = item.get('title')
            year = item.get('year')
            id_ = item.get('id')

            row_frame = ttk.Frame(self._frame, padding=5)
            row_frame.pack(fill="x", expand=True, padx=10, pady=5)

            label_text = f"{title} ({year})"
            label = ttk.Label(row_frame, text=label_text)
            label.pack(side="left", fill="x", expand=True)

            image_path = item.get("image_path")
            if image_path and os.path.exists(image_path):
                image = Image.open(image_path)
                image_tk = ImageTk.PhotoImage(image)
                label_image = Label(row_frame, image=image_tk)
                label_image.image = image_tk
                label_image.pack(side="right", padx=10)
            else:
                label_image = Label(row_frame, text="No Image", bg="gray", width=8, height=4)
                label_image.pack(side="right", padx=10)

            label.bind("<Button-1>", lambda e, item=item: self._on_item_click(item))
            label_image.bind("<Button-1>", lambda e, item=item: self._on_item_click(item))


    def _on_item_click(self, item):
        print(f"Item clicked: ({item['id']}) {item['title']} ({item['year']}) {item['item_type']}")

        if (item.get('item_type') == c.MOVIE):
            self._context_manager.set_show(h.normalize_text(item.get('title')))
            self._context_manager.set_type(item['item_type'])
            self._context_manager.set_year(item.get('year'))
            if self._on_callback:
                self._on_callback(c.SEARCH_SOURCES, self._context_manager.get_context(), self._new_middle_callback)
        elif (item.get('item_type') == c.SERIES):
            self._context_manager.set_type(item['item_type'])
            self._context_manager.set_year(item.get('year'))
            self._context_manager.set_show(h.normalize_text(item.get('title')))
            if self._on_callback:
                self._on_callback(c.SEARCH_SEASONS, item['id'], self._new_middle_callback)
        elif (item.get('item_type') == c.SEASON):
            self._context_manager.set_season(item.get('number'))
            if self._on_callback:
                self._on_callback(c.SEARCH_EPISODES, item['id'], self._new_middle_callback)
        elif (item.get('item_type') == c.EPISODE):
            self._context_manager.set_episode(item.get('year'))
            if self._on_callback:
                self._on_callback(c.SEARCH_SOURCES, self._context_manager.get_context(), self._new_middle_callback)

    def display_sources(self, items):
        if not items:
            frame = ttk.Frame(self._frame)
            frame.pack(fill="x", padx=10, pady=5)
            label_text = f"No sources found"
            label = Label(frame, text=label_text, anchor="w", padx=10, pady=5)
            label.pack(side="left", fill="x", expand=True)

        for item in items:
            name = item.get('torrentName')
            size = item.get('torrentSize')

            row_frame = ttk.Frame(self._frame, padding=5)
            row_frame.pack(fill="x", expand=True, padx=10, pady=5)

            label_text = f"{name} ({size})"
            label = Label(row_frame, text=label_text, anchor="w", padx=10, pady=5)
            label.pack(side="left", fill="x", expand=True)

            label.bind("<Button-1>", lambda e, item=item: self._on_source_click(item))

    def _on_source_click(self, source):
        if self._on_callback:
            self._context_manager.set_torrent_name(source['torrentName'])
            self._on_callback(c.GET_LINK, source, self._footer_callback)

    def destroy(self):
        self._scrollable_frame.container.destroy()

    def clear(self):
        pass

    def hide(self):
        self._scrollable_frame.pack_forget()

    def show(self):
        self._scrollable_frame.pack(fill=BOTH, expand=YES, padx=10, pady=10)

def load_image(image_url, target_height=150):
    if image_url:
        try:
            response = requests.get(image_url, stream=True)
            response.raise_for_status()
            image_data = response.content
            image = Image.open(io.BytesIO(image_data))
            original_width, original_height = image.size
            aspect_ratio = original_width / original_height
            target_width = int(target_height * aspect_ratio)
            image = image.resize((target_width, target_height), Image.Resampling.LANCZOS)
            return ImageTk.PhotoImage(image)
        except Exception as e:
            print(f"Failed to load image: {e}")
            return None
    else:
        return None

class ContextManager:
    def __init__(self):
        self.reset()

    def reset(self):
        self.year = None
        self.type_ = None
        self.show = None
        self.season = None
        self.episode = None
        self.torrent_name = None
        self.download_link = None

    def set_year(self, year):
        self.year = year

    def set_type(self, type_):
        self.type_ = type_

    def set_show(self, show):
        self.show = show

    def set_season(self, season):
        self.season = season

    def set_episode(self, episode):
        self.episode = episode

    def set_torrent_name(self, torrent_name):
        self.torrent_name = torrent_name

    def set_download_link(self, download_link):
        self.download_link = download_link

    def get_context(self):
        return {
            "type": self.type_,
            "year": self.year,
            "show": self.show,
            "season": self.season,
            "episode": self.episode,
            "torrent_name": self.torrent_name,
            "download_link": self.download_link,
        }
