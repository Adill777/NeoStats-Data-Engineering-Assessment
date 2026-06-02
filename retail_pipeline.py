import pandas as pd

# =====================================
# 1. LOAD DATA
# =====================================

file_path = "../Dataset/USECASE - Data Engineering.xlsx"

product_df = pd.read_excel(
    file_path,
    sheet_name="product_details"
)

retail1_df = pd.read_excel(
    file_path,
    sheet_name="retail_data1"
)

retail2_df = pd.read_excel(
    file_path,
    sheet_name="retail_data2"
)

print("Data Loaded Successfully")


# =====================================
# 2. MERGE RETAIL DATA
# =====================================

retail_df = pd.concat(
    [retail1_df, retail2_df],
    ignore_index=True
)

print("\nCombined Dataset Shape:")
print(retail_df.shape)


# =====================================
# 3. REMOVE INVALID QUANTITIES
# =====================================

invalid_qty_count = len(
    retail_df[retail_df["quantity"] <= 0]
)

retail_df = retail_df[
    retail_df["quantity"] > 0
]

print("\nInvalid Quantity Records Removed:")
print(invalid_qty_count)


# =====================================
# 4. FIX MISSING PRICES
# =====================================

missing_prices_before = retail_df["price"].isnull().sum()

price_lookup = dict(
    zip(
        product_df["product_id"],
        product_df["price"]
    )
)

retail_df["price"] = retail_df["price"].fillna(
    retail_df["product_id"].map(price_lookup)
)

missing_prices_after = retail_df["price"].isnull().sum()

print("\nMissing Prices Before:")
print(missing_prices_before)

print("\nMissing Prices After:")
print(missing_prices_after)


# =====================================
# 5. STANDARDIZE CATEGORIES
# =====================================

category_map = {
    "ELEC": "Electronics",
    "electronics": "Electronics",

    "CLOTH": "Clothing",
    "clothing": "Clothing",

    "FURN": "Furniture",
    "furniture": "Furniture",

    "HOME": "Home Appliances",
    "home appliances": "Home Appliances"
}

retail_df["category"] = retail_df["category"].replace(
    category_map
)

print("\nCategories:")
print(
    sorted(
        retail_df["category"].unique()
    )
)


# =====================================
# 6. STANDARDIZE PRODUCT NAMES
# (USING PRODUCT MASTER TABLE)
# =====================================

product_name_lookup = dict(
    zip(
        product_df["product_id"],
        product_df["product_name"]
    )
)

retail_df["product_name"] = retail_df[
    "product_id"
].map(product_name_lookup)

print("\nProduct Names:")
print(
    sorted(
        retail_df["product_name"].unique()
    )
)


# =====================================
# 7. STANDARDIZE DATES
# =====================================

retail_df["transaction_date"] = pd.to_datetime(
    retail_df["transaction_date"],
    errors="coerce"
)

print("\nDate Data Type:")
print(retail_df["transaction_date"].dtype)

print("\nInvalid Dates:")
print(
    retail_df["transaction_date"]
    .isnull()
    .sum()
)


# =====================================
# 8. CREATE YEAR / MONTH / QUARTER
# =====================================

retail_df["year"] = (
    retail_df["transaction_date"]
    .dt.year
)

retail_df["month"] = (
    retail_df["transaction_date"]
    .dt.month_name()
)

retail_df["quarter"] = (
    "Q"
    + retail_df["transaction_date"]
      .dt.quarter
      .astype(str)
)


# =====================================
# 9. PII MASKING
# =====================================

def mask_email(email):

    email = str(email)

    username, domain = email.split("@")

    return username[:2] + "***@" + domain


def mask_phone(phone):

    phone = str(phone)

    return phone[:2] + "******" + phone[-2:]


retail_df["email"] = retail_df["email"].apply(
    mask_email
)

retail_df["phone"] = retail_df["phone"].apply(
    mask_phone
)

print("\nPII Masking Completed")


# =====================================
# 10. REVENUE CALCULATION
# =====================================

retail_df["revenue"] = (
    retail_df["quantity"]
    * retail_df["price"]
    * (1 - retail_df["discount"])
)

print("\nRevenue Column Created")


# =====================================
# 11. KPI REPORT
# =====================================

total_revenue = retail_df["revenue"].sum()

print("\n==============================")
print("BUSINESS KPIs")
print("==============================")

print(
    f"\nTotal Revenue: ₹ {total_revenue:,.2f}"
)

print("\nRevenue By Category")

category_revenue = (
    retail_df
    .groupby("category")["revenue"]
    .sum()
    .sort_values(ascending=False)
)

print(category_revenue)

print("\nTop 10 Cities By Revenue")

city_revenue = (
    retail_df
    .groupby("city")["revenue"]
    .sum()
    .sort_values(ascending=False)
)

print(city_revenue.head(10))

print("\nTop Products By Revenue")

product_revenue = (
    retail_df
    .groupby("product_name")["revenue"]
    .sum()
    .sort_values(ascending=False)
)

print(product_revenue.head(10))


# =====================================
# 12. EXPORT CLEAN DATASET
# =====================================

output_file = (
    "../Dataset/cleaned_retail_data.xlsx"
)

retail_df.to_excel(
    output_file,
    index=False
)

print("\nClean Dataset Exported Successfully")
print(output_file)


# =====================================
# 13. FINAL DATASET SHAPE
# =====================================

print("\nFinal Dataset Shape:")
print(retail_df.shape)