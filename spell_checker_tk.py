"""
Simple Spell Checker with Tkinter GUI
File: spell_checker_tk.py
Requirements:
    pip install pyspellchecker

Features:
- Open / Save files
- Check spelling (F7) and highlight misspelled words
- Right-click a misspelled word to get suggestions and replace
- Add word to personal dictionary (stored in user_words.txt)
- Status bar and basic keyboard shortcuts

Author: ChatGPT (GPT-5 Thinking mini)
"""

import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from spellchecker import SpellChecker
import re
import os

# Constants
USER_DICT_FILE = "user_words.txt"

class SpellCheckerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Tkinter Spell Checker")
        self.root.geometry("900x600")

        # Spell checker backend
        self.sp = SpellChecker()
        self.user_words = set()
        self.load_user_words()

        # Menu
        self.create_menu()

        # Toolbar
        self.create_toolbar()

        # Main text area
        self.text = tk.Text(root, wrap="word", undo=True)
        self.text.pack(fill="both", expand=True, padx=4, pady=(0,4))
        self.text.tag_configure("misspelled", underline=True, foreground="red")

        # Right-click menu for suggestions
        self.suggest_menu = tk.Menu(root, tearoff=0)

        # Status bar
        self.status = tk.StringVar()
        self.status.set("Ready")
        status_bar = tk.Label(root, textvariable=self.status, anchor="w")
        status_bar.pack(side="bottom", fill="x")

        # Bindings
        self.root.bind_all("<Control-s>", self.save_file_event)
        self.root.bind_all("<Control-o>", self.open_file_event)
        self.root.bind_all("<Control-q>", self.quit_event)
        self.root.bind_all("<F7>", self.check_spelling_event)
        self.text.bind("<Button-3>", self.on_right_click)

        # Current file
        self.current_file = None

    # --------- File and menu functions ---------
    def create_menu(self):
        menubar = tk.Menu(self.root)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Open...", accelerator="Ctrl+O", command=self.open_file)
        filemenu.add_command(label="Save", accelerator="Ctrl+S", command=self.save_file)
        filemenu.add_command(label="Save As...", command=self.save_file_as)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", accelerator="Ctrl+Q", command=self.root.quit)
        menubar.add_cascade(label="File", menu=filemenu)

        toolmenu = tk.Menu(menubar, tearoff=0)
        toolmenu.add_command(label="Check Spelling (F7)", command=self.check_spelling)
        toolmenu.add_command(label="Add Word to Dictionary...", command=self.add_word_dialog)
        menubar.add_cascade(label="Tools", menu=toolmenu)

        helpmenu = tk.Menu(menubar, tearoff=0)
        helpmenu.add_command(label="About", command=self.show_about)
        menubar.add_cascade(label="Help", menu=helpmenu)

        self.root.config(menu=menubar)

    def create_toolbar(self):
        toolbar = tk.Frame(self.root)
        btn_check = tk.Button(toolbar, text="Check (F7)", command=self.check_spelling)
        btn_check.pack(side="left", padx=2, pady=2)
        btn_add = tk.Button(toolbar, text="Add Word", command=self.add_word_dialog)
        btn_add.pack(side="left", padx=2, pady=2)
        toolbar.pack(fill="x")

    def show_about(self):
        messagebox.showinfo("About", "Simple Python Spell Checker\nUsing pyspellchecker and Tkinter")

    def open_file_event(self, event=None):
        self.open_file()

    def save_file_event(self, event=None):
        self.save_file()

    def quit_event(self, event=None):
        self.root.quit()

    # --------- File operations ---------
    def open_file(self):
        fname = filedialog.askopenfilename(filetypes=[("Text files","*.txt"), ("All files","*.*")])
        if not fname:
            return
        with open(fname, 'r', encoding='utf-8') as f:
            data = f.read()
        self.text.delete(1.0, tk.END)
        self.text.insert(tk.END, data)
        self.current_file = fname
        self.status.set(f"Opened {os.path.basename(fname)}")
        self.clear_highlights()

    def save_file(self):
        if not self.current_file:
            return self.save_file_as()
        content = self.text.get(1.0, tk.END)
        with open(self.current_file, 'w', encoding='utf-8') as f:
            f.write(content)
        self.status.set(f"Saved {os.path.basename(self.current_file)}")

    def save_file_as(self):
        fname = filedialog.asksaveasfilename(defaultextension='.txt', filetypes=[('Text', '*.txt'), ('All files','*.*')])
        if not fname:
            return
        content = self.text.get(1.0, tk.END)
        with open(fname, 'w', encoding='utf-8') as f:
            f.write(content)
        self.current_file = fname
        self.status.set(f"Saved {os.path.basename(fname)}")

    # --------- User dictionary ---------
    def load_user_words(self):
        try:
            if os.path.exists(USER_DICT_FILE):
                with open(USER_DICT_FILE, 'r', encoding='utf-8') as f:
                    for line in f:
                        w = line.strip()
                        if w:
                            self.user_words.add(w.lower())
                            self.sp.word_frequency.add(w.lower())
        except Exception as e:
            print("Could not load user words:", e)

    def add_word(self, word):
        word = word.strip()
        if not word:
            return
        self.user_words.add(word.lower())
        self.sp.word_frequency.add(word.lower())
        with open(USER_DICT_FILE, 'a', encoding='utf-8') as f:
            f.write(word + "\n")
        self.status.set(f"Added '{word}' to user dictionary")
        self.check_spelling()

    def add_word_dialog(self):
        w = simpledialog.askstring("Add Word", "Enter word to add to dictionary:")
        if w:
            self.add_word(w)

    # --------- Spell checking logic ---------
    def get_words_with_indices(self):
        """Return list of (word, start_index, end_index) in the text widget."""
        text = self.text.get(1.0, tk.END)
        words = []
        # Regex to find words (letters, apostrophes, hyphens)
        for match in re.finditer(r"[A-Za-z\u00C0-\u017F'-]+", text):
            w = match.group(0)
            start_pos = match.start()
            end_pos = match.end()
            # convert to Tkinter index
            start_index = f"1.0 + {start_pos} chars"
            end_index = f"1.0 + {end_pos} chars"
            words.append((w, start_index, end_index))
        return words

    def clear_highlights(self):
        self.text.tag_remove("misspelled", "1.0", tk.END)

    def check_spelling_event(self, event=None):
        self.check_spelling()

    def check_spelling(self):
        self.clear_highlights()
        content = self.text.get(1.0, tk.END)
        if not content.strip():
            self.status.set("No text to check")
            return

        words = self.get_words_with_indices()
        misspelled = []
        for w, start, end in words:
            lw = w.lower()
            if lw in self.user_words:
                continue
            # numeric or single-letter words skip
            if len(lw) == 1:
                continue
            if self.sp.unknown([lw]):
                # Tag this range
                try:
                    self.text.tag_add("misspelled", start, end)
                    misspelled.append((w, start, end))
                except tk.TclError:
                    # bad indices sometimes happen with unicode; skip
                    continue

        self.status.set(f"Found {len(misspelled)} possible errors")

    # --------- Right-click suggestions & replace ---------
    def on_right_click(self, event):
        # get index under mouse
        idx = self.text.index(f"@{event.x},{event.y}")
        # check if index has misspelled tag
        tags = self.text.tag_names(idx)
        if "misspelled" in tags:
            # find word boundaries around idx
            start = self.text.search(r"\m", idx, backwards=True, regexp=True)
            end = self.text.search(r"\M", idx, forwards=True, regexp=True)
            # fallback: use word_start/word_end
            if not start:
                start = self.text.index(f"{idx} wordstart")
            if not end:
                end = self.text.index(f"{idx} wordend")
            word = self.text.get(start, end)
            # build suggestion menu
            self.suggest_menu.delete(0, tk.END)
            suggestions = list(self.sp.candidates(word.lower()))[:6]
            if suggestions:
                for s in suggestions:
                    display = s
                    self.suggest_menu.add_command(label=display, command=lambda rep=s, a=start, b=end: self.replace_word(a, b, rep))
            else:
                self.suggest_menu.add_command(label="No suggestions", state="disabled")
            self.suggest_menu.add_separator()
            self.suggest_menu.add_command(label="Add to dictionary", command=lambda w=word: self.add_word(w))
            try:
                self.suggest_menu.tk_popup(event.x_root, event.y_root)
            finally:
                self.suggest_menu.grab_release()
        else:
            # default right click: popup with simple options
            menu = tk.Menu(self.root, tearoff=0)
            menu.add_command(label="Check Spelling (F7)", command=self.check_spelling)
            menu.add_command(label="Add Word to Dictionary...", command=self.add_word_dialog)
            try:
                menu.tk_popup(event.x_root, event.y_root)
            finally:
                menu.grab_release()

    def replace_word(self, start, end, new_word):
        self.text.delete(start, end)
        self.text.insert(start, new_word)
        self.check_spelling()


if __name__ == "__main__":
    root = tk.Tk()
    app = SpellCheckerApp(root)
    root.mainloop()
