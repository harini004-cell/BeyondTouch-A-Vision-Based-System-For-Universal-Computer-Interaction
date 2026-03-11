# vk_gui.py
import tkinter as tk, pyautogui
KEY_LAYOUT = [["q","w","e","r","t","y","u","i","o","p"],
              ["a","s","d","f","g","h","j","k","l"],
              ["z","x","c","v","b","n","m",",",".","/"]]
def make_key(parent,k):
    def on_click():
        if k=="space": pyautogui.write(" ")
        elif k=="enter": pyautogui.press("enter")
        elif k=="bksp": pyautogui.press("backspace")
        else: pyautogui.write(k)
    return tk.Button(parent,text=k.upper(),width=4,height=2,command=on_click)
def build():
    root=tk.Tk(); root.title("Virtual Keyboard")
    for row in KEY_LAYOUT:
        f=tk.Frame(root); f.pack()
        for k in row: make_key(f,k).pack(side="left",padx=2,pady=2)
    ctrl=tk.Frame(root); ctrl.pack(pady=6)
    for k in ["space","enter","bksp"]:
        make_key(ctrl,k).pack(side="left",padx=6)
    root.mainloop()

if __name__ == "__main__":
    build()
