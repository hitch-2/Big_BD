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

        grid = tk.Frame(self.container)
        grid.pack(expand=True)

        buttons = [
            ("Дэшборд", self.show_dashboard),
            ("Столбчатая диаграмма", self.show_bar),
            ("Линейный график", self.show_line),
            ("Спарклайн", self.show_sparkline),
            ("Сводная таблица", self.show_table),
            ("Круговая диаграмма", self.show_pie),
        ]

        for i, (text, cmd) in enumerate(buttons):
            btn = ttk.Button(
                grid,
                text=text,
                command=cmd
            )
            btn.grid(
                row=i // 3,
                column=i % 3,
                padx=40,
                pady=40,
                ipadx=40,
                ipady=30
            )


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

    fig = Figure(figsize=(10, 4))
    ax = fig.add_subplot(111)

    canvas = FigureCanvasTkAgg(fig, self.container)
    canvas.get_tk_widget().pack(fill="both", expand=True)

    df_sorted = self.df.sort_values("date")
    values = df_sorted["value"].tolist()

    selected = []

    def redraw():
        ax.clear()
        if len(selected) == 2:
            v1, v2 = selected
            ax.plot(v1, linewidth=2)
            ax.plot(v2, linewidth=2)

            for i in range(len(v1)):
                if v1[i] >= v2[i]:
                    ax.fill_between(
                        [i, i],
                        v1[i],
                        v2[i],
                        color="green",
                        alpha=0.3
                    )
                else:
                    ax.fill_between(
                        [i, i],
                        v1[i],
                        v2[i],
                        color="red",
                        alpha=0.3)

            ax.axis("off")
        canvas.draw()

    table = tk.Frame(self.container)
    table.pack(pady=10)

    for i, val in enumerate(values):
        var = tk.BooleanVar()

        def toggle(v=values, idx=i, var=var):
            if var.get():
                selected.append(v)
            else:
                selected.remove(v)
            if len(selected) > 2:
                var.set(False)
                selected.pop()
            redraw()

        chk = ttk.Checkbutton(
            table,
            text=f"Значение {i + 1}: {val}",
            variable=var,
            command=toggle
        )
        chk.pack(anchor="w")

    self.back_button()


    # ---------- СВОДНАЯ ТАБЛИЦА ----------

    def show_table(self):
        self.clear()

    tree = ttk.Treeview(
        self.container,
        columns=("date", "category", "value"),
        show="headings"
    )

    tree.heading("date", text="Дата")
    tree.heading("category", text="Категория")
    tree.heading("value", text="Значение")

    for _, row in self.df.iterrows():
        tree.insert(
            "",
            "end",
            values=(row["date"], row["category"], row["value"])
        )

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

    def show_dashboard(self):
        self.clear()

        fig = Figure(figsize=(14, 8))

        ax1 = fig.add_subplot(221)
        ax2 = fig.add_subplot(222)
        ax3 = fig.add_subplot(223)
        ax4 = fig.add_subplot(224)

        grouped = self.df.groupby("category")["value"].sum()
        grouped.plot(kind="bar", ax=ax1, title="Bar")

        df_sorted = self.df.sort_values("date")
        for cat in df_sorted["category"].unique():
            data = df_sorted[df_sorted["category"] == cat]
            ax2.plot(data["date"], data["value"])
        ax2.set_title("Line")

        ax3.plot(df_sorted["value"])
        ax3.axis("off")
        ax3.set_title("Sparkline")

        ax4.pie(grouped.values, labels=grouped.index)
        ax4.set_title("Pie")

        canvas = FigureCanvasTkAgg(fig, self.container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

        self.back_button()
