import json
from typing import List, Dict
from recommendation.recent_search import do_recent_search_by_product_description
from recommendation.helper.utils import gemini_pro, CATEGORY_LIST, MAX_RETRIES

Gemini = gemini_pro


def get_description_list(user_input: dict) -> List[str]:
    '''
    takes the User_input Dict as input and return the Description of the product 
    for given user 

    • Args : 
        user_input : dict object of all user's input  

    • return : 
        List of Product-Description
    '''
    Prompt_Template = f'''
     I'd like you to act as a recommendation system and suggest a product that best matches my preferences.\n

     Here's my profile: \n
     -- my Country is : {user_input.get('country')} in that mainly from the City: {user_input.get('city')} \n
     consider me in the Age Group: {user_input.get('age_group')} and my Gender is : {user_input.get('gender')} \n
     my height Height: {user_input.get('height')} and Weight: {user_input.get('weight')} also my Body Shape is : {user_input.get('body_shape')}\n
     my Skin Tone: {user_input.get('skin_tone')} as well my Hair Color is : {user_input.get('hair_color')} \n
     and also i always Preferred Clothing Patterns like this : {user_input.get('cloth_patterns')}.\n
     while shoping i generally Preferred Clothing Colors like : {user_input.get('cloth_colors')} , as well i am Comfortable with Revealing: {user_input.get('body_part')} \n
     Here is Description of my Favorite Topwear: {user_input.get('fav_topwear')} \n
     Here is Description of my Favorite Bottomwear: {user_input.get('fav_bottomwear')} \n
     Here is Description of my Favorite Footwear: {user_input.get('fav_footwear')}\n


     -- Consider All Details of User Which Provided Above
     -- Now you have to Generate 5 Product Description According to You By Considering All the Details Provided By User
     -- Generate 5 Product Description ,
     -- now this 5 Product Description involevs 1 Top-Wear ( if User is man/male then generate Description by considering that and if User is Female/girl then according to it.. )
     -- 1 Bottom-wear ( this Description is also according to the User's gender and other provided details )
     -- 1 foot-wear (this Description is also according to the User's gender and other provided details )
     -- 1 accessories ( this Description is also according to the User's gender and other provided details )
     -- 1 outwear / dresses (generate outwear description if male otherwise generate dresses if the provided gender is female)
     -- it's okay if any part is None in the user's details still generate the description for all products , don't generate any None output..

     --- So basically User Want 5 Product Descriptions According to Above need''' + '''

     • Example If Gender is Male/Men :
     -- {'descriptions' : {
         'topwear' : 'Black and White T-shirt with Polo Coller .....(generate similar description provided in the details),
         'bottomwear', : 'Blue Jeans Pants ......( generate similar description provided in the user demographics)',
         'footwear' : 'Addidass Shoes...',( generate similar description provided in the user demographics)
         'accesories' : 'silver Watch...',( if not provided in teh user demographics then generates according to you..please don't provide Null or NA )
         'Others' :'bomber jackets matches in this..', }
         }

     • Example If Gender is FeMale/Woman :
     -- {'descriptions' : {
         'topwear' : 'red and pink T-Dress Top with Sleeves .....( make this long according to Provided Data'  ,
         'bottomwear' : 'woman trousers ......( make this long according to provided Data)',
         'footwear' : 'hight hills ...',
         'accesories' : 'nose ring...',
         'Others' : 'Embroidered Crepe Couture short dress - Rear zip and hook fastening ', }
         }

      -- this both is just and example and generate this kind of the output from the Provided Data ''' + '''

     • Format :
     -- Consider Format Must , Output Format must be in  tructured JSON format that matches the following Format..
                {'descriptions' : {

                    'topwear' : '....' ,
                    'bottomwear' : '....' ,
                    'footwear' : '....' ,
                    'accesories' : '....' ,
                    'Others' : '....' ,   } }
                }

        * i wanted to perform the json.lods(json_string) on string which you provide me
        so please convert this string into json readable format.. so i can easily load that format..

        --make sure u only provide the json string in output don't provide any extra other thing or text.. just json_strigng...
        '''

    retries = 0
    while retries < MAX_RETRIES:

        try:
            optimized_prompt = Prompt_Template
            given_string = Gemini.generate_content(optimized_prompt).text
            json_string = given_string[given_string.find(
                '{'):given_string.rfind('}') + 1]

            json_objects = json.loads(json_string)
            description_list = [values for values in list(
                json_objects.values())[0].values()]

            if len(description_list) >= 5:
                return description_list
        except BaseException:
            retries += 1

    return description_list


def get_recommendation_by_user_demographics(
        user_input: Dict) -> List[str]:
    '''
    Takes the User input and Provide the Best Similar Product Based on User's specific like and their Demographics

    • Args :
        user_input : dict object which have all details about the User's demographics

    • Return :
        Product_id_list: recommended Product ID list
    '''

    description_list = get_description_list(user_input)

    cat_list = CATEGORY_LIST + \
        ['Others'] if user_input.get('gender').lower(
        ) == 'male' else CATEGORY_LIST + ['dresses']
    gender = 'men' if user_input.get('gender').lower() == 'male' else 'women'

    Product_list = do_recent_search_by_product_description(
        description_list, category_list=cat_list, preffered_gender=gender)

    return Product_list
