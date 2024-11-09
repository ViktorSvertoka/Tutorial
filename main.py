from pyspark.sql import SparkSession
from pyspark.sql.functions import col, sum, round

# Ініціалізація SparkSession
spark = SparkSession.builder.appName("PySpark Data Analysis").getOrCreate()

# ANSI escape codes для кольорів
MAGENTA = "\033[35m"
CYAN = "\033[36m"
YELLOW = "\033[33m"

print(" ")

print(f"{MAGENTA}Домашнє завдання. Аналіз даних у PySpark")

print(" ")
print(" ")

# 1. Завантаження CSV-файлів у DataFrame
users_df = spark.read.csv("data/users.csv", header=True, inferSchema=True)
purchases_df = spark.read.csv("data/purchases.csv", header=True, inferSchema=True)
products_df = spark.read.csv("data/products.csv", header=True, inferSchema=True)

# Виведення кількості рядків для кожного DataFrame до очищення
print(f"{CYAN}Кількість рядків у кожному DataFrame до очищення:{YELLOW}")
print(f"users: {users_df.count()}")
print(f"purchases: {purchases_df.count()}")
print(f"products: {products_df.count()}")
print(" ")

# 2. Очистіть дані, видаляючи будь-які рядки з пропущеними значеннями
users_df = users_df.dropna()
purchases_df = purchases_df.dropna()
products_df = products_df.dropna()

# Виведення кількості рядків для кожного DataFrame після очищення
print(f"{CYAN}\nКількість рядків у кожному DataFrame після очищення:{YELLOW}")
print(f"users: {users_df.count()}")
print(f"purchases: {purchases_df.count()}")
print(f"products: {products_df.count()}")
print(" ")

# 3. Загальна сума покупок за категорією продуктів
purchases_with_products = purchases_df.join(products_df, "product_id", "inner")
total_sales_by_category = purchases_with_products.groupBy("category").agg(
    round(sum(col("price") * col("quantity")), 2).alias("total_sales")
)

print(f"{CYAN}\nЗагальна сума покупок за категорією продуктів:{YELLOW}")
total_sales_by_category.show()

# 4. Сума покупок за категорією для вікової категорії від 18 до 25 років
purchases_with_users = purchases_with_products.join(users_df, "user_id", "inner")
sales_18_25 = purchases_with_users.filter((col("age") >= 18) & (col("age") <= 25))

sales_by_category_18_25 = sales_18_25.groupBy("category").agg(
    round(sum(col("price") * col("quantity")), 2).alias("total_sales")
)

print(
    f"{CYAN}\nСума покупок за категорією для вікової категорії від 18 до 25 років:{YELLOW}"
)
sales_by_category_18_25.show()

# 5. Визначення частки покупок за кожною категорією для вікової категорії 18-25 років
total_sales_18_25 = sales_by_category_18_25.agg(
    sum("total_sales").alias("total")
).collect()[0]["total"]

percentage_sales_by_category_18_25 = sales_by_category_18_25.withColumn(
    "percentage", round((col("total_sales") / total_sales_18_25) * 100, 2)
)

print(
    f"{CYAN}\nЧастка покупок за кожною категорією для вікової категорії 18-25 років:{YELLOW}"
)
percentage_sales_by_category_18_25.show()

# 6. Вибір 3 категорій з найвищим відсотком витрат
top_3_categories = percentage_sales_by_category_18_25.orderBy(
    col("percentage").desc()
).limit(3)

print(
    f"{CYAN}\nТоп 3 категорії продуктів з найвищим відсотком витрат для вікової категорії 18-25 років:{YELLOW}"
)
top_3_categories.show()

# Закриття SparkSession
spark.stop()
