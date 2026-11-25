"""
PS 29 - E-Commerce Sales Analyzer
Analyses online order data from a CSV file: total revenue, units sold,
best-selling products and category-wise revenue, with Matplotlib charts.

CSV columns: Order_ID, Product, Category, Quantity, Price
Revenue of a row = Quantity x Price

Usage:  python ecommerce_sales_analyzer.py [path/to/orders.csv]
"""

import os
import sys

import pandas as pd
import matplotlib.pyplot as plt

REQUIRED_COLUMNS = ["Order_ID", "Product", "Category", "Quantity", "Price"]


# --------------------------------------------------------------------------
# Loading and cleaning
# --------------------------------------------------------------------------
def load_and_clean(path):
    """Read the CSV with Pandas, skip invalid rows (with messages),
    remove duplicates and add a Revenue column. Returns a clean DataFrame."""
    if not os.path.isfile(path):
        print(f"Error: file '{path}' not found.")
        return None

    try:
        raw = pd.read_csv(path, dtype=str, keep_default_na=False,
                          skipinitialspace=True)
    except pd.errors.EmptyDataError:
        print("Error: the CSV file is empty.")
        return None
    except Exception as exc:  # unreadable / malformed file
        print(f"Error: could not read CSV ({exc}).")
        return None

    raw.columns = [c.strip() for c in raw.columns]
    missing = [c for c in REQUIRED_COLUMNS if c not in raw.columns]
    if missing:
        print(f"Error: missing column(s): {', '.join(missing)}")
        return None

    valid_rows = []
    for i, row in raw.iterrows():
        n = i + 1  # data row number (header not counted)
        order_id = row["Order_ID"].strip()
        product = row["Product"].strip()
        category = row["Category"].strip()
        qty_s = row["Quantity"].strip()
        price_s = row["Price"].strip()

        if not order_id or not product or not category:
            print(f"Row {n} skipped: missing Order_ID, Product or Category")
            continue

        # Quantity must be a positive whole number
        try:
            qty = int(qty_s)
        except ValueError:
            print(f"Row {n} skipped: invalid Quantity '{qty_s}'")
            continue
        if qty <= 0:
            print(f"Row {n} skipped: Quantity must be positive")
            continue

        # Price must be a positive number
        try:
            price = float(price_s)
        except ValueError:
            print(f"Row {n} skipped: invalid Price '{price_s}'")
            continue
        if price <= 0:
            print(f"Row {n} skipped: Price must be positive")
            continue

        valid_rows.append({"Order_ID": order_id, "Product": product,
                           "Category": category, "Quantity": qty,
                           "Price": price})

    df = pd.DataFrame(valid_rows, columns=REQUIRED_COLUMNS)

    # Remove duplicate orders (same Order_ID appearing more than once)
    before = len(df)
    df = df.drop_duplicates(subset="Order_ID", keep="first")
    removed = before - len(df)
    if removed:
        print(f"{removed} duplicate row(s) removed")

    df["Revenue"] = df["Quantity"] * df["Price"]
    return df.reset_index(drop=True)


# --------------------------------------------------------------------------
# Formatting helpers
# --------------------------------------------------------------------------
def fmt(x):
    """Show whole numbers without decimals (32500), else 2 decimals."""
    return str(int(x)) if float(x).is_integer() else f"{x:.2f}"


# --------------------------------------------------------------------------
# Features
# --------------------------------------------------------------------------
def show_summary(df):
    """Menu 1: total revenue, orders, units sold, top product."""
    total_revenue = df["Revenue"].sum()
    orders = df["Order_ID"].nunique()
    units = int(df["Quantity"].sum())
    by_product = df.groupby("Product")["Revenue"].sum().sort_values(ascending=False)
    top_name, top_rev = by_product.index[0], by_product.iloc[0]

    print(f"Total Revenue: {fmt(total_revenue)} | Orders: {orders}")
    print(f"Units sold: {units} | Top product: {top_name} ({fmt(top_rev)})")


def show_category_revenue(df):
    """Menu 2: category-wise revenue with percentages and a pie chart."""
    by_cat = df.groupby("Category")["Revenue"].sum().sort_values(ascending=False)
    total = by_cat.sum()
    for cat, rev in by_cat.items():
        print(f"{cat}: {fmt(rev)} ({rev / total * 100:.2f}%)")

    plt.figure(figsize=(6, 6))
    plt.pie(by_cat.values, labels=by_cat.index, autopct="%.2f%%", startangle=90)
    plt.title("Category-wise Revenue")
    plt.tight_layout()
    plt.savefig("category_revenue_pie.png")
    print("Pie chart 'Category-wise Revenue' displayed")
    plt.show()


def show_top_products(df):
    """Menu 3: top 5 products by revenue with a bar chart."""
    top5 = (df.groupby("Product")["Revenue"].sum()
              .sort_values(ascending=False).head(5))
    print("Top 5 products by revenue:")
    for rank, (prod, rev) in enumerate(top5.items(), start=1):
        print(f"  {rank}. {prod}: {fmt(rev)}")

    plt.figure(figsize=(8, 5))
    bars = plt.bar(top5.index, top5.values, color="steelblue")
    plt.bar_label(bars, labels=[fmt(v) for v in top5.values])
    plt.title("Top 5 Products by Revenue")
    plt.xlabel("Product")
    plt.ylabel("Revenue")
    plt.tight_layout()
    plt.savefig("top_products_bar.png")
    print("Bar chart 'Top 5 Products by Revenue' displayed")
    plt.show()


# --------------------------------------------------------------------------
# Main menu
# --------------------------------------------------------------------------
def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "orders.csv"
    df = load_and_clean(path)
    if df is None:
        return
    if df.empty:
        print("No valid orders found.")
        return

    while True:
        print("\n===== E-Commerce Sales Analyzer =====")
        print("1. Summary (revenue, orders, units, top product)")
        print("2. Category-wise revenue (pie chart)")
        print("3. Top 5 products (bar chart)")
        print("4. Exit")
        choice = input("Enter choice: ").strip()

        if choice == "1":
            show_summary(df)
        elif choice == "2":
            show_category_revenue(df)
        elif choice == "3":
            show_top_products(df)
        elif choice == "4":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please enter 1-4.")


if __name__ == "__main__":
    main()
