import json
import PIL.Image
import requests
from io import BytesIO
from typing import List, Tuple, Dict
from recommendation.recent_search import do_recent_search_by_product_description
from recommendation.helper.utils import gemini_pro_vision, get_vector_details, CUSTOM_HEADERS, CATEGORY_LIST, MAX_RETRIES, NUM_RECOMMENDED_PRODUCTS


def get_description_list(user_input: Dict, product_id: str) -> List[str]:
    '''
    takes the User_input Dict adn product id as input and return the Description of the good fit product 
    for given product id 

    • Args : 
        user_input : dict object of all user's input  
        Product_id : unique identification number of given Product 

    • return : 
        List of the good fit Product-Description
    '''

    details = get_vector_details(product_id=product_id).payload
    description = details['Description']

    Prompt_Template = f'''

    • Act as : Recommendation System Which Suggesting The Best-Fit Product For Selected One..

    • Outcome : AI shopping assistant that knows your style and preferences.
    You tell it you've just bought a sleek, black leather jacket and you're looking for the perfect outfit to complete the look.
    The AI lights up and begins to describe products that would complement your new jacket

    • Main Work :
    -- First Findout This Provided Image product Is Belonging Which Category of Product
    -- here is the product description of Provided Image :''' + f'''{description}
    -- thare are 5 Categories :
    TOPWEAR , the subcategories can be: SHIRTS, TSHIRTS, BLOUSES, TANK TOPS, SWEATERS, HOODIES,
    BOTTOMWEAR, the subcategories can be: PANTS, TROUSERS, JEANS, SHORTS, SKIRTS, LEGGINGS,
    FOOTWEAR , the subcategories can be : SNEAKERS, BOOTS, SANDALS, FLATS, HEELS, LOAFERS, ESPADRILLES, SLIPPERS, FLIP-FLOPS
    OUTWEAR, the subcategories can be: COATS, PARKAS, JACKETS, VESTS
    ACCESORIES  , the subcategories can be : WATCHES, TIES, BELTS, WALLETS, SUNGLASSES, HATS, CUFFLINKS, BAGS
    OTHERS :
    - If Product Not Belongs to any above category then that product falls under Others Category ,

    -- now if Selected ( provided Image ) Product is Top-Wear
    -- then Generate the Product Description For Rest Of Other Categoris
    -- example : As you've selected a classic black leather jacket outwear , then  I'd recommend pairing it with a crisp white t-shirt (topwear )
    for a timeless contrast.For the bottom wear, a pair of dark-washed skinny jeans would offer a streamlined silhouette,
    while black Chelsea boots(footwear) would add a touch of sophistication to your ensemble.
    To accessorize, consider a silver watch with a minimalist design and a pair of aviator sunglasses to elevate your style quotient.
    And for those chilly evenings, a lightweight, charcoal grey scarf would be the perfect addition to wrap up your look."

     • Here's my profile: \n
     -- my Country is : {user_input.get('country')} in that mainly from the City: {user_input.get('city')} \n
        consider me in the Age Group: {user_input.get('age_group')} and my Gender is : {user_input.get('gender')} \n
        my height Height: {user_input.get('height')} and Weight: {user_input.get('weight')} also my Body Shape is : {user_input.get('body_shape')}\n
        my Skin Tone: {user_input.get('skin_tone')} as well my Hair Color is : {user_input.get('hair_color')} \n
        and also i always Preferred Clothing Patterns like this : {user_input.get('cloth_patterns')}.\n
        while shoping i generally Preferred Clothing Colors like : {user_input.get('cloth_colors')} , as well i am Comfortable with Revealing: {user_input.get('body_part')} \n
        Here is Description of my Favorite Topwear: {user_input.get('fav_topwear')} \n
        Here is Description of my Favorite Bottomwear: {user_input.get('fav_bottomwear')} \n
        Here is Description of my Favorite Footwear: {user_input.get('fav_footwear')}\n

        indexing order should be like this --> 0th : topwear , 1st : bottomwear , 2nd : footwear , 3rd : outwear , 4th : accessories , 5th : other

     -- Consider All Details of User Which Provided Above
     -- Now you have to Generate 5 Product Description Based on this Selected Image For Rest oF categories''' + '''

    • Example If Gender is Male/Men and Provided Image Items is Top-Wear  : ( if gender is Women / female then generates output according to it.. )

   -- {'descriptions' : {
         topwear : 'blak t-shirt with coller'..(generate description according provided user details this is just an example ),
         bottomwear : 'White Trouser....(generate description according provided user details this is just an example ),
         footwear  : 'White Sneakers....(generate description according provided user details this is just an example ),
         outwear : 'Bomber Jacket '(generate description according provided user details this is just an example ),
         accesories : 'Lather Belt / Sanglasses.. '(generate description according provided user details this is just an example ),
         Others : 'Silver / Gold Ring..'  } }
         -- this is just an example.. . generates the other output according to other scenario and other provided image and take inspiration from provided User detail

      -- this both is just and example and generate this kind of the output from the Provided Data ''' + '''

     • Format :
     -- Consider Format Must , Output Format must be in tructured JSON format that matches the following Format..
                {'descriptions' : {
                    'topwear' : '....' ,
                    'bottomwear' : '....' ,
                    'footwear' : '....' ,
                    'accesories' : '....' ,
                    'outwear' : ....
                    'Others' : '....' ,   }
                }

        * i wanted to perform the json.lods(json_string) and json.load should give me the dict, which you provide me
        so please convert this string into json readable format.. so i can easily load that format..

        --make sure u only provide the json string in output don't provide any extra other thing or text.. just json_strigng...'''

    image_link = eval(details['Images'])[0]
    response = requests.get(image_link, headers=CUSTOM_HEADERS)
    image = PIL.Image.open(BytesIO(response.content))

    description_list = []
    retries = 0
    while retries < MAX_RETRIES:
        try:
            print(1)
            gemini_response = gemini_pro_vision.generate_content(
                [Prompt_Template, image], stream=True)
            print(gemini_response)
            print(2)
            gemini_response.resolve()
            given_string = gemini_response.text
            print(3)

            given_string = str(
                given_string[given_string.find('{'):given_string.rfind('}') + 1])
            json_objects = json.loads(given_string)
            print(4)

            description_list = [val for val in list(
                json_objects.values())[0].values()]
            print(5)

            if len(description_list) >= 5:
                return description_list
        except:
            retries += 1

    return description_list


