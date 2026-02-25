import json
import mysql.connector


swiggy_data_input = input("Enter the JSON file path or file name : ")

with open(swiggy_data_input) as json_file:
    raw = json.load(json_file)

product_data = []


for i in raw.get('data', {}).get('cards', []):

    card_details = i.get('card', {}).get('card', {}).get('gridElements', {})
    if not card_details:
        continue

    cd = card_details.get("infoWithStyle", {}).get("items", [])

    for card in cd:
        full_image_path = 'https://instamart-media-assets.swiggy.com/swiggy/image/upload/fl_lossy,f_auto,q_auto,h_600/'

        for subitems in card.get('variations', []):

            product_dict = {}

            product_dict["Product Name"] = subitems.get("displayName")
            product_dict["Product ID"] = subitems.get("skuId")
            product_dict["Product Price"] = float(subitems.get("price", {}).get('offerPrice', {}).get('units', 0))
            product_dict["Product quantity"] = subitems.get("quantityDescription")

            image_ids = subitems.get("imageIds", [])
            product_dict["Product Image Url"] = [full_image_path + image for image in image_ids]

            discount_text = subitems.get("price", {}).get('offerApplied', {}).get('listingDescription', '0')
            product_dict["Discount percentage"] = int(discount_text.split('%')[0]) if '%' in discount_text else 0

            product_dict["Product Mrp"] = float(subitems.get("price", {}).get('mrp', {}).get('units', 0))
            product_dict["Product In Stock"] = card.get('inStock', False)

            product_data.append(product_dict)


output_file = input("Enter new JSON file name to save extracted data : ")

with open(output_file, "w") as file:
    json.dump(product_data, file, indent=4)

print("JSON file saved successfull")


conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="actowiz" 
)

cursor = conn.cursor()

# Create database automatically
cursor.execute("CREATE DATABASE IF NOT EXISTS swiggy_key_data")
cursor.execute("USE swiggy_key_data")


cursor.execute("""
CREATE TABLE IF NOT EXISTS products (
    id INT PRIMARY KEY AUTO_INCREMENT,
    product_name VARCHAR(255),
    product_id VARCHAR(100) UNIQUE,
    product_price DECIMAL(10,2),
    product_quantity VARCHAR(50),
    discount_percentage INT,
    product_mrp DECIMAL(10,2),
    product_in_stock BOOLEAN
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS product_images (
    id INT PRIMARY KEY AUTO_INCREMENT,
    product_id VARCHAR(100),
    image_url TEXT,
    FOREIGN KEY (product_id) REFERENCES products(product_id)
    ON DELETE CASCADE
)
""")

for item in product_data:

    cursor.execute("""
    INSERT INTO products 
    (product_name, product_id, product_price, product_quantity,
     discount_percentage, product_mrp, product_in_stock)
    VALUES (%s,%s,%s,%s,%s,%s,%s)
    ON DUPLICATE KEY UPDATE
        product_name=VALUES(product_name),
        product_price=VALUES(product_price),
        product_quantity=VALUES(product_quantity),
        discount_percentage=VALUES(discount_percentage),
        product_mrp=VALUES(product_mrp),
        product_in_stock=VALUES(product_in_stock)
    """, (
        item["Product Name"],
        item["Product ID"],
        item["Product Price"],
        item["Product quantity"],
        item["Discount percentage"],
        item["Product Mrp"],
        item["Product In Stock"]
    ))

    for img in item["Product Image Url"]:
        cursor.execute("""
        INSERT INTO product_images (product_id, image_url)
        VALUES (%s,%s)
        """, (item["Product ID"], img))


conn.commit()
cursor.close()
conn.close()

print("Data successfully inserted")