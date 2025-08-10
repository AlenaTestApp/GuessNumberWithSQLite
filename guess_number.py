import random
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import pygame
import sqlite3


pygame.mixer.init()
con = sqlite3.connect("Guess_Game.db")
cursor = con.cursor()
cursor.execute("""
        CREATE TABLE IF NOT EXISTS players (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        attempts INTEGER NOT NULL,
        guessed_number INTEGER NOT NULL
        )       
""")
con.commit()
current_player = None
attempts = 0
results_window = 0
min_range = 1
max_range = 100
number = random.randint(min_range, max_range)


def play_sound():
    pygame.mixer.music.load("sounds/GAME-003.WAV")
    pygame.mixer.music.play()


def check_guess():
    try:
        guess = int(entry.get())
        global attempts
        attempts += 1
        result_label.config(text="")
        if guess < number:
            result_label.config(text="Guess Number is bigger")
        elif guess > number:
            result_label.config(text="Guess Number is lower")
        else:
            play_sound()
            messagebox.showinfo("CONGRATULATION!!!!", f"You guessed number {number} for {attempts} attempts")
            save_result(current_player, attempts, number)
            reset_game()
    except ValueError:
        messagebox.showerror("Error", "Please, enter integer number")


def reset_game():
    global number, attempts
    attempts = 0
    number = random.randint(min_range, max_range)
    result_label.config(text="")
    entry.delete(0, tk.END)


def save_result(player_name, attempts, guess_number):
    cursor.execute("""
    INSERT INTO players (name, attempts, guessed_number)
    VALUES (?, ?, ?)
    """, (player_name, attempts, guess_number))
    con.commit()


def set_range():
    global min_range, max_range, number
    try:
        min_range = int(min_range_entry.get())
        max_range = int(max_range_entry.get())
        if min_range >= max_range:
            raise ValueError("Min number must be less than number")
        number = random.randint(min_range, max_range)
        reset_game()
        messagebox.showinfo("Range set to", f" {min_range} - {max_range}. New Game started")
    except ValueError:
        messagebox.showerror("ERROR", "Select number in correct range")


def select_player():
    global current_player
    current_player = simpledialog.askstring("Player", "Enter your name")
    if not current_player:
        messagebox.showwarning("WARNING!", "Player field shouldn't be empty")
        select_player()


def add_new_player():
    global current_player
    new_player_name = simpledialog.askstring("New Player", "Enter the name of new Player")
    if new_player_name:
        current_player = new_player_name
        messagebox.showinfo("New Player", "Player added")
        reset_game()
    else:
        messagebox.showwarning("WARNING!", "Player field shouldn't be empty")


def show_result():

    """Отображает результаты всех игроков из базы данных."""
    global results_window, root, cursor

    # Проверка существования окна
    if isinstance(results_window, tk.Toplevel) and results_window.winfo_exists():
        results_window.destroy()

    results_window = tk.Toplevel(root)
    results_window.title("Результаты игроков")
    results_window.configure(bg="#e0f7fa")

    frame = tk.Frame(results_window, bg="#e0f7fa")
    frame.pack(padx=10, pady=10, fill="both", expand=True)

    tree = ttk.Treeview(frame, columns=("name", "attempts", "guessed_number"), show="headings", height=10)
    tree.heading("name", text="Имя игрока")
    tree.heading("attempts", text="Попытки")
    tree.heading("guessed_number", text="Загаданное число")

    tree.column("name", anchor=tk.CENTER, width=150)
    tree.column("attempts", anchor=tk.CENTER, width=100)
    tree.column("guessed_number", anchor=tk.CENTER, width=130)

    scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    tree.configure(yscroll=scrollbar.set)

    tree.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    cursor.execute("SELECT name, attempts, guessed_number FROM players")
    for row in cursor.fetchall():
        tree.insert("", tk.END, values=row)


def clear_database():
    global results_window
    if not messagebox.askyesno("Confirm", "Clear all saved results? This cannot be undone."):
        return
    try:
        cursor.execute("DELETE FROM players")
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='players'")
        con.commit()
        if isinstance(results_window, tk.Toplevel) and results_window.winfo_exists():
            results_window.destroy()
        messagebox.showinfo("Done", "All results cleared. New game starts fresh.")
        reset_game()
    except Exception as e:
        messagebox.showerror("Error", f"Failed to clear DB:\n{e}")


def exit_game():
    con.close()
    root.destroy()


# main window
root = tk.Tk()
root.title("GUESS NUMBER..")
root.geometry("400x350")
root.configure(bg="#ffebee")
select_player()

# Layer 1
frame = tk.Frame(root, bg="#ffebee")
frame.pack(pady=10)
title_label = tk.Label(frame, text="Guess Number", font=("Arial", 16, "bold"), bg="#ffebee", fg="#d32f2f")
title_label.pack(pady=5)
# Layer 2
range_frame = tk.Frame(frame, bg="#ffebee")
range_frame.pack(pady=5)
# Min Number Label
min_label = tk.Label(range_frame, text="Min Number", font=("Arial", 10), bg="#ffebee")
min_label.grid(row=0, column=0, padx=5)
# Min Number Input Entry
min_range_entry = tk.Entry(range_frame, width=5)
min_range_entry.grid(row=0, column=1, padx=5)
min_range_entry.insert(0, str(min_range))
# Max Number Label
max_label = tk.Label(range_frame, text="Max Number", font=("Arial", 10), bg="#ffebee")
max_label.grid(row=0, column=2, padx=5)
# Max Number Input Entry
max_range_entry = tk.Entry(range_frame, width=5)
max_range_entry.grid(row=0, column=3, padx=5)
max_range_entry.insert(0, str(max_range))
# Button to update range
set_range_button = ttk.Button(range_frame, text="Set range", command=set_range)
set_range_button.grid(row=0, column=4, padx=5)
# Instructions
instructions_label = tk.Label(frame, text="Try to guess number from selected range",
                              font=("Arial", 10), bg="#ffebee")
instructions_label.pack(pady=5)
# Entry field
entry = tk.Entry(frame, font=("Arial", 12))
entry.pack(pady=5)
# Button's Frame
btn_frame = tk.Frame(frame, bg="#ffebee")
btn_frame.pack(pady=5)
# Button SUBMIT
guess_btn = ttk.Button(btn_frame, text="Submit", command=check_guess)
guess_btn.pack(side=tk.LEFT, padx=5)
# New Player button
# new_player_btn = tk.Button(btn_frame, text="Add New Player", command=add_new_player, font=("Arial", 10),
#                       bg="#1976d2", fg="white")
new_player_btn = ttk.Button(btn_frame, text="Add New Player", command=add_new_player)
new_player_btn.pack(side=tk.LEFT, padx=5)
# Results button
results_btn = ttk.Button(frame, text="Show Results", command=show_result)
results_btn.pack(pady=5)
# EXIT button
exit_btn = ttk.Button(frame, text="Exit Game", command=exit_game)
exit_btn.pack(pady=5)
# Results Label
result_label = tk.Label(frame, text="", font=("Arial", 12), bg="#ffebee", fg="#d32f2f")
result_label.pack(pady=10)
# Clear DB
clear_btn = ttk.Button(frame, text="Clear Results", command=clear_database)
clear_btn.pack(pady=5)


root.mainloop()



