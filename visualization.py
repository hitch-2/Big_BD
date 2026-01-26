import pandas as pd
import matplotlib.pyplot as plt
from data_module import DataManager

def choose_visualization():
    print("Выберите тип визуализации:")
    print("1 — Столбчатая диаграмма")
    print("2 — Линейный график")
    print("3 — Спарклайн")
    print("4 — Сводная таблица")
    print("5 — Круговая диаграмма")
    return input("Ваш выбор: ")

def bar_chart(df):
    grouped = df.groupby("category")["value"].sum()
    grouped.plot(kind="bar")
    plt.show()

def line_chart(df):
    df_sorted = df.sort_values("date")
    plt.plot(df_sorted["date"], df_sorted["value"])
    plt.show()

def sparkline(df):
    df_sorted = df.sort_values("date")
    plt.plot(df_sorted["value"])
    plt.axis("off")
    plt.show()

def pivot_table(df):
    pivot = pd.pivot_table(
        df,
        values="value",
        index="category",
        aggfunc="sum"
    )
    print(pivot)

def pie_chart(df):
    grouped = df.groupby("category")["value"].sum()
    grouped.plot(kind="pie", autopct="%1.1f%%")
    plt.ylabel("")
    plt.show()

def main():
    manager = DataManager(
        mongo_uri="mongodb+srv://abi:bkCVTo9fgYvhQN23@cluster0.gs3dt6o.mongodb.net/?authSource=admin&retryWrites=true&w=majority",
        db_name="analytics_db",
        collection_name="sales_data"
    )


    df = manager.get_data()

    choice = choose_visualization()

    match choice:
        case "1":
            bar_chart(df)
        case "2":
            line_chart(df)
        case "3":
            sparkline(df)
        case "4":
            pivot_table(df)
        case "5":
            pie_chart(df)
        case _:
            print("Неверный выбор")

if __name__ == "__main__":
    main()
