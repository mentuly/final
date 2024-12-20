from gui.gui import disk_usage_analyzer
import tkinter as tk

def main():
    root = tk.Tk()
    app = disk_usage_analyzer(root)
    root.mainloop() # запуск гуішки

if __name__ == "__main__":
    main()