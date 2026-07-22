import pyodbc, pandas as pd, os, json

SERVER = "ANGELO-DESKTOP"
DATABASE = "SupplyChain_DW"
OUT = os.path.join(os.getcwd(), "demo_data")

conn = pyodbc.connect(
    f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={SERVER};DATABASE={DATABASE};"
    "Trusted_Connection=yes;TrustServerCertificate=yes;",
    autocommit=True
)

queries = {
    "kpi_summary": "SELECT * FROM analytics.v_kpi_summary ORDER BY year, month",
    "kpi_otif_detail": "SELECT * FROM analytics.v_kpi_otif_detail ORDER BY year, month",
    "kpi_profitability": "SELECT * FROM analytics.v_kpi_profitability ORDER BY year, month",
    "adv_trends": "SELECT * FROM analytics.v_adv_trends ORDER BY year_month, market",
}

os.makedirs(OUT, exist_ok=True)

for name, sql in queries.items():
    df = pd.read_sql(sql, conn)
    path = os.path.join(OUT, f"{name}.csv")
    df.to_csv(path, index=False, encoding="utf-8")
    print(f"OK {name}.csv -> {len(df)} rows, {len(df.columns)} cols")

meta = {}
for name in queries:
    df = pd.read_csv(os.path.join(OUT, f"{name}.csv"))
    meta[name] = {"rows": len(df), "columns": list(df.columns)}

with open(os.path.join(OUT, "_manifest.json"), "w") as f:
    json.dump(meta, f, indent=2, default=str)

conn.close()
total = sum(v["rows"] for v in meta.values())
print(f"Done. {total} total rows in {len(meta)} files")
