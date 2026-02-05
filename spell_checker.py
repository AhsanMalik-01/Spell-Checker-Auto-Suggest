import tkinter as tk
from tkinter import messagebox

# ==========================================
# PART 1: Simple Data Structures
# ==========================================

class TrieNode:
    """A single node in our Trie tree"""
    def __init__(self):
        self.children = {}  # Store child letters
        self.is_word = False  # Is this the end of a word?

class Trie:
    """A tree structure to store words efficiently"""
    def __init__(self):
        self.root = TrieNode()
        self.all_words = []  # Keep all words in a list too
    
    def add_word(self, word):
        """Add a word to our dictionary"""
        word = word.lower()
        node = self.root
        
        # Go through each letter
        for letter in word:
            if letter not in node.children:
                node.children[letter] = TrieNode()
            node = node.children[letter]
        
        node.is_word = True
        self.all_words.append(word)
    
    def word_exists(self, word):
        """Check if a word is in our dictionary"""
        word = word.lower()
        node = self.root
        
        # Try to find each letter
        for letter in word:
            if letter not in node.children:
                return False
            node = node.children[letter]
        
        return node.is_word
    
    def find_suggestions(self, prefix):
        """Find all words that start with prefix"""
        prefix = prefix.lower()
        node = self.root
        
        # Navigate to the prefix
        for letter in prefix:
            if letter not in node.children:
                return []
            node = node.children[letter]
        
        # Find all words from this point
        suggestions = []
        self._find_all_words(node, prefix, suggestions)
        return suggestions[:10]  # Return top 10
    
    def _find_all_words(self, node, current_word, suggestions):
        """Helper: Find all words starting from a node"""
        if node.is_word:
            suggestions.append(current_word)
        
        for letter, child in node.children.items():
            self._find_all_words(child, current_word + letter, suggestions)


def calculate_difference(word1, word2):
    """
    Count how many changes needed to turn word1 into word2
    (insert, delete, or replace letters)
    """
    len1 = len(word1)
    len2 = len(word2)
    
    # Create a table to store results
    table = []
    for i in range(len1 + 1):
        row = []
        for j in range(len2 + 1):
            row.append(0)
        table.append(row)
    
    # Fill first column and row
    for i in range(len1 + 1):
        table[i][0] = i
    for j in range(len2 + 1):
        table[0][j] = j
    
    # Fill the rest of the table
    for i in range(1, len1 + 1):
        for j in range(1, len2 + 1):
            if word1[i-1] == word2[j-1]:
                table[i][j] = table[i-1][j-1]  # Letters match
            else:
                table[i][j] = 1 + min(
                    table[i-1][j],      # Delete
                    table[i][j-1],      # Insert
                    table[i-1][j-1]     # Replace
                )
    
    return table[len1][len2]


# ==========================================
# PART 2: Beautiful GUI
# ==========================================

class SpellCheckerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Spell Checker & Auto-Suggest")
        self.root.geometry("800x700")
        self.root.resizable(False, False)
        self.root.config(bg="#f5f5f5")
        
        # Create our dictionary
        self.dictionary = Trie()
        self.load_words()
        
        # Track statistics
        self.total_checks = 0
        self.total_corrections = 0
        
        self.setup_gui()
    
    def load_words(self):
        """Load all dictionary words"""
        words = [
            # Programming words
            "algorithm", "application", "binary", "code", "computer", "data",
            "database", "debug", "function", "hardware", "internet", "java",
            "language", "memory", "network", "program", "python", "software",
            "system", "technology", "tree", "trie", "variable", "web",
            
            # Common words
            "about", "after", "again", "all", "also", "always", "and",
            "answer", "any", "apple", "are", "around", "ask", "back",
            "because", "before", "being", "between", "both", "but", "call",
            "came", "can", "change", "come", "could", "create", "day",
            "did", "different", "do", "does", "down", "each", "even",
            "every", "find", "first", "follow", "for", "from", "get",
            "give", "good", "great", "had", "has", "have", "help",
            "here", "high", "home", "how", "important", "into", "is",
            "it", "just", "know", "large", "last", "like", "little",
            "long", "look", "made", "make", "many", "may", "more",
            "most", "move", "much", "name", "need", "new", "next",
            "not", "now", "number", "of", "old", "on", "one",
            "only", "or", "other", "our", "out", "over", "part",
            "people", "place", "program", "put", "said", "same", "say",
            "school", "see", "she", "should", "show", "small", "some",
            "take", "tell", "than", "that", "the", "their", "them",
            "then", "there", "these", "they", "thing", "think", "this",
            "time", "to", "too", "two", "under", "up", "use",
            "very", "want", "was", "water", "way", "we", "well",
            "were", "what", "when", "where", "which", "who", "will",
            "with", "word", "work", "world", "would", "write", "year",
            "you", "your"
        ]
        
        for word in words:
            self.dictionary.add_word(word)
    
    def setup_gui(self):
        """Create all visual elements"""
        
        # Header
        header = tk.Frame(self.root, bg="#2196F3", height=80)
        header.pack(fill=tk.X)
        
        title = tk.Label(
            header,
            text="✓ Spell Checker & Auto-Suggest",
            font=("Arial", 24, "bold"),
            bg="#2196F3",
            fg="white"
        )
        title.pack(pady=20)
        
        # Main area
        main = tk.Frame(self.root, bg="#f5f5f5")
        main.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)
        
        # Input section
        input_box = tk.LabelFrame(
            main,
            text="  Enter Word  ",
            font=("Arial", 12, "bold"),
            bg="#f5f5f5"
        )
        input_box.pack(fill=tk.X, pady=(0, 15))
        
        input_area = tk.Frame(input_box, bg="#f5f5f5")
        input_area.pack(padx=15, pady=15)
        
        # Text entry
        entry_box = tk.Frame(input_area, bg="white", relief=tk.SOLID, bd=1)
        entry_box.pack(side=tk.LEFT, padx=(0, 10))
        
        self.word_input = tk.Entry(
            entry_box,
            font=("Arial", 16),
            width=30,
            bg="white",
            relief=tk.FLAT
        )
        self.word_input.pack(padx=5, pady=5)
        self.word_input.bind('<KeyRelease>', self.show_suggestions)
        self.word_input.bind('<Return>', lambda e: self.check_word())
        self.word_input.focus()
        
        # Buttons
        buttons = tk.Frame(input_area, bg="#f5f5f5")
        buttons.pack(side=tk.LEFT)
        
        check_button = tk.Button(
            buttons,
            text="🔍 Check",
            command=self.check_word,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 11, "bold"),
            padx=20,
            pady=10,
            relief=tk.FLAT,
            cursor="hand2"
        )
        check_button.pack(side=tk.LEFT, padx=5)
        
        clear_button = tk.Button(
            buttons,
            text="✖ Clear",
            command=self.clear_all,
            bg="#f44336",
            fg="white",
            font=("Arial", 11, "bold"),
            padx=20,
            pady=10,
            relief=tk.FLAT,
            cursor="hand2"
        )
        clear_button.pack(side=tk.LEFT, padx=5)
        
        # Result message
        result_area = tk.Frame(main, bg="#f5f5f5", height=60)
        result_area.pack(fill=tk.X, pady=(0, 15))
        
        self.result_text = tk.Label(
            result_area,
            text="",
            font=("Arial", 13, "italic"),
            bg="#f5f5f5"
        )
        self.result_text.pack(pady=10)
        
        # Suggestions box
        suggest_box = tk.LabelFrame(
            main,
            text="  Suggestions  ",
            font=("Arial", 12, "bold"),
            bg="#f5f5f5"
        )
        suggest_box.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        list_area = tk.Frame(suggest_box, bg="white")
        list_area.pack(padx=15, pady=15, fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(list_area)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.suggestions = tk.Listbox(
            list_area,
            font=("Arial", 12),
            bg="white",
            selectbackground="#2196F3",
            selectforeground="white",
            relief=tk.FLAT,
            yscrollcommand=scrollbar.set
        )
        self.suggestions.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.suggestions.yview)
        
        self.suggestions.bind('<<ListboxSelect>>', self.use_suggestion)
        self.suggestions.bind('<Double-Button-1>', self.use_and_check)
        
        # Statistics
        stats = tk.Frame(main, bg="#e3f2fd", relief=tk.SOLID, bd=1)
        stats.pack(fill=tk.X)
        
        stats_inner = tk.Frame(stats, bg="#e3f2fd")
        stats_inner.pack(pady=10)
        
        self.words_label = tk.Label(
            stats_inner,
            text=f"📚 Dictionary: {len(self.dictionary.all_words)} words",
            font=("Arial", 10),
            bg="#e3f2fd",
            fg="#1976D2"
        )
        self.words_label.pack(side=tk.LEFT, padx=20)
        
        self.checks_label = tk.Label(
            stats_inner,
            text=f"🔍 Checks: {self.total_checks}",
            font=("Arial", 10),
            bg="#e3f2fd",
            fg="#1976D2"
        )
        self.checks_label.pack(side=tk.LEFT, padx=20)
        
        self.fixes_label = tk.Label(
            stats_inner,
            text=f"✓ Corrections: {self.total_corrections}",
            font=("Arial", 10),
            bg="#e3f2fd",
            fg="#1976D2"
        )
        self.fixes_label.pack(side=tk.LEFT, padx=20)
    
    def show_suggestions(self, event):
        """Show suggestions as user types"""
        typed = self.word_input.get().strip()
        self.suggestions.delete(0, tk.END)
        
        if typed:
            matches = self.dictionary.find_suggestions(typed)
            
            if matches:
                for word in matches:
                    self.suggestions.insert(tk.END, f"  {word}")
            else:
                self.suggestions.insert(tk.END, "  No suggestions")
    
    def check_word(self):
        """Check if the word is spelled correctly"""
        typed = self.word_input.get().strip()
        
        if not typed:
            messagebox.showwarning("Empty", "Please type a word first!")
            return
        
        if not typed.isalpha():
            messagebox.showerror("Invalid", "Please use only letters!")
            return
        
        self.total_checks += 1
        self.update_stats()
        
        # Check if word exists
        if self.dictionary.word_exists(typed):
            self.result_text.config(
                text=f"✓ Correct! '{typed}' is spelled right.",
                fg="#4CAF50",
                font=("Arial", 13, "bold")
            )
            self.suggestions.delete(0, tk.END)
            self.suggestions.insert(tk.END, f"  '{typed}' is in dictionary!")
        else:
            self.result_text.config(
                text=f"✗ Wrong! '{typed}' not found.",
                fg="#f44336",
                font=("Arial", 13, "bold")
            )
            self.find_similar_words(typed)
            self.total_corrections += 1
            self.update_stats()
    
    def find_similar_words(self, wrong_word):
        """Find words that are similar to the misspelled word"""
        self.suggestions.delete(0, tk.END)
        self.suggestions.insert(tk.END, "  🔄 Searching...")
        self.root.update()
        
        similar = []
        
        # Compare with all dictionary words
        for word in self.dictionary.all_words:
            difference = calculate_difference(wrong_word.lower(), word)
            
            # Only keep words that are close
            if difference <= 3:
                similar.append((difference, word))
        
        # Sort by how similar they are
        similar.sort()
        
        self.suggestions.delete(0, tk.END)
        
        if similar:
            self.suggestions.insert(tk.END, "  📝 Did you mean:")
            for diff, word in similar[:8]:
                self.suggestions.insert(tk.END, f"    • {word} (changes: {diff})")
        else:
            self.suggestions.insert(tk.END, "  ✗ No similar words found")
    
    def use_suggestion(self, event):
        """Fill input when clicking a suggestion"""
        selection = self.suggestions.curselection()
        if selection:
            text = self.suggestions.get(selection[0]).strip()
            
            # Extract just the word
            if "•" in text:
                word = text.split("•")[1].split("(")[0].strip()
            else:
                word = text.strip()
            
            if word and word.isalpha():
                self.word_input.delete(0, tk.END)
                self.word_input.insert(0, word)
                self.result_text.config(text="")
    
    def use_and_check(self, event):
        """Use suggestion and check it (double-click)"""
        self.use_suggestion(event)
        self.root.after(100, self.check_word)
    
    def update_stats(self):
        """Update the statistics display"""
        self.checks_label.config(text=f"🔍 Checks: {self.total_checks}")
        self.fixes_label.config(text=f"✓ Corrections: {self.total_corrections}")
    
    def clear_all(self):
        """Clear everything"""
        self.word_input.delete(0, tk.END)
        self.suggestions.delete(0, tk.END)
        self.result_text.config(text="")
        self.word_input.focus()


# ==========================================
# Run the Program
# ==========================================

if __name__ == "__main__":
    root = tk.Tk()
    app = SpellCheckerApp(root)
    root.mainloop()