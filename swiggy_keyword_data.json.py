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

        # for cards in i ['card']['card']['gridElements']['infoWithStyle']['items']:#card.card.gridElements.infoWithStyle.items[0]
        card_details = i.get('card',{}).get('card',{}).get('gridElements',{})# if not found in i than they give {}
        if card_details == {}:
            continue #skip that itration if grieelement not found
        cd = card_details["infoWithStyle"]["items"]
        for card in cd:
            full_image_path = 'https://instamart-media-assets.swiggy.com/swiggy/image/upload/fl_lossy,f_auto,q_auto,h_600/'
            for subitems in card['variations']:
                product_dict = dict()
                product_dict["Product Name"] = subitems["displayName"]
                product_dict["Product ID"] = subitems["skuId"]
                product_dict["Product Price"] =float(subitems["price"]['offerPrice']['units'])
                product_dict["Product quantity"] = subitems["quantityDescription"]
                product_dict["Product Image Url"] = subitems["imageIds"]
                product_dict["Product Image Url"] = [full_image_path+image for image in product_dict["Product Image Url"]]
                # if not subitems["price"]['offerApplied']['listingDescription']:
                #     product_dict['Discount percentage'] = None
                # else:
                product_dict["Discount percentage"] = int(subitems["price"]['offerApplied']['listingDescription'].split('%')[0] or 0)
                product_dict["Product Mrp"] = float(subitems["price"]['mrp']['units'])
                product_data.append(product_dict)
                product_dict['Product In Stock'] = card['inStock']
    return product_data

def convert_json_dump(result):# created a function to convert the extracted data into json format and save it to a file
    file_input_name = input(r"Enter the file path or file name : ")
    with open(file_input_name, "w") as file:
        json.dump(result, file, indent=4)

raw = open_json(swiggy_data_input)
extrac_d = extracting_data(raw)
convert_json_dump(extrac_d)