def get_good_fit_products_for_selected_product(user_input: Dict,
                                               product_id: str,
                                               num_recommended_products=NUM_RECOMMENDED_PRODUCTS) -> Tuple[List[str],
                                                                                                           List[str]]:
    '''
    Takes the User input and Provide the Best Fit Products For User's Selecte Product
    • Args :
        user_input : dict object which have all details about the User's demographics
        product_id : Product id which user selected for shopping , and for we want to generates the best-fit products
        num_recommended_products : number of products u want as recommended products

    • Return :
        Product_id_list: recommended Product ID list
        cat_list : rest of the categories list 
    '''

    desc_list = get_description_list(user_input, product_id)
    delet_product_category = get_vector_details(product_id).payload['Category']

    cat_list = CATEGORY_LIST + \
        ['Others'] if user_input.get('gender').lower(
        ) == 'male' else CATEGORY_LIST + ['dresses']
    gender = 'men' if user_input.get('gender').lower() == 'male' else 'women'

    for i in range(5):
        for idx, cat in enumerate(cat_list):
            if cat == delet_product_category:
                cat_list.remove(cat)
                desc_list.pop(idx)
        if len(desc_list) == 5:
            break
        else:
            continue

    Product_list = do_recent_search_by_product_description(
        desc_list, category_list=cat_list, preffered_gender=gender, num_recommended_products=num_recommended_products)
    return Product_list, cat_list
