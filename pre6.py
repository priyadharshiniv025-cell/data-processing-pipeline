# ==============================
# MINI SALES ANALYSIS - Full automation
# Input: CSV / Excel / JSON -> Output: CSV or Excel (unique file per run)
# ==============================

import os
import re
import math
from datetime import datetime

import pandas as pd

import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt

import tkinter as tk
from tkinter import filedialog, messagebox


def log(message: str, summary_widget: tk.Text | None = None):
    print(message)
    if summary_widget is not None:
        summary_widget.insert(tk.END, message + "\n")
        summary_widget.see(tk.END)


def clean_product_name(name: str) -> str:
    name = str(name).strip()
    name = re.sub(r"[^A-Za-z0-9 ]+", "", name)
    name = re.sub(r"\s+", " ", name)
    return name.title()


def load_dataset_auto(path: str) -> pd.DataFrame:
    ext = os.path.splitext(path)[1].lower()
    if ext == ".csv":
        return pd.read_csv(path)
    elif ext in (".xls", ".xlsx"):
        return pd.read_excel(path)
    elif ext == ".json":
        return pd.read_json(path)
    else:
        raise ValueError(f"Unsupported file type: {ext}. Use CSV, Excel, or JSON.")


def auto_find_columns(df: pd.DataFrame):
    cols = list(df.columns)

    # 1) DATE: prefer existing datetime column
    datetime_cols = df.select_dtypes(include=["datetime64[ns]", "datetimetz"]).columns.tolist()
    if datetime_cols:
        date_col = datetime_cols[0]
    else:
        date_col = None
        best_score = -1.0
        for col in cols:
            try:
                s = df[col].dropna().astype(str).head(300)
                parsed = pd.to_datetime(s, errors="coerce")
                score = float(parsed.notna().mean())
            except Exception:
                score = 0.0
            if score > best_score and score > 0.3:
                best_score = score
                date_col = col
        if date_col is None:
            date_col = cols[0]

    # 2) NUMERIC (quantity/price), skip ID-like
    numeric_cols = df.select_dtypes(include=["number"]).columns
    numeric_info = {}
    for col in numeric_cols:
        s = pd.to_numeric(df[col], errors="coerce")
        non_na = s.dropna()
        if len(non_na) == 0:
            continue
        nunique = non_na.nunique()
        is_id_like = (
            pd.api.types.is_integer_dtype(non_na)
            and nunique >= 0.8 * len(non_na)
            and float(non_na.min()) == 1
            and float(non_na.max()) == len(df)
        )
        if is_id_like:
            continue
        numeric_info[col] = {
            "mean": float(non_na.mean()),
            "unique_ratio": nunique / len(non_na),
        }

    if not numeric_info:
        quantity_col = numeric_cols[0] if len(numeric_cols) > 0 else cols[0]
        price_col = numeric_cols[1] if len(numeric_cols) > 1 else quantity_col
    else:
        quantity_col = min(
            numeric_info.items(),
            key=lambda kv: (kv[1]["unique_ratio"], kv[1]["mean"]),
        )[0]
        price_col = max(numeric_info.items(), key=lambda kv: kv[1]["mean"])[0]

    # 3) PRODUCT: text, medium cardinality
    obj_cols = df.select_dtypes(include=["object", "string"]).columns.tolist()
    if not obj_cols:
        remaining = [c for c in cols if c not in {date_col, quantity_col, price_col}]
        product_col = remaining[0] if remaining else cols[0]
    else:
        best_col = obj_cols[0]
        best_score = 1e9
        for col in obj_cols:
            s = df[col].astype(str)
            ratio = s.nunique() / max(len(s), 1)
            score = abs(ratio - 0.2)
            if score < best_score:
                best_score = score
                best_col = col
        product_col = best_col

    return date_col, product_col, quantity_col, price_col


