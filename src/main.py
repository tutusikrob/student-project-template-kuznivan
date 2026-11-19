import tkinter as tk
from tkinter import messagebox, ttk


class RepairApp:
    """Приложение для учёта заявок на ремонт телефонов (сервисный центр «MyСмарт»)."""

    STATUSES = ["Принят", "В ремонте", "Готов", "Выдан"]

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("MyСмарт — Учёт заявок на ремонт телефонов (Спринт 1)")
        self.root.geometry("860x500")
        self.root.minsize(760, 440)

        # Хранилище заявок в оперативной памяти (список словарей)
        self.orders: list[dict] = []
        self.next_id: int = 1

        self._build_ui()

    def _build_ui(self) -> None:
        """Создание элементов интерфейса (базовая версия Спринта 1)."""
        header = tk.Label(
            self.root,
            text="Сервисный центр «MyСмарт» — Журнал заявок на ремонт",
            font=("Segoe UI", 13, "bold"),
            pady=10,
        )
        header.pack(fill=tk.X)

        # Таблица заявок
        table_frame = tk.Frame(self.root, padx=12, pady=4)
        table_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("id", "model", "issue", "status")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=12)
        self.tree.heading("id", text="№ заявки")
        self.tree.heading("model", text="Модель телефона")
        self.tree.heading("issue", text="Описание поломки")
        self.tree.heading("status", text="Статус")

        self.tree.column("id", width=90, anchor=tk.CENTER)
        self.tree.column("model", width=220, anchor=tk.W)
        self.tree.column("issue", width=390, anchor=tk.W)
        self.tree.column("status", width=120, anchor=tk.CENTER)

        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Форма добавления новой заявки
        form_frame = tk.LabelFrame(self.root, text="Новая заявка", padx=12, pady=10)
        form_frame.pack(fill=tk.X, padx=12, pady=10)

        tk.Label(form_frame, text="Модель телефона:*").grid(row=0, column=0, sticky=tk.W, pady=4)
        self.model_entry = tk.Entry(form_frame, width=32)
        self.model_entry.grid(row=0, column=1, sticky=tk.W, padx=(6, 18), pady=4)

        tk.Label(form_frame, text="Описание поломки:*").grid(row=0, column=2, sticky=tk.W, pady=4)
        self.issue_entry = tk.Entry(form_frame, width=42)
        self.issue_entry.grid(row=0, column=3, sticky=tk.W, padx=(6, 12), pady=4)

        add_btn = tk.Button(
            form_frame,
            text="Добавить заявку",
            command=self.add_order,
            bg="#2e7d32",
            fg="white",
            padx=12,
            pady=4,
        )
        add_btn.grid(row=0, column=4, padx=4)

    def refresh_table(self) -> None:
        """Обновление содержимого таблицы на экране."""
        for item in self.tree.get_children():
            self.tree.delete(item)
        for order in self.orders:
            self.tree.insert(
                "",
                tk.END,
                values=(order["id"], order["model"], order["issue"], order["status"]),
            )

    def add_order(self) -> None:
        """Добавление новой заявки с проверкой обязательных полей."""
        model = self.model_entry.get().strip()
        issue = self.issue_entry.get().strip()

        if not model or not issue:
            messagebox.showwarning(
                "Ошибка ввода",
                "Пожалуйста, заполните оба обязательных поля: «Модель телефона» и «Описание поломки».",
            )
            return

        new_order = {
            "id": self.next_id,
            "model": model,
            "issue": issue,
            "status": "Принят",
        }
        self.orders.append(new_order)
        self.next_id += 1

        self.model_entry.delete(0, tk.END)
        self.issue_entry.delete(0, tk.END)
        self.refresh_table()


if __name__ == "__main__":
    root = tk.Tk()
    app = RepairApp(root)
    root.mainloop()
