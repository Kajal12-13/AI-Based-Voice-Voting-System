import tkinter as tk

def button_vote_ui():
    result = {"vote": None}

    def select_vote(choice):
        result["vote"] = choice
        root.destroy()

    root = tk.Tk()
    root.title("Vote Selection")
    root.geometry("300x250")

    label = tk.Label(root, text="Select Your Vote", font=("Arial", 14))
    label.pack(pady=10)

    tk.Button(root, text="1 - BJP", width=20, height=2,
              command=lambda: select_vote("BJP")).pack(pady=5)

    tk.Button(root, text="2 - Congress", width=20, height=2,
              command=lambda: select_vote("Congress")).pack(pady=5)

    tk.Button(root, text="3 - NOTA", width=20, height=2,
              command=lambda: select_vote("NOTA")).pack(pady=5)

    root.mainloop()
    return result["vote"]