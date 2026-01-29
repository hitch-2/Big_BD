import tkinter as tk
from tkinter import ttk
import pandas as pd

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from data_module import DataManager


class App(tk.Tk):
    def __init__(self, df):
        super().__init__()

        self.df = df.copy()
        self.df["date"] = pd.to_datetime(self.df["date"])

        self.title("Analytics Dashboard")
        self.state("zoomed")

        self.container = tk.Frame(self, bg="#f5f6f7")
        self.container.pack(fill="both", expand=True)

        self.show_main_menu()

    def clear(self):
        for w in self.container.winfo_children():
            w.destroy()

    def back_button(self):
        ttk.Button(
            self.container,
            text="← Назад",
            command=self.show_main_menu
        ).pack(pady=15)

    # ---------------- MAIN MENU ----------------

    def show_main_menu(self):
        self.clear()

        grid = tk.Frame(self.container, bg="#f5f6f7")
        grid.pack(expand=True)

        buttons = [
            ("Дэшборд", self.show_dashboard),
            ("Столбчатая", self.show_bar),
            ("Линейный", self.show_line),
            ("Спарклайн", self.show_sparkline),
            ("Сводная таблица", self.show_table),
            ("Круговая", self.show_pie),
        ]

        for i, (text, cmd) in enumerate(buttons):
            ttk.Button(
                grid,
                text=text,
                command=cmd,
                width=25
            ).grid(
                row=i // 3,
                column=i % 3,
                padx=30,
                pady=30,
                ipady=25
            )

    # ---------------- BAR ----------------

    def show_bar(self):
        self.clear()

        fig = Figure(figsize=(10, 6))
        ax = fig.add_subplot(111)

        grouped = self.df.groupby("category")["value"].sum()
        ax.bar(grouped.index, grouped.values)

        self._draw(fig)
        self.back_button()

    # ---------------- LINE ----------------

    def show_line(self):
        self.clear()

        fig = Figure(figsize=(10, 6))
        ax = fig.add_subplot(111)

        for cat, data in self.df.groupby("category"):
            ax.plot(
                data.sort_values("date")["date"],
                data.sort_values("date")["value"],
                marker="o",
                label=cat
            )

        ax.legend()
        self._draw(fig)
        self.back_button()

    # ---------------- SPARKLINE ----------------

    def show_sparkline(self):
        self.clear()

        top = tk.Frame(self.container)
        top.pack(fill="x", pady=10)

        categories = sorted(self.df["category"].unique())

        cb1 = ttk.Combobox(top, values=categories, state="readonly")
        cb2 = ttk.Combobox(top, values=categories, state="readonly")
        cb1.pack(side="left", padx=10)
        cb2.pack(side="left", padx=10)

        fig = Figure(figsize=(10, 4))
        ax = fig.add_subplot(111)
        canvas = FigureCanvasTkAgg(fig, self.container)
        canvas.get_tk_widget().pack(fill="both", expand=True)

        def redraw():
            if not cb1.get() or not cb2.get():
                return

            ax.clear()

            d1 = self.df[self.df["category"] == cb1.get()].sort_values("date")
            d2 = self.df[self.df["category"] == cb2.get()].sort_values("date")

            y1 = d1["value"].values
            y2 = d2["value"].values

            ax.plot(y1, linewidth=2)
            ax.plot(y2, linewidth=2, linestyle="--")

            ax.fill_between(
                range(len(y1)),
                y1,
                y2,
                where=(y1 >= y2),
                color="green",
                alpha=0.3,
                interpolate=True
            )
            ax.fill_between(
                range(len(y1)),
                y1,
                y2,
                where=(y1 < y2),
                color="red",
                alpha=0.3,
                interpolate=True
            )

            ax.axis("off")
            canvas.draw()

        cb1.bind("<<ComboboxSelected>>", lambda e: redraw())
        cb2.bind("<<ComboboxSelected>>", lambda e: redraw())

        self.back_button()

    # ---------------- TABLE ----------------

    def show_table(self):
        self.clear()

        tree = ttk.Treeview(
            self.container,
            columns=("id", "date", "category", "value"),
            show="headings"
        )

        tree.heading("id", text="ID")
        tree.heading("date", text="Дата")
        tree.heading("category", text="Категория")
        tree.heading("value", text="Значение")

        tree.column("id", width=60)
        tree.column("date", width=120)
        tree.column("category", width=200)
        tree.column("value", width=120)

        for i, row in self.df.iterrows():
            tree.insert(
                "",
                "end",
                values=(i + 1, row["date"].date(), row["category"], row["value"])
            )

        tree.pack(fill="both", expand=True, padx=20, pady=20)
        self.back_button()

    # ---------------- PIE ----------------

    def show_pie(self):
        self.clear()

        fig = Figure(figsize=(6, 6))
        ax = fig.add_subplot(111)

        grouped = self.df.groupby("category")["value"].sum()
        ax.pie(grouped.values, labels=grouped.index, autopct="%1.1f%%")

        self._draw(fig)
        self.back_button()

    # ---------------- DASHBOARD ----------------

    def show_dashboard(self):
        self.clear()

        main_frame = ttk.Frame(self.container)
        main_frame.pack(fill="both", expand=True)

        canvas = tk.Canvas(main_frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Binding mouse wheel
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        def block(title):
            box = ttk.LabelFrame(scrollable_frame, text=title)
            box.pack(fill="x", padx=20, pady=15)
            return box

        self._mini_bar(block("Bar"))
        self._mini_line(block("Line"))
        self._mini_spark(block("Sparkline"))
        self._mini_pie(block("Pie"))
        self._mini_table(block("Table"))

        self.back_button()

    # ---------------- HELPERS ----------------

    def _draw(self, fig):
        canvas = FigureCanvasTkAgg(fig, self.container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def _mini_bar(self, parent):
        fig = Figure(figsize=(5, 3))
        ax = fig.add_subplot(111)
        self.df.groupby("category")["value"].sum().plot(kind="bar", ax=ax)
        FigureCanvasTkAgg(fig, parent).get_tk_widget().pack()

    def _mini_line(self, parent):
        fig = Figure(figsize=(5, 3))
        ax = fig.add_subplot(111)
        for cat, d in self.df.groupby("category"):
            ax.plot(d["date"], d["value"])
        FigureCanvasTkAgg(fig, parent).get_tk_widget().pack()

    def _mini_spark(self, parent):
        fig = Figure(figsize=(5, 2))
        ax = fig.add_subplot(111)
        ax.plot(self.df.sort_values("date")["value"])
        ax.axis("off")
        FigureCanvasTkAgg(fig, parent).get_tk_widget().pack()

    def _mini_pie(self, parent):
        fig = Figure(figsize=(4, 4))
        ax = fig.add_subplot(111)
        g = self.df.groupby("category")["value"].sum()
        ax.pie(g.values)
        FigureCanvasTkAgg(fig, parent).get_tk_widget().pack()

    def _mini_table(self, parent):
        lbl = ttk.Label(parent, text=f"Всего записей: {len(self.df)}")
        lbl.pack(pady=10)


if __name__ == "__main__":
    manager = DataManager(
        mongo_uri="mongodb+srv://abi:***@cluster0.gs3dt6o.mongodb.net/",
        db_name="analytics_db",
        collection_name="sales_data"
    )

    df = manager.get_data()
    App(df).mainloop()