def run_sales_analysis(
    path: str,
    summary_widget: tk.Text | None = None,
    output_format: str = "csv",
) -> str:
    log(f"Selected file: {path}", summary_widget)

    df = load_dataset_auto(path)
    df.columns = df.columns.str.strip()
    log("\nColumn Names: " + str(list(df.columns)), summary_widget)

    date_col, product_col, quantity_col, price_col = auto_find_columns(df)
    log("\nAuto-detected: Date=%s, Product=%s, Qty=%s, Price=%s" % (
        date_col, product_col, quantity_col, price_col), summary_widget)

    print(df.head())
    print(df.info())

    if product_col in df.columns:
        df[product_col] = df[product_col].apply(clean_product_name)

    df[quantity_col] = pd.to_numeric(df[quantity_col], errors="coerce")
    df[price_col] = pd.to_numeric(df[price_col], errors="coerce")

    # Date: safe handling (already datetime or parse)
    if pd.api.types.is_datetime64_any_dtype(df[date_col]):
        pass
    else:
        df[date_col] = pd.to_datetime(df[date_col], errors="coerce", dayfirst=True)

    df = df.dropna(subset=[quantity_col, price_col, product_col])
    valid_date = df[date_col].notna()
    if valid_date.any():
        df = df.loc[valid_date].copy()
    df = df.drop_duplicates()

    if len(df) == 0:
        raise ValueError("No rows left after cleaning.")

    df["Total"] = df[quantity_col] * df[price_col]
    if date_col in df.columns and df[date_col].notna().any():
        df["Month"] = df[date_col].dt.month
    else:
        df["Month"] = 1

    total_revenue = df["Total"].sum()
    log("\nTotal Revenue: %s (rounded: %s)" % (total_revenue, math.ceil(total_revenue)), summary_widget)

    top_product = df.groupby(product_col)[quantity_col].sum().sort_values(ascending=False)
    revenue_by_product = df.groupby(product_col)["Total"].sum().sort_values(ascending=False)
    monthly_sales = df.groupby("Month")["Total"].sum().sort_index()

    print(top_product)
    print(revenue_by_product)
    print(monthly_sales)

    if len(monthly_sales) > 0 and monthly_sales.mean() > 0:
        log("Best month vs avg: %s%%" % math.ceil(monthly_sales.max() / monthly_sales.mean() * 100), summary_widget)

    # Matplotlib (TkAgg)
    try:
        if len(revenue_by_product) > 0:
            plt.figure(figsize=(8, 4))
            revenue_by_product.plot(kind="bar")
            plt.title("Revenue by Product")
            plt.xlabel(product_col)
            plt.ylabel("Revenue")
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.show()
    except Exception as e:
        log("Bar chart skip: %s" % e, summary_widget)

    try:
        if len(monthly_sales) > 0:
            plt.figure(figsize=(8, 4))
            monthly_sales.plot(kind="line", marker="o")
            plt.title("Monthly Sales Trend")
            plt.xlabel("Month")
            plt.ylabel("Total Revenue")
            plt.tight_layout()
            plt.show()
    except Exception as e:
        log("Line chart skip: %s" % e, summary_widget)

    # Save: CSV or Excel — name from imported file (e.g. January_Sales.xlsx → January_Sales_cleaned_...)
    output_dir = os.path.dirname(path)
    if not output_dir:
        output_dir = os.getcwd()
    os.makedirs(output_dir, exist_ok=True)
    imported_basename = os.path.splitext(os.path.basename(path))[0]  # e.g. "January_Sales"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base = imported_basename + "_cleaned_" + timestamp  # different name per file, unique per run
    if output_format.lower() == "excel":
        output_path = os.path.join(output_dir, base + ".xlsx")
        try:
            df.to_excel(output_path, index=False, engine="openpyxl")
        except Exception as e:
            log("Excel save failed (%s), saving as CSV instead." % e, summary_widget)
            output_path = os.path.join(output_dir, base + ".csv")
            df.to_csv(output_path, index=False)
    else:
        output_path = os.path.join(output_dir, base + ".csv")
        df.to_csv(output_path, index=False)

    log("\nDone. Saved: %s" % output_path, summary_widget)
    return output_path


def select_file_and_run(summary_widget: tk.Text, output_format_var: tk.StringVar):
    file_path = filedialog.askopenfilename(
        title="Select data file",
        filetypes=[
            ("Data files", "*.csv *.xls *.xlsx *.json"),
            ("CSV", "*.csv"),
            ("Excel", "*.xls *.xlsx"),
            ("JSON", "*.json"),
            ("All", "*.*"),
        ],
    )
    if not file_path:
        return
    summary_widget.delete("1.0", tk.END)
    fmt = output_format_var.get().strip().lower() or "csv"
    if fmt not in ("csv", "excel"):
        fmt = "csv"
    try:
        out = run_sales_analysis(file_path, summary_widget, output_format=fmt)
        messagebox.showinfo("Success", "Analysis done.\nSaved: %s" % out)
    except Exception as e:
        messagebox.showerror("Error", str(e))


def main():
    root = tk.Tk()
    root.title("Mini Sales Analysis (Automatic)")
    root.geometry("680x480")

    tk.Label(root, text="Mini Sales Analysis Tool", font=("Arial", 14)).pack(pady=10)

    fmt_frame = tk.Frame(root)
    fmt_frame.pack(pady=5)
    tk.Label(fmt_frame, text="Save result as:").pack(side=tk.LEFT, padx=5)
    output_format_var = tk.StringVar(value="CSV")
    for label, val in [("CSV", "csv"), ("Excel", "excel")]:
        tk.Radiobutton(
            fmt_frame,
            text=label,
            variable=output_format_var,
            value=val,
        ).pack(side=tk.LEFT, padx=5)

    summary_text = tk.Text(root, height=14, width=82, wrap="word")
    summary_text.pack(padx=10, pady=5)

    tk.Button(
        root,
        text="Select Data File and Run Analysis",
        font=("Arial", 10),
        command=lambda: select_file_and_run(summary_text, output_format_var),
    ).pack(pady=10)

    root.mainloop()


if __name__ == "__main__":
    main()
