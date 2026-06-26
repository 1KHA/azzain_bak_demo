import json
from typing import List
from recommendation.helper.utils import (
    gemini_pro,
    MAX_RETRIES,
    NUM_RECOMMENDED_PAIR,
    PAIR_CATEGORY_PARAMS,
)
from recommendation.recent_search import do_recent_search_by_product_description
from recommendation.similar_items import get_similar_items

# import streamlit as st


def get_pair_description_list(
    user_input: dict, Category_details: dict, hidden_params=PAIR_CATEGORY_PARAMS
) -> List[str]:
    """
    takes the User_input Dict adn category_name as input and return the Description of pairs

    • Args :
        user_input : dict object of all user's input
        category_name : category name u wanted to generate the pair

    • return :
        List of the good fit Product-Description
    """
    Prompt_Template = (
        f"""
    
• I'd like you to act as a recommendation system and suggest a product that best matches my preferences.

Below is the Category name and Sub-Category Features :
category : {Category_details.get('category_name')}  , Sub-Category Features : {Category_details.get('sub_category_name')}

and according to this category belos is the Perameter u need to Consider  : 
{hidden_params.get(Category_details.get('category_name'))}

Based on the given category and it's Perameter ,please generate 5 product description pairs (clothing pairs) tailored to the user's demographics:

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


Consider User's Gender: {user_input.get('gender')}

For each of the 5 product description pairs, include:
1. Product description for topwear
2. Product description for bottomwear
3. Product description for footwear

Ensure the descriptions are gender-specific and relevant to the given category and based on provided user data. """
        + """

-It is mandatory to generate all 15 descriptions. Do not forget any of them. Ensure each category contains exactly 5 descriptions.

Example:
If the Gender is Male/man and the category is Party-Wear, then the descriptions should look like:

{
    "descriptions": {
        "topwear1": "A stylish navy blue slim-fit Henley shirt made from soft cotton. It features a three-button placket and ribbed cuffs for a sleek, modern look. Perfect for a laid-back party vibe.",
        "bottomwear1": "Light blue distressed jeans with a slim cut, made from stretch denim for comfort and flexibility. The distressed detailing adds a touch of edginess to your outfit.",
        "footwear1": "Classic white low-top sneakers with a minimalist design. Made from durable leather with a cushioned insole.",
        "topwear2": "A tailored black blazer with a satin lapel, ideal for a sophisticated evening look. Crafted from a wool blend for a perfect fit.",
        "bottomwear2": "Slim-fit black chinos made from breathable fabric, providing both style and comfort. Perfectly pairs with a blazer for a refined outfit.",
        "footwear2": "Elegant black leather loafers with a polished finish. Featuring a cushioned footbed for all-night comfort.",
        "topwear3": "A casual red and white checkered shirt made from lightweight cotton. Ideal for a relaxed party atmosphere.",
        "bottomwear3": "Dark blue denim jeans with a straight leg cut. Made from stretchable fabric for maximum comfort and mobility.",
        "footwear3": "Comfortable brown suede boots with a rugged sole. Perfect for adding a touch of style to your casual look.",
        "topwear4": "A versatile charcoal grey crew-neck sweater made from a cozy wool blend. It features a relaxed fit and ribbed trims for added comfort. Ideal for a casual yet refined look",
        "bottomwear4": "Dark wash straight-leg jeans crafted from high-quality denim. These jeans offer a classic fit with a slight stretch, ensuring all-day comfort and style.",
        "footwear4": "Sleek black leather Chelsea boots with elastic side panels. These boots provide a sophisticated finish to your ensemble and are perfect for both casual and semi-formal occasions",
        "topwear5": "A crisp white Oxford shirt with a slim fit, made from breathable cotton. It features a button-down collar and a single chest pocket, making it perfect for both smart and casual settings",
        "bottomwear5": "Khaki chinos with a tailored fit, made from soft twill fabric. These chinos are comfortable and versatile, suitable for both work and weekend wear",
        "footwear5": "Brown suede desert boots with a lace-up closure. These boots are comfortable and stylish, offering a touch of rugged elegance to your outfit"
    }
}

This example is for illustration purposes only. Generate unique content based on the provided data.

Users Data:

Output Format:
Ensure the output is in a structured JSON format as follows:

{
    "descriptions": {
        "topwear1": "...",
        "bottomwear1": "...",
        "footwear1": "...",
        "topwear2": "...",
        "bottomwear2": "...",
        "footwear2": "...",
        "topwear3": "...",
        "bottomwear3": "...",
        "footwear3": "..."
        "topwear4": "...",
        "bottomwear4": "...",
        "footwear4": "..."
        "topwear5": "...",
        "bottomwear5": "...",
        "footwear5": "..."
    }
}

The JSON string should be valid and properly formatted to allow for JSON parsing using `json.loads(json_string)`. Only provide the JSON string in the output, without any additional text or explanation.
"""
    )

    retries = 0
    while retries < MAX_RETRIES:

        try:
            optimized_prompt = Prompt_Template
            given_string = gemini_pro.generate_content(optimized_prompt).text
            json_string = given_string[
                given_string.find("{") : given_string.rfind("}") + 1
            ]

            json_objects = json.loads(json_string)

            description_list = [
                values for values in list(json_objects.values())[0].values()
            ]

            if len(description_list) >= 5:
                return description_list
            else:
                retries += 1
        except BaseException:
            retries += 1

    return description_list


