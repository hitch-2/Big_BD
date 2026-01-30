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

        canvas = tk.Canvas(main_frame, highlightthickness=0, bg="#f5f6f7")
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, style="TFrame")

        # create window and keep its width equal to canvas width to avoid horizontal scrolling
        canvas_window_id = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

        def on_scrollable_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        def on_canvas_configure(event):
            # make inner frame width match canvas width (prevents horizontal scroll)
            canvas.itemconfig(canvas_window_id, width=event.width)

        scrollable_frame.bind("<Configure>", on_scrollable_configure)
        canvas.bind("<Configure>", on_canvas_configure)

        canvas.configure(yscrollcommand=scrollbar.set, bg="#f5f6f7")

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        # Grid layout с 2 колонками — убрано первое большое окно, всё в пределах одной ширины
        grid = ttk.Frame(scrollable_frame)
        grid.pack(fill="both", expand=True, padx=12, pady=12)

        # Row 0: линейный по категориям (лево) + круговая (право)
        box_line = self._create_box(grid, "Линейный по категориям")
        box_line.grid(row=0, column=0, sticky="nsew", padx=6, pady=6)
        self._mini_line(box_line)

        right_pie = self._create_box(grid, "Распределение по категориям")
        right_pie.grid(row=0, column=1, sticky="nsew", padx=6, pady=6)
        fig_p = Figure(figsize=(4, 3), tight_layout=True)
        ax_p = fig_p.add_subplot(111)
        g = self.df.groupby("category")["value"].sum()
        ax_p.pie(g.values, labels=g.index, autopct="%1.0f%%", textprops={"fontsize": 8})
        canvas_p = FigureCanvasTkAgg(fig_p, right_pie)
        canvas_p.get_tk_widget().pack(fill="both", expand=True)

        # Row 1: три мини-графика (в две колонки — spark и bar)
        box_spark = self._create_box(grid, "Сравнение (спарклайн)")
        box_spark.grid(row=1, column=0, sticky="nsew", padx=6, pady=6)
        self._mini_spark(box_spark)  # используется новая версия спарклайна

        box_bar = self._create_box(grid, "Столбчатая")
        box_bar.grid(row=1, column=1, sticky="nsew", padx=6, pady=6)
        self._mini_bar(box_bar)

        # Row 2: таблица статистики на всю ширину
        table_box = self._create_box(grid, "Статистика / Топ по категориям")
        table_box.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=6, pady=6)
        self._mini_table(table_box)

        # Конфигурация сетки — равномерное распределение, без горизонтального скролла
        for c in range(2):
            grid.columnconfigure(c, weight=1, uniform="col")
        grid.rowconfigure(0, weight=1)
        grid.rowconfigure(1, weight=1)
        grid.rowconfigure(2, weight=0)

        self.back_button()

    def _chart_box(self, parent, title, func, row, col):
        box = self._create_box(parent, title)
        box.grid(row=row, column=col, sticky="nsew", padx=5, pady=5)
        func(box)

    def _create_box(self, parent, title):
        box = ttk.LabelFrame(parent, text=title, padding=10)
        return box

    def _draw(self, fig):
        canvas = FigureCanvasTkAgg(fig, self.container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def _mini_bar(self, parent):
        fig = Figure(figsize=(5, 3), tight_layout=True)
        ax = fig.add_subplot(111)
        self.df.groupby("category")["value"].sum().plot(kind="bar", ax=ax)
        ax.set_title("По категориям")
        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def _mini_line(self, parent):
        fig = Figure(figsize=(5, 3), tight_layout=True)
        ax = fig.add_subplot(111)
        for cat, d in self.df.groupby("category"):
            ax.plot(d.sort_values("date")["date"], d["value"], label=cat)
        ax.set_title("Временной ряд")
        ax.legend(fontsize=8)
        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def _mini_spark(self, parent):
        """
        Обновлённый компактный спарклайн для дэшборда:
        - два комбобокса для выбора категорий
        - выравнивание по дате (merge) для корректного заполнения цветом
        """
        top = ttk.Frame(parent)
        top.pack(fill="x", padx=2, pady=4)

        categories = sorted(self.df["category"].unique())
        cb1 = ttk.Combobox(top, values=categories, state="readonly", width=18)
        cb2 = ttk.Combobox(top, values=categories, state="readonly", width=18)
        cb1.pack(side="left", padx=(2, 6))
        cb2.pack(side="left", padx=(2, 6))

        fig = Figure(figsize=(4, 1.6), tight_layout=True)
        ax = fig.add_subplot(111)
        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.get_tk_widget().pack(fill="both", expand=True)

        def redraw():
            ax.clear()
            a = cb1.get()
            b = cb2.get()
            if not a or not b:
                canvas.draw()
                return

            d1 = self.df[self.df["category"] == a][["date", "value"]].sort_values("date")
            d2 = self.df[self.df["category"] == b][["date", "value"]].sort_values("date")

            # выравниваем по дате - outer merge и заполнение вперед/0
            merged = pd.merge(d1, d2, on="date", how="outer", suffixes=("_a", "_b")).sort_values("date")
            merged["value_a"] = merged["value_a"].ffill().fillna(0)
            merged["value_b"] = merged["value_b"].ffill().fillna(0)

            y1 = merged["value_a"].values
            y2 = merged["value_b"].values
            x = range(len(y1))

            ax.plot(x, y1, color="#2E86AB", linewidth=1.4)
            ax.plot(x, y2, color="#F39C12", linewidth=1.2, linestyle="--")

            ax.fill_between(x, y1, y2, where=(y1 >= y2), color="#2ECC71", alpha=0.25, interpolate=True)
            ax.fill_between(x, y1, y2, where=(y1 < y2), color="#E74C3C", alpha=0.25, interpolate=True)

            ax.set_xticks([])
            ax.set_yticks([])
            ax.set_title(f"{a} vs {b}", fontsize=9)
            canvas.draw()

        # выставляем дефолтные значения и рисуем
        if len(categories) >= 2:
            cb1.set(categories[0])
            cb2.set(categories[1])
            redraw()

        cb1.bind("<<ComboboxSelected>>", lambda e: redraw())
        cb2.bind("<<ComboboxSelected>>", lambda e: redraw())

    def _mini_table(self, parent):
        """
        Компактная таблица: топ-10 категорий с суммой значений и общие метрики.
        Сделана как Treeview, чтобы текст не обрезался и был выровнен.
        """
        info_frame = ttk.Frame(parent)
        info_frame.pack(fill="x", padx=4, pady=(4, 8))

        stats = [
            f"Всего записей: {len(self.df)}",
            f"Дата от: {self.df['date'].min().date()}",
            f"Дата до: {self.df['date'].max().date()}",
            f"Категорий: {self.df['category'].nunique()}",
        ]

        for stat in stats:
            ttk.Label(info_frame, text=stat, font=("Arial", 9)).pack(side="left", padx=8)

        # Treeview с топ-10 категорий
        tree_frame = ttk.Frame(parent)
        tree_frame.pack(fill="both", expand=True, padx=4, pady=4)

        tree = ttk.Treeview(tree_frame, columns=("category", "sum"), show="headings", height=6)
        tree.heading("category", text="Категория")
        tree.heading("sum", text="Сумма")
        tree.column("category", anchor="w", width=300)
        tree.column("sum", anchor="e", width=120)

        grouped = self.df.groupby("category")["value"].sum().sort_values(ascending=False).head(10)
        for cat, val in grouped.items():
            tree.insert("", "end", values=(cat, f"{val:.2f}"))

        tree.pack(fill="both", expand=True)


if __name__ == "__main__":
    manager = DataManager(
        mongo_uri="mongodb+srv://abi:bkCVTo9fgYvhQN23@cluster0.gs3dt6o.mongodb.net/",
        db_name="analytics_db",
        collection_name="sales_data"
    )

    df = manager.get_data()
    App(df).mainloop()
