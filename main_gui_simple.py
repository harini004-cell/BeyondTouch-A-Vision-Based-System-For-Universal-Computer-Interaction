# main_gui_simple.py (small)
import tkinter as tk, threading, os
def run(script):
    threading.Thread(target=lambda: os.system(f'python "{script}"'), daemon=True).start()

root = tk.Tk(); root.title("BeyondTouch"); root.geometry("360x220")
tk.Button(root, text="Hand", width=20, command=lambda: run("hand_controller.py")).pack(pady=8)
tk.Button(root, text="Eye", width=20, command=lambda: run("eye_use_reference.py")).pack(pady=8)
tk.Button(root, text="Voice", width=20, command=lambda: run("voice_fallback_final.py")).pack(pady=8)
tk.Button(root, text="Exit", width=10, command=root.destroy).pack(pady=12)
root.mainloop()
