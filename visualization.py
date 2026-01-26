import tkinter as tk
from tkinter import ttk
import pandas as pd

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from data_module import DataManager


class App(tk.Tk):
    def __init__(self, df):
        super().__init__()

        self.df = df
        self.title("Data Visualization")
        self.state("zoomed")

        self.container = tk.Frame(self)
        self.container.pack(fill="both", expand=True)

        self.show_main_menu()

    def clear(self):
        for widget in self.container.winfo_children():
            widget.destroy()

    # ---------- ГЛАВНОЕ МЕНЮ ----------

    def show_main_menu(self):
        self.clear()

        buttons = [
            ("Столбчатая диаграмма", self.show_bar),
            ("Линейный график", self.show_line),
            ("Спарклайн", self.show_sparkline),
            ("Сводная таблица", self.show_table),
            ("Круговая диаграмма", self.show_pie),
        ]

        for text, command in buttons:
            btn = ttk.Button(self.container, text=text, command=command)
            btn.pack(pady=20, ipadx=30, ipady=10)

    def back_button(self):
        ttk.Button(
            self.container,
            text="Назад",
            command=self.show_main_menu
        ).pack(pady=15)

    # ---------- СТОЛБЧАТАЯ ДИАГРАММА ----------

    def show_bar(self):
        self.clear()

        fig = Figure(figsize=(10, 6))
        ax = fig.add_subplot(111)

        grouped = self.df.groupby("category")["value"].sum()
        ax.bar(grouped.index, grouped.values)

        canvas = FigureCanvasTkAgg(fig, master=self.container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

        self.back_button()

    # ---------- ЛИНЕЙНЫЙ ГРАФИК ----------

    def show_line(self):
        self.clear()

        fig = Figure(figsize=(10, 6))
        ax = fig.add_subplot(111)

        df_sorted = self.df.sort_values("date")
        categories = df_sorted["category"].unique()
        lines = {}

        for cat in categories:
            data = df_sorted[df_sorted["category"] == cat]
            line, = ax.plot(
                data["date"],
                data["value"],
                marker="o",
                label=cat
            )
            lines[cat] = line

        ax.legend()

        canvas = FigureCanvasTkAgg(fig, master=self.container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

        controls = tk.Frame(self.container)
        controls.pack(side="bottom", pady=10)

        vars = {}

        def toggle(category):
            lines[category].set_visible(vars[category].get())
            canvas.draw()

        for cat in categories:
            vars[cat] = tk.BooleanVar(value=True)
            chk = ttk.Checkbutton(
                controls,
                text=cat,
                variable=vars[cat],
                command=lambda c=cat: toggle(c)
            )
            chk.pack(side="left", padx=10)

        self.back_button()

    # ---------- СПАРКЛАЙН ----------

    def show_sparkline(self):
        self.clear()

        fig = Figure(figsize=(10, 3))
        ax = fig.add_subplot(111)

        df_sorted = self.df.sort_values("date")
        ax.plot(df_sorted["value"])
        ax.axis("off")

        canvas = FigureCanvasTkAgg(fig, master=self.container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

        self.back_button()

    # ---------- СВОДНАЯ ТАБЛИЦА ----------

    def show_table(self):
        self.clear()

        pivot = pd.pivot_table(
            self.df,
            values="value",
            index="category",
            aggfunc="sum"
        )

        tree = ttk.Treeview(
            self.container,
            columns=("category", "value"),
            show="headings"
        )
        tree.heading("category", text="Категория")
        tree.heading("value", text="Сумма")

        for cat, row in pivot.iterrows():
            tree.insert("", "end", values=(cat, row["value"]))

        tree.pack(fill="both", expand=True)

        self.back_button()

    # ---------- КРУГОВАЯ ДИАГРАММА ----------

    def show_pie(self):
        self.clear()

        fig = Figure(figsize=(6, 6))
        ax = fig.add_subplot(111)

        grouped = self.df.groupby("category")["value"].sum()
        ax.pie(grouped.values, labels=grouped.index, autopct="%1.1f%%")

        canvas = FigureCanvasTkAgg(fig, master=self.container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

        self.back_button()


# ---------- ТОЧКА ВХОДА ----------

if __name__ == "__main__":
    manager = DataManager(
        mongo_uri="mongodb+srv://abi:bkCVTo9fgYvhQN23@cluster0.gs3dt6o.mongodb.net/?authSource=admin",
        db_name="analytics_db",
        collection_name="sales_data"
    )

    df = manager.get_data()
    app = App(df)
    app.mainloop()
