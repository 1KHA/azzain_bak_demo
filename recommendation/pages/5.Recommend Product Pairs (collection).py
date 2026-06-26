import streamlit as st
from product_pair_for_category import get_pair_from_category
from helper.utils import get_vector_details ,PAIR_CATEGORY_PARAMS ,PAIR_CATEGORY_PARAMS

cat_ = st.selectbox(
    'please select the category', PAIR_CATEGORY_PARAMS )

if cat_ == 'Trip to' : 
    country = st.text_input('Please Enter the Country Name You Wanted to go')
    sub_category = st.selectbox('please select the below sub-Category',['Csual','Formal','More Casual','Less Casual','Less Formal','More Formal',country + "Country's Formal Outfit",country +  "Country's Formal Outfit",country + "Country's Formal Outfit"])
else : 
    country = None 
    sub_category = st.selectbox('please select the below sub-Category',['Csual','Formal','More Casual','Less Casual','Less Formal','More Formal'])

gender_ = st.selectbox('select Gender', ['male', 'female'])
my_dict = {'country': 'india',
           'city': 'Gujrat,rajkot',
           'age_group': '[17-21]',
           'gender': gender_,
           'height': '120-130 cm',
           'weight': '90-100',
           'body_shape': 'oval',
           'skin_tone': 'gray',
           'hair_color': 'black',
           'cloth_patterns': ['cheks', 'strips'],
           'cloth_colors': ['black','blue'],
           'body_part': ['leg', 'hand', 'body'],
           'fav_topwear': ['SHORT SLEEVE CREW NECK T-SHIRT REGULAR FIT 67% LYOCELL 33% COTTON MADE IN PORTUGAL', 'SLIM FIT EVENING SHIRT POINT COLLAR CONVERTIBLE CUFF PLISSE PLASTRON FLUID SILK PARACHUTE 74% LYOCELL 26% SILK MADE IN ITALY'],
           'fav_bottomwear': ['LIGHTWEIGHT PLEAT CARGO PLEAT DETAIL BELT LOOPS 19,5CM HEM 100% COTTON MADE IN ITALY', 'Slim-fit trousers with trouser crease and side pockets. Belt loops at the waist. Concealed zip fastening. The item, made of black fabric, is part of the collection curated with designer Stefano Pilati.Made in Italy Composition: 97%cotton, 3%elastane, buttons:100%motherofpearl Materials: Size worn: 48 IT. The model is 185 cm tall Product Code: FB0966AQMVF0QA1 Sustainability:'],
           'fav_footwear': ['Lace-up wedge sneakers in molded rubber with shiny finish and knit upper, with thick graphic sole. Marshmallow line. GIVENCHY signature debossed on the back of the heel.', 'ROBERT CHELSEA BOOT ROUND TOE SHAPE RUBBER SOLE WITH LEATHER APPEARANCE TOM FORD SIGNATURE LEATHER LINING BLAKE CONSTRUCTION UPPER: CALF LEATHER SOLE: 100% RUBBER HEEL HEIGHT: 18MM']}


my_dict_input = {'category_name' : cat_ , 
                'sub_category_name' : sub_category }

st.write(f'''category is { my_dict_input.get('category_name') } Sub-Category is : { my_dict_input.get('sub_category_name') } 
            Hidden Params is : {PAIR_CATEGORY_PARAMS.get(my_dict_input.get('category_name')) }''' )

if st.button('Proceed'):

    Product_ids ,extra_p_ids = get_pair_from_category(
        user_input=my_dict, Category_details =my_dict_input) 
    
    st.session_state['extra_p_ids'] = extra_p_ids 

    Image_urls = []

    for i in range(0,30,6):
        top = Product_ids[i:i+2]
        bottom = Product_ids[i+2:i+4]
        foot = Product_ids[i+4:i+6]
        for t , b , f in zip(top,bottom,foot):
            pair = [t,b,f]
            Image_urls.extend(pair)

    for idx in range(0 , 30 , 3):
        col_1 , col_2, col_3 = st.columns(3)
        detail = get_vector_details(Image_urls[idx]).payload

        col_1.image(eval(detail['Images'])[0] ,width=200)
        # col_1.write(detail['Product ID'])
        # col_1.write(detail['Category'])
        # col_1.write(detail['Sub-Category'])
        # col_1.write(detail.get('Gender'))

        detail = get_vector_details(Image_urls[idx+1]).payload
        col_2.image(eval(detail['Images'])[0] ,width=200)
        # col_2.write(detail['Product ID'])
        # col_2.write(detail['Category']) 
        # col_2.write(detail['Sub-Category']) 
        # col_2.write(detail.get('Gender')) 

        detail = get_vector_details(Image_urls[idx+2]).payload
        col_3.image(eval(detail['Images'])[0] ,width=200) 
        # col_3.write(detail['Product ID'])  
        # col_3.write(detail['Sub-Category'])
        # col_3.write(detail['Category'])
        # col_3.write(detail.get('Gender'))

        st.divider()


if st.button('Get Extra Pairs'): 

    Image_urls =[]
    Product_ids = st.session_state['extra_p_ids'] 

    Image_urls = Product_ids 
    st.write(Product_ids) 

    for idx in range(0 , 15 , 3):
        col_1 , col_2, col_3 = st.columns(3)
        detail = get_vector_details(Image_urls[idx]).payload
        col_1.image(eval(detail['Images'])[0] ,width=200)
        # col_1.write(detail['Product ID'])
        # col_1.write(detail['Category'])
        # col_1.write(detail['Sub-Category'])
        # col_1.write(detail.get('Gender'))

        detail = get_vector_details(Image_urls[idx+1]).payload
        col_2.image(eval(detail['Images'])[0] ,width=200)
        # col_2.write(detail['Product ID'])
        # col_2.write(detail['Category']) 
        # col_2.write(detail['Sub-Category']) 
        # col_2.write(detail.get('Gender')) 

        detail = get_vector_details(Image_urls[idx+2]).payload
        col_3.image(eval(detail['Images'])[0] ,width=200) 
        # col_3.write(detail['Product ID'])  
        # col_3.write(detail['Sub-Category'])
        # col_3.write(detail['Category'])
        # col_3.write(detail.get('Gender'))

        st.divider()