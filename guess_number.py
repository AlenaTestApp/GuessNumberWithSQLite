import random
import sqlite3
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import pygame


# ---------- class SoundManager ----------
class SoundManager:
    def __init__(self, sound_path="sounds/GAME-003.WAV"):
        pygame.mixer.init()
        self.sound_path = sound_path

    def play_sound(self):
        pygame.mixer.music.load(self.sound_path)
        pygame.mixer.music.play()


# ---------- class DatabaseManager ----------
class DatabaseManager:
    def __init__(self, path="Guess_Game.db"):
        self.con = sqlite3.connect(path)
        self.cursor = self.con.cursor()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS players (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                attempts INTEGER NOT NULL,
                guessed_number INTEGER NOT NULL
            )
        """)
        self.con.commit()

    def save_result(self, player_name, attempts, guess_number):
        self.cursor.execute("""
            INSERT INTO players (name, attempts, guessed_number)
            VALUES (?, ?, ?)
        """, (player_name, attempts, guess_number))
        self.con.commit()

    def fetch_results(self):
        self.cursor.execute("SELECT name, attempts, guessed_number FROM players")
        return self.cursor.fetchall()

    def clear_all(self):
        self.cursor.execute("DELETE FROM players")
        self.cursor.execute("DELETE FROM sqlite_sequence WHERE name='players'")
        self.con.commit()

    def close(self):
        self.con.close()


# ---------- class GuessNumberApp ----------
class GuessNumberApp:
    def __init__(self):
        self.current_player = None
        self.attempts = 0
        self.results_window = 0
        self.min_range = 1
        self.max_range = 100
        self.number = random.randint(self.min_range, self.max_range)

        # services
        self.sound = SoundManager()
        self.db = DatabaseManager()

        # tk UI
        self.root = tk.Tk()
        self.root.title("GUESS NUMBER..")
        self.root.geometry("400x350")
        self.root.configure(bg="#ffebee")

        self.select_player()
        self.build_ui()

    # ---- build UI ----
    def build_ui(self):
        self.frame = tk.Frame(self.root, bg="#ffebee")
        self.frame.pack(pady=10)

        self.title_label = tk.Label(self.frame, text="Guess Number",
                                    font=("Arial", 16, "bold"), bg="#ffebee", fg="#d32f2f")
        self.title_label.pack(pady=5)

        self.range_frame = tk.Frame(self.frame, bg="#ffebee")
        self.range_frame.pack(pady=5)

        self.min_label = tk.Label(self.range_frame, text="Min Number", font=("Arial", 10), bg="#ffebee")
        self.min_label.grid(row=0, column=0, padx=5)

        self.min_range_entry = tk.Entry(self.range_frame, width=5)
        self.min_range_entry.grid(row=0, column=1, padx=5)
        self.min_range_entry.insert(0, str(self.min_range))

        self.max_label = tk.Label(self.range_frame, text="Max Number", font=("Arial", 10), bg="#ffebee")
        self.max_label.grid(row=0, column=2, padx=5)

        self.max_range_entry = tk.Entry(self.range_frame, width=5)
        self.max_range_entry.grid(row=0, column=3, padx=5)
        self.max_range_entry.insert(0, str(self.max_range))

        self.set_range_button = ttk.Button(self.range_frame, text="Set range", command=self.set_range)
        self.set_range_button.grid(row=0, column=4, padx=5)

        self.instructions_label = tk.Label(self.frame, text="Try to guess number from selected range",
                                           font=("Arial", 10), bg="#ffebee")
        self.instructions_label.pack(pady=5)

        self.entry = tk.Entry(self.frame, font=("Arial", 12))
        self.entry.pack(pady=5)

        self.btn_frame = tk.Frame(self.frame, bg="#ffebee")
        self.btn_frame.pack(pady=5)

        self.guess_btn = ttk.Button(self.btn_frame, text="Submit", command=self.check_guess)
        self.guess_btn.pack(side=tk.LEFT, padx=5)

        self.new_player_btn = ttk.Button(self.btn_frame, text="Add New Player", command=self.add_new_player)
        self.new_player_btn.pack(side=tk.LEFT, padx=5)

        self.results_btn = ttk.Button(self.frame, text="Show Results", command=self.show_result)
        self.results_btn.pack(pady=5)

        self.clear_btn = ttk.Button(self.frame, text="Clear Results", command=self.clear_database)
        self.clear_btn.pack(pady=5)

        self.exit_btn = ttk.Button(self.frame, text="Exit Game", command=self.exit_game)
        self.exit_btn.pack(pady=5)

        self.result_label = tk.Label(self.frame, text="", font=("Arial", 12), bg="#ffebee", fg="#d32f2f")
        self.result_label.pack(pady=10)

    def play_sound(self):
        self.sound.play_sound()

    def check_guess(self):
        try:
            guess = int(self.entry.get())
        except ValueError:
            messagebox.showerror("Error", "Please, enter integer number")
            return

        self.attempts += 1
        self.result_label.config(text="")

        if guess < self.number:
            self.result_label.config(text="Guess Number is bigger")
        elif guess > self.number:
            self.result_label.config(text="Guess Number is lower")
        else:
            self.play_sound()
            messagebox.showinfo("CONGRATULATION!!!!",
                                f"You guessed number {self.number} for {self.attempts} attempts")
            self.save_result(self.current_player, self.attempts, self.number)
            self.reset_game()

    def reset_game(self):
        self.attempts = 0
        self.number = random.randint(self.min_range, self.max_range)
        self.result_label.config(text="")
        self.entry.delete(0, tk.END)

    def save_result(self, player_name, attempts, guess_number):
        self.db.save_result(player_name, attempts, guess_number)

    def set_range(self):
        try:
            self.min_range = int(self.min_range_entry.get())
            self.max_range = int(self.max_range_entry.get())
            if self.min_range >= self.max_range:
                raise ValueError("Min number must be less than number")
            self.number = random.randint(self.min_range, self.max_range)
            self.reset_game()
            messagebox.showinfo("Range set to", f" {self.min_range} - {self.max_range}. New Game started")
        except ValueError:
            messagebox.showerror("ERROR", "Select number in correct range")

    def select_player(self):
        self.current_player = simpledialog.askstring("Player", "Enter your name")
        if not self.current_player:
            messagebox.showwarning("WARNING!", "Player field shouldn't be empty")
            return self.select_player()

    def add_new_player(self):
        new_player_name = simpledialog.askstring("New Player", "Enter the name of new Player")
        if new_player_name:
            self.current_player = new_player_name
            messagebox.showinfo("New Player", "Player added")
            self.reset_game()
        else:
            messagebox.showwarning("WARNING!", "Player field shouldn't be empty")

    def show_result(self):
        if isinstance(self.results_window, tk.Toplevel) and self.results_window.winfo_exists():
            self.results_window.destroy()

        self.results_window = tk.Toplevel(self.root)
        self.results_window.title("Player Results")
        self.results_window.configure(bg="#e0f7fa")

        frame = tk.Frame(self.results_window, bg="#e0f7fa")
        frame.pack(padx=10, pady=10, fill="both", expand=True)

        tree = ttk.Treeview(frame, columns=("name", "attempts", "guessed_number"), show="headings", height=10)
        tree.heading("name", text="Player Name")
        tree.heading("attempts", text="Attempts")
        tree.heading("guessed_number", text="Guessed Number")

        tree.column("name", anchor=tk.CENTER, width=150)
        tree.column("attempts", anchor=tk.CENTER, width=100)
        tree.column("guessed_number", anchor=tk.CENTER, width=130)

        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscroll=scrollbar.set)

        tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        for row in self.db.fetch_results():
            tree.insert("", tk.END, values=row)

    def clear_database(self):
        if not messagebox.askyesno("Confirm", "Clear all saved results? This cannot be undone."):
            return
        try:
            self.db.clear_all()
            if isinstance(self.results_window, tk.Toplevel) and self.results_window.winfo_exists():
                self.results_window.destroy()
            messagebox.showinfo("Done", "All results cleared. New game starts fresh.")
            self.reset_game()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to clear DB:\n{e}")

    def exit_game(self):
        try:
            self.db.close()
        finally:
            self.root.destroy()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    GuessNumberApp().run()
