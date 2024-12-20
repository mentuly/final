import os
import psutil
import tkinter as tk
from datetime import datetime
from tkinter import ttk, messagebox, filedialog
from disk_analysis.visualizer import plot_usage

class disk_usage_analyzer:
    def __init__(self, root):
        # стоврення самого бекграунду і назви програми
        self.root = root
        self.root.title("Аналізатор використання диску")
        self.root.geometry("500x300")
        self.set_dark_mode()
        self.create_widgets()

    def set_dark_mode(self):
        # налаштування темного режиму
        self.root.configure(bg='#2E2E2E')  # темний фон для вікна
        self.dark_text = "#000000"  # світлий текст для темного фону
        self.dark_button = "#3A3A3A"  # текстова кнопка
        self.dark_button_active = "#575757"  # активна кнопка

        # оновлення всіх віджетів для темного режиму
        style = ttk.Style()
        style.configure("TButton", background=self.dark_button, foreground=self.dark_text, font=("Arial", 10))
        style.map("TButton", background=[("active", self.dark_button_active)])

        style.configure("TLabel", background='#2E2E2E', foreground=self.dark_text, font=("Arial", 10))
        style.configure("TCombobox", fieldbackground=self.dark_button, background=self.dark_button, foreground=self.dark_text)

    def create_widgets(self):
        # створення віджетів
        self.disk_label = ttk.Label(self.root, text="Виберіть диск:")
        self.disk_label.grid(row=0, column=0, padx=10, pady=10)

        # отримання всіх доступних дисків
        self.disk_options = [f"{disk.device}" for disk in psutil.disk_partitions()]
        self.disk_combobox = ttk.Combobox(self.root, values=self.disk_options, state="readonly")
        self.disk_combobox.set(self.disk_options[0] if self.disk_options else "C:/")
        self.disk_combobox.grid(row=0, column=1, padx=10, pady=10)

        # кнопка вибору папки
        self.folder_button = ttk.Button(self.root, text="Сканувати папку", command=self.open_folder_dialog)
        self.folder_button.grid(row=0, column=2, padx=10, pady=10)

        self.folder_path = tk.StringVar(value="")  # збереження шляху до папки

        # типи для вибору діаграм
        self.chart_label = ttk.Label(self.root, text="Вибір типу діаграми:")
        self.chart_label.grid(row=2, column=0, padx=10, pady=10)

        self.chart_types = ["pie", "bar", "online_pie", "online_bar", "online_line"]
        self.chart_combobox = ttk.Combobox(self.root, values=self.chart_types, state="readonly")
        self.chart_combobox.set("pie")
        self.chart_combobox.grid(row=2, column=1, padx=10, pady=10)

        # кнопка для аналізу
        self.analyze_button = ttk.Button(self.root, text="Аналізувати", command=self.analyze_disk)
        self.analyze_button.grid(row=3, column=0, columnspan=2, pady=20)

    def open_folder_dialog(self):
        # викликання менюшки для вибору папки та параметрів фільтру
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.folder_path.set(folder_selected)
            self.show_folder_analysis_dialog(folder_selected)

    def show_folder_analysis_dialog(self, folder_selected):
        # стоврення вікна для аналізу папки з фільтром
        folder_analysis_window = tk.Toplevel(self.root)
        folder_analysis_window.title("Аналіз папки")
        folder_analysis_window.configure(bg='#2E2E2E')

        # поле вибору папки
        folder_label = ttk.Label(folder_analysis_window, text="Обрана папка:")
        folder_label.grid(row=0, column=0, padx=10, pady=10)
        folder_entry = ttk.Entry(folder_analysis_window, textvariable=self.folder_path, width=40, state="readonly")
        folder_entry.grid(row=0, column=1, padx=10, pady=10)

        # фільтр
        sort_label = ttk.Label(folder_analysis_window, text="Сортувати за:")
        sort_label.grid(row=1, column=0, padx=10, pady=10)

        # параметри фільтру
        self.sort_options = ["Розмір", "Дата створення"]
        sort_combobox = ttk.Combobox(folder_analysis_window, values=self.sort_options, state="readonly")
        sort_combobox.set("Розмір")
        sort_combobox.grid(row=1, column=1, padx=10, pady=10)

        # кнопка для аналізу папки
        analyze_button = ttk.Button(folder_analysis_window, text="Аналізувати", command=lambda: self.analyze_folder(folder_selected, sort_combobox.get(), folder_analysis_window))
        analyze_button.grid(row=2, column=0, columnspan=2, pady=10)

        # кнопка для видалення файлу
        delete_button = ttk.Button(folder_analysis_window, text="Видалити", command=lambda: self.delete_selected_item(folder_analysis_window))
        delete_button.grid(row=3, column=0, columnspan=2, pady=10)

    def analyze_folder(self, folder, sort_by, folder_analysis_window):
        # аналізує папку та показує після фільтру
        data = self.scan_folder(folder, sort_by)

        # очищення попередніх результатів
        for widget in folder_analysis_window.winfo_children():
            widget.destroy()

        # виведення результатів
        result_text = tk.Text(folder_analysis_window, height=10, width=50)
        result_text.grid(row=0, column=0, padx=10, pady=10)

        # запис результату в текстове поле яке буде як раз користувач бачити
        if sort_by == "Розмір":
            result_text.insert(tk.END, "\n".join([f"{folder}: {size:.2f} МБ" for folder, size in data.items()]))
        elif sort_by == "Дата створення":
            # це для дати стоврення нашої вказаної папки
            folder_creation_date = self.get_folder_creation_date(folder)
            result_text.insert(tk.END, f"Дата створення вибраної папки: {folder_creation_date}")
        
        result_text.config(state=tk.DISABLED)

    def scan_folder(self, folder, sort_by):
        # сканування папки саме папки, без підпапок
        folder_data = []

        try:
            # перебираються тільки файли і папки в поточній директорії
            for item in os.listdir(folder):
                item_path = os.path.join(folder, item)
                if os.path.isfile(item_path):
                    # розмір
                    size = os.stat(item_path).st_size / (1024**2)  # розмір у мб
                    folder_data.append({
                        "name": item,
                        "size": size,
                        "date": datetime.fromtimestamp(os.stat(item_path).st_ctime)
                    })
                elif os.path.isdir(item_path):
                    # розмір папки (без врахування вмісту підпапок)
                    size = sum(
                        os.stat(os.path.join(item_path, f)).st_size
                        for f in os.listdir(item_path)
                        if os.path.isfile(os.path.join(item_path, f))
                    ) / (1024**2)  # розмір у мб
                    folder_data.append({
                        "name": item,
                        "size": size,
                        "date": datetime.fromtimestamp(os.stat(item_path).st_ctime)
                    })
        except Exception as e:
            messagebox.showerror("Помилка", f"Не вдалося проаналізувати папку: {str(e)}")

        # фільтри
        if sort_by == "Розмір":
            folder_data.sort(key=lambda x: x["size"], reverse=True)
        elif sort_by == "Дата створення":
            folder_data.sort(key=lambda x: x["date"], reverse=True)

        # поверенння результату в словник
        return {
            item["name"]: item["size"] if sort_by == "Розмір" else item["date"].strftime("%Y-%m-%d %H:%M:%S")
            for item in folder_data
        }

    def get_folder_creation_date(self, folder_path):
        # отримання дати створенння папки
        stats = os.stat(folder_path)
        creation_time = datetime.fromtimestamp(stats.st_ctime)
        return creation_time.strftime("%Y-%m-%d %H:%M:%S")

    def delete_selected_item(self, folder_analysis_window):
        # видаляє вибраний файйл
        selected_item = filedialog.askopenfilename(title="Виберіть файл для видалення", initialdir=self.folder_path.get())
        if selected_item:
            try:
                if os.path.isdir(selected_item):
                    os.rmdir(selected_item)
                    messagebox.showinfo("Видалено", f"Папку {selected_item} успішно видалено.")
                else:
                    os.remove(selected_item)
                    messagebox.showinfo("Видалено", f"Файл {selected_item} успішно видалено.")
            except Exception as e:
                messagebox.showerror("Помилка", f"Не вдалося видалити: {str(e)}")
            
            # оновлення видалення реза=ультату
            folder_analysis_window.destroy()
            self.show_folder_analysis_dialog(self.folder_path.get())

    def analyze_disk(self):
        # аналіз вибраного диску
        selected_disk = self.disk_combobox.get()
        selected_chart_type = self.chart_combobox.get()

        # так би мовити витягуємо данні з диска щоб отримати інформацію
        disk_usage = psutil.disk_usage(selected_disk)
        data = {
            "Загальний": disk_usage.total / (1024**3),  # розмір у гб
            "Вільно": disk_usage.free / (1024**3)
        }

        # викликаємо функцію для побудови діаграми
        try:
            plot_usage(data, selected_chart_type)
        except Exception as e:
            messagebox.showerror("Помилка", f"Сталася помилка: {str(e)}")