"""
Vérifie et corrige le schéma de bronze.orders pour qu'il corresponde au CSV.
"""
import pyodbc

conn_str = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=ANGELO-DESKTOP;"
    "DATABASE=SupplyChain_DW;"
    "Trusted_Connection=yes;"
    "TrustServerCertificate=yes;"
)

conn = pyodbc.connect(conn_str, autocommit=True)
cursor = conn.cursor()

# Vérifier les colonnes existantes
cursor.execute("""
    SELECT COLUMN_NAME, DATA_TYPE
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA = 'bronze' AND TABLE_NAME = 'orders'
    ORDER BY ORDINAL_POSITION
""")
existing = {row[0] for row in cursor.fetchall()}

print(f"Colonnes existantes dans bronze.orders: {len(existing)}")

# Colonnes du CSV (dans l'ordre)
csv_columns = [
    "Type", "Days for shipping (real)", "Days for shipment (scheduled)",
    "Benefit per order", "Sales per customer", "Delivery Status",
    "Late_delivery_risk", "Category Id", "Category Name",
    "Customer City", "Customer Country", "Customer Email",
    "Customer Fname", "Customer Id", "Customer Lname",
    "Customer Password", "Customer Segment", "Customer State",
    "Customer Street", "Customer Zipcode", "Department Id",
    "Department Name", "Latitude", "Longitude", "Market",
    "Order City", "Order Country", "Order Customer Id",
    "order date (DateOrders)", "Order Id", "Order Item Cardprod Id",
    "Order Item Discount", "Order Item Discount Rate", "Order Item Id",
    "Order Item Product Price", "Order Item Profit Ratio",
    "Order Item Quantity", "Sales", "Order Item Total",
    "Order Profit Per Order", "Order Region", "Order State",
    "Order Status", "Order Zipcode", "Product Card Id",
    "Product Category Id", "Product Description", "Product Image",
    "Product Name", "Product Price", "Product Status",
    "shipping date (DateOrders)", "Shipping Mode",
]

# Trouver les colonnes manquantes
missing = [c for c in csv_columns if c not in existing]
print(f"Colonnes manquantes: {missing}")

# Trouver les colonnes en trop
extra = [c for c in existing if c not in csv_columns and c != "_loaded_at"]
print(f"Colonnes en trop: {extra}")

if missing or extra:
    print("\nLa table doit etre recreee.")
    print("Suppression et recreation de bronze.orders...")

    # Drop index first, then table
    cursor.execute("""
        IF EXISTS (SELECT * FROM sys.indexes WHERE name = 'uix_bronze_orders_item')
            DROP INDEX uix_bronze_orders_item ON bronze.orders
    """)
    cursor.execute("DROP TABLE bronze.orders")

    # Recreate with ALL CSV columns in correct order
    create_sql = """
        CREATE TABLE bronze.orders (
            [Type] NVARCHAR(50),
            [Days for shipping (real)] NVARCHAR(50),
            [Days for shipment (scheduled)] NVARCHAR(50),
            [Benefit per order] NVARCHAR(50),
            [Sales per customer] NVARCHAR(50),
            [Delivery Status] NVARCHAR(100),
            [Late_delivery_risk] NVARCHAR(10),
            [Category Id] NVARCHAR(50),
            [Category Name] NVARCHAR(200),
            [Customer City] NVARCHAR(200),
            [Customer Country] NVARCHAR(100),
            [Customer Email] NVARCHAR(200),
            [Customer Fname] NVARCHAR(100),
            [Customer Id] NVARCHAR(50),
            [Customer Lname] NVARCHAR(100),
            [Customer Password] NVARCHAR(100),
            [Customer Segment] NVARCHAR(50),
            [Customer State] NVARCHAR(100),
            [Customer Street] NVARCHAR(200),
            [Customer Zipcode] NVARCHAR(20),
            [Department Id] NVARCHAR(50),
            [Department Name] NVARCHAR(200),
            [Latitude] NVARCHAR(50),
            [Longitude] NVARCHAR(50),
            [Market] NVARCHAR(50),
            [Order City] NVARCHAR(200),
            [Order Country] NVARCHAR(100),
            [Order Customer Id] NVARCHAR(50),
            [order date (DateOrders)] NVARCHAR(50),
            [Order Id] NVARCHAR(50),
            [Order Item Cardprod Id] NVARCHAR(50),
            [Order Item Discount] NVARCHAR(50),
            [Order Item Discount Rate] NVARCHAR(50),
            [Order Item Id] NVARCHAR(50),
            [Order Item Product Price] NVARCHAR(50),
            [Order Item Profit Ratio] NVARCHAR(50),
            [Order Item Quantity] NVARCHAR(50),
            [Sales] NVARCHAR(50),
            [Order Item Total] NVARCHAR(50),
            [Order Profit Per Order] NVARCHAR(50),
            [Order Region] NVARCHAR(200),
            [Order State] NVARCHAR(100),
            [Order Status] NVARCHAR(50),
            [Order Zipcode] NVARCHAR(20),
            [Product Card Id] NVARCHAR(50),
            [Product Category Id] NVARCHAR(50),
            [Product Description] NVARCHAR(MAX),
            [Product Image] NVARCHAR(MAX),
            [Product Name] NVARCHAR(500),
            [Product Price] NVARCHAR(50),
            [Product Status] NVARCHAR(10),
            [shipping date (DateOrders)] NVARCHAR(50),
            [Shipping Mode] NVARCHAR(50),
            [_loaded_at] DATETIME DEFAULT GETDATE()
        );
    """
    cursor.execute(create_sql)

    # Recreate index
    cursor.execute("""
        CREATE UNIQUE NONCLUSTERED INDEX uix_bronze_orders_item
        ON bronze.orders ([Order Item Id])
        WITH (IGNORE_DUP_KEY = ON)
    """)

    print("Table bronze.orders recreee avec succes. 53 colonnes + _loaded_at.")
else:
    print("Schema OK. Aucune modification necessaire.")

conn.close()
