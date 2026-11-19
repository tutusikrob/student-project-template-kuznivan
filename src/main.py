import tkinter as tk
from tkinter import messagebox, ttk


class RepairApp:
    """Приложение для учёта заявок на ремонт телефонов (сервисный центр «MyСмарт»)."""

    STATUSES = ["Принят", "В ремонте", "Готов", "Выдан"]

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("MyСмарт — Учёт заявок на ремонт телефонов (v1.0)")
        self.root.geometry("920x580")
        self.root.minsize(820, 500)

        self.orders: list[dict] = []
        self.next_id: int = 1
        self.selected_order_id: int | None = None

        self._build_ui()
        self.update_stats()

    def _build_ui(self) -> None:
        header = tk.Label(
            self.root,
            text="Сервисный центр «MyСмарт» — Учёт заявок на ремонт телефонов",
            font=("Segoe UI", 13, "bold"),
            pady=8,
        )
        header.pack(fill=tk.X)

        filter_frame = tk.LabelFrame(self.root, text="Поиск и фильтрация", padx=10, pady=8)
        filter_frame.pack(fill=tk.X, padx=12, pady=(0, 8))

        tk.Label(filter_frame, text="Поиск (№ или модель):").pack(side=tk.LEFT)
        self.search_entry = tk.Entry(filter_frame, width=28)
        self.search_entry.pack(side=tk.LEFT, padx=(6, 16))
        self.search_entry.bind("<Return>", lambda _event: self.refresh_table())

        tk.Label(filter_frame, text="Статус:").pack(side=tk.LEFT)
        self.status_filter = ttk.Combobox(
            filter_frame,
            values=["Все"] + self.STATUSES,
            state="readonly",
            width=15,
        )
        self.status_filter.current(0)
        self.status_filter.pack(side=tk.LEFT, padx=(6, 16))
        self.status_filter.bind("<<ComboboxSelected>>", lambda _event: self.refresh_table())

        tk.Button(filter_frame, text="Найти", command=self.refresh_table, width=10).pack(side=tk.LEFT, padx=4)
        tk.Button(filter_frame, text="Сбросить", command=self.reset_filters, width=10).pack(side=tk.LEFT, padx=4)

        table_frame = tk.Frame(self.root, padx=12, pady=2)
        table_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("id", "model", "issue", "status")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=11)
        self.tree.heading("id", text="№ заявки")
        self.tree.heading("model", text="Модель телефона")
        self.tree.heading("issue", text="Описание поломки")
        self.tree.heading("status", text="Статус")

        self.tree.column("id", width=90, anchor=tk.CENTER)
        self.tree.column("model", width=230, anchor=tk.W)
        self.tree.column("issue", width=420, anchor=tk.W)
        self.tree.column("status", width=130, anchor=tk.CENTER)

        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.bind("<<TreeviewSelect>>", self.on_select_order)

        form_frame = tk.LabelFrame(self.root, text="Карточка заявки", padx=12, pady=10)
        form_frame.pack(fill=tk.X, padx=12, pady=8)

        self.selected_info_label = tk.Label(
            form_frame,
            text="Выбранная заявка: не выбрана (режим добавления новой)",
            fg="#1565c0",
            font=("Segoe UI", 9, "bold"),
        )
        self.selected_info_label.grid(row=0, column=0, columnspan=4, sticky=tk.W, pady=(0, 8))

        tk.Label(form_frame, text="Модель телефона:*").grid(row=1, column=0, sticky=tk.W, pady=4)
        self.model_entry = tk.Entry(form_frame, width=32)
        self.model_entry.grid(row=1, column=1, sticky=tk.W, padx=(6, 20), pady=4)

        tk.Label(form_frame, text="Описание поломки:*").grid(row=1, column=2, sticky=tk.W, pady=4)
        self.issue_entry = tk.Entry(form_frame, width=45)
        self.issue_entry.grid(row=1, column=3, sticky=tk.W, padx=(6, 0), pady=4)

        btn_frame = tk.Frame(form_frame)
        btn_frame.grid(row=2, column=0, columnspan=4, sticky=tk.W, pady=(10, 0))

        tk.Button(btn_frame, text="Добавить заявку", command=self.add_order, bg="#2e7d32", fg="white", padx=10, pady=4).pack(side=tk.LEFT, padx=(0, 8))
        tk.Button(btn_frame, text="Сохранить изменения", command=self.update_order, bg="#1565c0", fg="white", padx=10, pady=4).pack(side=tk.LEFT, padx=8)
        tk.Button(btn_frame, text="Следующий статус", command=self.advance_status, bg="#ef6c00", fg="white", padx=10, pady=4).pack(side=tk.LEFT, padx=8)
        tk.Button(btn_frame, text="Удалить заявку", command=self.delete_order, bg="#c62828", fg="white", padx=10, pady=4).pack(side=tk.LEFT, padx=8)
        tk.Button(btn_frame, text="Очистить форму", command=self.clear_form, padx=10, pady=4).pack(side=tk.LEFT, padx=8)

        self.stats_label = tk.Label(self.root, text="", relief=tk.SUNKEN, anchor=tk.W, padx=12, pady=5, font=("Segoe UI", 9))
        self.stats_label.pack(side=tk.BOTTOM, fill=tk.X)
    def _find_order_by_id(self, order_id: int) -> dict | None:
        for order in self.orders:
            if order["id"] == order_id:
                return order
        return None

    def update_stats(self) -> None:
        total = len(self.orders)
        counts = {status: 0 for status in self.STATUSES}
        for order in self.orders:
            if order["status"] in counts:
                counts[order["status"]] += 1

        self.stats_label.config(
            text=(
                f"Всего заявок: {total}   |   "
                f"Принят: {counts['Принят']}   |   "
                f"В ремонте: {counts['В ремонте']}   |   "
                f"Готов: {counts['Готов']}   |   "
                f"Выдан: {counts['Выдан']}"
            )
        )

    def refresh_table(self) -> None:
        query = self.search_entry.get().strip().lower()
        selected_status = self.status_filter.get()

        for item in self.tree.get_children():
            self.tree.delete(item)

        for order in self.orders:
            if selected_status != "Все" and order["status"] != selected_status:
                continue
            if query:
                if not (query in str(order["id"]) or query in order["model"].lower()):
                    continue
            self.tree.insert("", tk.END, values=(order["id"], order["model"], order["issue"], order["status"]))

        self.update_stats()

    def reset_filters(self) -> None:
        self.search_entry.delete(0, tk.END)
        self.status_filter.current(0)
        self.refresh_table()

    def clear_form(self) -> None:
        self.selected_order_id = None
        self.selected_info_label.config(text="Выбранная заявка: не выбрана (режим добавления новой)")
        self.model_entry.delete(0, tk.END)
        self.issue_entry.delete(0, tk.END)
        for item in self.tree.selection():
            self.tree.selection_remove(item)

    def on_select_order(self, _event: tk.Event) -> None:
        selection = self.tree.selection()
        if not selection:
            return
        values = self.tree.item(selection[0], "values")
        order = self._find_order_by_id(int(values[0]))
        if not order:
            return

        self.selected_order_id = order["id"]
        self.selected_info_label.config(text=f"Выбранная заявка: № {order['id']} | Текущий статус: «{order['status']}»")
        self.model_entry.delete(0, tk.END)
        self.model_entry.insert(0, order["model"])
        self.issue_entry.delete(0, tk.END)
        self.issue_entry.insert(0, order["issue"])

    def add_order(self) -> None:
        model = self.model_entry.get().strip()
        issue = self.issue_entry.get().strip()
        if not model or not issue:
            messagebox.showwarning("Ошибка ввода", "Заполните обязательные поля: «Модель телефона» и «Описание поломки».")
            return

        self.orders.append({"id": self.next_id, "model": model, "issue": issue, "status": "Принят"})
        self.next_id += 1
        self.clear_form()
        self.refresh_table()

    def update_order(self) -> None:
        if self.selected_order_id is None:
            messagebox.showwarning("Внимание", "Сначала выберите заявку в таблице для редактирования.")
            return

        model = self.model_entry.get().strip()
        issue = self.issue_entry.get().strip()
        if not model or not issue:
            messagebox.showwarning("Ошибка ввода", "Поля «Модель телефона» и «Описание поломки» не могут быть пустыми.")
            return

        order = self._find_order_by_id(self.selected_order_id)
        if order:
            order["model"] = model
            order["issue"] = issue
            self.refresh_table()
            messagebox.showinfo("Готово", f"Заявка № {order['id']} успешно обновлена.")

    def advance_status(self) -> None:
        if self.selected_order_id is None:
            messagebox.showwarning("Внимание", "Сначала выберите заявку в таблице.")
            return

        order = self._find_order_by_id(self.selected_order_id)
        if not order:
            return

        idx = self.STATUSES.index(order["status"])
        if idx >= len(self.STATUSES) - 1:
            messagebox.showwarning("Ограничение статуса", f"Заявка № {order['id']} уже имеет конечный статус «Выдан».")
            return

        order["status"] = self.STATUSES[idx + 1]
        self.selected_info_label.config(text=f"Выбранная заявка: № {order['id']} | Текущий статус: «{order['status']}»")
        self.refresh_table()

    def delete_order(self) -> None:
        if self.selected_order_id is None:
            messagebox.showwarning("Внимание", "Сначала выберите заявку в таблице для удаления.")
            return

        order = self._find_order_by_id(self.selected_order_id)
        if not order:
            return

        if messagebox.askyesno("Подтверждение удаления", f"Удалить заявку № {order['id']} ({order['model']})?"):
            self.orders = [item for item in self.orders if item["id"] != order["id"]]
            self.clear_form()
            self.refresh_table()


if __name__ == "__main__":
    root = tk.Tk()
    app = RepairApp(root)
    root.mainloop()
