from application import Application

import tkinter as tk
import os

def main():
    root = tk.Tk()
    root.title("光滑极限量规辅助设计工具")
    width = 741
    height = 424
    x = (root.winfo_screenwidth() - width) // 2
    y = (root.winfo_screenheight() - height) // 2
    root.geometry(f'{width}x{height}+{x}+{y}')
    root.resizable(False, False)
    root.iconbitmap(
        os.path.join(
            os.path.dirname(__file__),
            'icon.ico'
        )
    )
    Application(master=root)
    root.mainloop()

if __name__ == "__main__":
    main()