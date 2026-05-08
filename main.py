import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
import os

class CurrencyConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("Currency Converter")
        self.root.geometry("600x500")

        # API ключ (замените на свой)
        self.api_key = "YOUR_API_KEY"
        self.history_file = "history.json"
        self.history = self.load_history()

        self.setup_ui()

    def setup_ui(self):
        # Выбор валюты "из"
        ttk.Label(self.root, text="Из валюты:").grid(row=0, column=0, padx=10, pady=10)
        self.from_currency = ttk.Combobox(self.root, values=self.get_currencies())
        self.from_currency.grid(row=0, column=1, padx=10, pady=10)

        # Выбор валюты "в"
        ttk.Label(self.root, text="В валюту:").grid(row=1, column=0, padx=10, pady=10)
        self.to_currency = ttk.Combobox(self.root, values=self.get_currencies())
        self.to_currency.grid(row=1, column=1, padx=10, pady=10)

        # Поле ввода суммы
        ttk.Label(self.root, text="Сумма:").grid(row=2, column=0, padx=10, pady=10)
        self.amount_entry = ttk.Entry(self.root)
        self.amount_entry.grid(row=2, column=1, padx=10, pady=10)

        # Кнопка конвертации
        self.convert_btn = ttk.Button(self.root, text="Конвертировать", command=self.convert_currency)
        self.convert_btn.grid(row=3, column=0, columnspan=2, pady=20)

        # Таблица истории
        self.create_history_table()

    def get_currencies(self):
        # Список популярных валют
        return ['USD', 'EUR', 'GBP', 'JPY', 'CAD', 'AUD', 'CHF', 'CNY', 'RUB', 'UAH']

    def create_history_table(self):
        columns = ('ID', 'From', 'To', 'Amount', 'Result', 'Rate')
        self.tree = ttk.Treeview(self.root, columns=columns, show='headings')

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=80)

        self.tree.grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky='nsew')

        # Полосы прокрутки
        scrollbar = ttk.Scrollbar(self.root, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.grid(row=4, column=2, sticky='ns')
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Заполняем таблицу историей
        self.refresh_history()

    def convert_currency(self):
        try:
            # Валидация ввода
            amount = float(self.amount_entry.get())
            if amount <= 0:
                messagebox.showerror("Ошибка", "Сумма должна быть положительным числом")
                return

            from_curr = self.from_currency.get()
            to_curr = self.to_currency.get()

            if not from_curr or not to_curr:
                messagebox.showerror("Ошибка", "Выберите валюты")
                return

            # Получение курса через API
            rate = self.get_exchange_rate(from_curr, to_curr)
            if rate is None:
                return

            result = amount * rate

            # Сохранение в историю
            record = {
                'id': len(self.history) + 1,
                'from': from_curr,
                'to': to_curr,
                'amount': amount,
                'result': result,
                'rate': rate
            }
            self.history.append(record)
            self.save_history()

            # Обновление таблицы
            self.refresh_history()

            messagebox.showinfo("Результат", f"{amount} {from_curr} = {result:.2f} {to_curr}")

        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректную сумму")

    def get_exchange_rate(self, from_curr, to_curr):
        try:
            url = f"https://api.exchangerate-api.com/v4/latest/{from_curr}"
            response = requests.get(url)
            data = response.json()

            if response.status_code == 200 and to_curr in data['rates']:
                return data['rates'][to_curr]
            else:
                messagebox.showerror("Ошибка", "Не удалось получить курс валюты")
                return None
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка подключения: {e}")
            return None

    def save_history(self):
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(self.history, f, indent=2, ensure_ascii=False)

    def load_history(self):
        if os.path.exists(self.history_file):
            with open(self.history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []

    def refresh_history(self):
        # Очистка таблицы
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Заполнение данными
        for record in self.history:
            self.tree.insert('', 'end', values=(
                record['id'],
                record['from'],
                record['to'],
                f"{record['amount']:.2f}",
                f"{record['result']:.2f}",
                f"{record['rate']:.4f}"
            ))

if __name__ == "__main__":
    root = tk.Tk()
    app = CurrencyConverter(root)
    root.mainloop()