def get_pair_from_category(
    user_input: str, Category_details: dict, num_return_pairs=NUM_RECOMMENDED_PAIR
) -> List[str]:
    """
    take the user_input dict and category_name as the input and generate the Product_list of the Pair

    • Args :
        user_input : dict object of all user's input
        category_name : category name u wanted to generate the pair
        num_return_pairs : number of pairs you want

    • return :
        p_list : list of the product for the pair

    """
    desc_list = get_pair_description_list(user_input, Category_details=Category_details)

    # st.write(desc_list)
    cat_list = ["topwear", "bottomwear", "footwear"] * 5
    Product_list = do_recent_search_by_product_description(
        desc_list,
        category_list=cat_list,
        preffered_gender="men" if user_input.get("gender") == "male" else "women",
        num_recommended_products=len(cat_list),
    )

    p_list = []
    # for product_id in Product_list :
    #     p_list.append(product_id)
    #     similar_product_id = get_similar_items(product_id=product_id,num_recommended_products=1)
    #     p_list.append(similar_product_id[0])
    for idx in range(0, len(Product_list), 3):
        p_list.append(
            {
                "topwear": Product_list[idx],
                "bottomwear": Product_list[idx + 1],
                "footwear": Product_list[idx + 2],
            }
        )
        similar_topwear_id = get_similar_items(
            product_id=Product_list[idx], num_recommended_products=1
        )
        similar_bottomwear_id = get_similar_items(
            product_id=Product_list[idx + 1], num_recommended_products=1
        )
        similar_footwear_id = get_similar_items(
            product_id=Product_list[idx + 2], num_recommended_products=1
        )
        p_list.append(
            {
                "topwear": similar_topwear_id[0],
                "bottomwear": similar_bottomwear_id[0],
                "footwear": similar_footwear_id[0],
            }
        )

    extra_p_list = []
    # for product_id in Product_list:
    #     similar_product_id = get_similar_items(
    #         product_id=product_id, num_recommended_products=3
    #     )
    #     similar_product_id = [
    #         p_id for p_id in similar_product_id if p_id not in p_list
    #     ][:1]
    #     extra_p_list.append(similar_product_id[0])
    for idx in range(0, len(Product_list), 3):
        similar_topwear_id = get_similar_items(
            product_id=Product_list[idx], num_recommended_products=3
        )
        similar_bottomwear_id = get_similar_items(
            product_id=Product_list[idx + 1], num_recommended_products=3
        )
        similar_footwear_id = get_similar_items(
            product_id=Product_list[idx + 2], num_recommended_products=3
        )
        similar_topwear_id = [
            p_id for p_id in similar_topwear_id if p_id not in p_list
        ][:1]
        similar_bottomwear_id = [
            p_id for p_id in similar_bottomwear_id if p_id not in p_list
        ][:1]
        similar_footwear_id = [
            p_id for p_id in similar_footwear_id if p_id not in p_list
        ][:1]
        if (
            len(similar_topwear_id) > 0
            and len(similar_bottomwear_id) > 0
            and len(similar_footwear_id) > 0
        ):
            extra_p_list.append(
                {
                    "topwear": similar_topwear_id[0],
                    "bottomwear": similar_bottomwear_id[0],
                    "footwear": similar_footwear_id[0],
                }
            )

    return p_list, extra_p_list
