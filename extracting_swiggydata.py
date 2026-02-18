import json
swiggy_data_input = input(r"Enter the file path or file name : ")
# json file path : "C:\Users\yash.limbasiya\Downloads\swiggy.json"

def open_json(swiggy_data_input):# this is json load function
    with open(swiggy_data_input) as json_file:
        datad = json.load(json_file)
    return datad
product_data = [] # append in this list

def extracting_data(raw): # main data extracting function
    for i in raw['data']['cards']:#data.cards[0]
        for cards in i ['card']['card']['gridElements']['infoWithStyle']['items']:#card.card.gridElements.infoWithStyle.items[0]
            # create a dicionry to appen that all data into dict
            full_image_path = r'https://instamart-media-assets.swiggy.com/swiggy/image/upload/fl_lossy,f_auto,q_auto,h_600/'
            for subitems in cards['variations']:
                product_dict = dict()
                product_dict["Product Name"] = subitems["displayName"]
                product_dict["Product ID"] = subitems["skuId"]
                product_dict["Product Price"] =float(subitems["price"]['offerPrice']['units'])
                product_dict["Product quantity"] = subitems["quantityDescription"]
                product_dict["Product Image Url"] = subitems["imageIds"]
                product_dict["Product Image Url"] = [full_image_path+image for image in product_dict["Product Image Url"]]
                product_dict["Discount percentage"] =int(subitems["price"]['offerApplied']['listingDescription'].split("%")[0])
                product_dict["Product Mrp"] = float(subitems["price"]['mrp']['units'])
                product_data.append(product_dict)
                product_dict['Product In Stock'] = cards['inStock']
    return product_data

def convert_json_dump(result):# created a function to convert the extracted data into json format and save it to a file
    with open("swiggy_product_Data.json", "w") as file:
        json.dump(result, file, indent=4)

raw = open_json(swiggy_data_input)
extrac_d = extracting_data(raw)
convert_json_dump(extrac_d)