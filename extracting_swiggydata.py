import json
import mysql.connector

swiggy_data_input = input(r"Enter the file path or file name : ")
# json file path : "C:\Users\yash.limbasiya\Downloads\swiggy.json"

# this is json load function
with open(swiggy_data_input) as json_file:
    raw = json.load(json_file)

product_data = [] # append in this list

# main data extracting function
for i in raw['data']['cards']:#data.cards[0]
    for cards in i['card']['card']['gridElements']['infoWithStyle']['items']:#card.card.gridElements.infoWithStyle.items[0]
        # create a dicionry to appen that all data into dict
        full_image_path = 'https://instamart-media-assets.swiggy.com/swiggy/image/upload/fl_lossy,f_auto,q_auto,h_600/'
        for subitems in cards['variations']:
            product_dict = dict()
            product_dict["Product Name"] = subitems["displayName"]
            product_dict["Product ID"] = subitems["skuId"]
            product_dict["Product Price"] = float(subitems["price"]['offerPrice']['units'])
            product_dict["Product quantity"] = subitems["quantityDescription"]
            product_dict["Product Image Url"] = subitems["imageIds"]
            product_dict["Product Image Url"] = [full_image_path + image for image in product_dict["Product Image Url"]]
            product_dict["Discount percentage"] = int(subitems["price"]['offerApplied']['listingDescription'].split("%")[0])
            product_dict["Product Mrp"] = float(subitems["price"]['mrp']['units'])
            product_dict['Product In Stock'] = cards['inStock']
            product_data.append(product_dict)


# created a function to convert the extracted data into json format and save it to a file
file_input_name = input(r"Enter the file new name that given to you: ")
with open(file_input_name, "w") as file:
    json.dump(product_data, file, indent=4)


conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="actowiz",
    database="swiggy_db"
)

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS products (
    id INT PRIMARY KEY AUTO_INCREMENT,
    product_id VARCHAR(100) UNIQUE,
    product_name VARCHAR(255),
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
    (product_id, product_name, product_price, product_quantity,
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
        item["Product ID"],
        item["Product Name"],
        item["Product Price"],
        item["Product quantity"],
        item["Discount percentage"],
        item["Product Mrp"],
        item["Product In Stock"]
    ))

    cursor.execute("DELETE FROM product_images WHERE product_id=%s", (item["Product ID"],))

    for img in item["Product Image Url"]:
        cursor.execute("""
        INSERT INTO product_images (product_id, image_url)
        VALUES (%s,%s)
        """, (item["Product ID"], img))

conn.commit()
cursor.close()
conn.close()

print("Data successfully stored ")