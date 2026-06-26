# import streamlit as st
# from product_pair_for_category import get_pair_from_category, get_product_pairs
# from helper.utils import get_image_link
# from exp import get_good_fit_products_for_selected_product
# from recent_search import do_globle_search_by_description

# default_image = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAMgAAADICAMAAACahl6sAAAAe1BMVEX///8AAAAHBwe0tLStra38/PywsLC8vLzz8/P29vYODg6oqKjHx8fZ2dmVlZUUFBRLS0vQ0NB8fHyenp4zMzMdHR2CgoJsbGwZGRlUVFR1dXWhoaHf398/Pz9GRkZTU1MlJSWNjY0sLCxhYWEoKChBQUFnZ2fn5+eQkJBXH8SxAAAImklEQVR4nO2d6XqrOAyGDYkLJIQskD1plk6X+7/CSZvOmRbJtmzLJjMP398WnBcvkrxJiF69evXq1atXr169evX6H0q+T8ps8DQePw2ycvIuu/499sqzandqpklL02a7q7K8619HU56tZss2wW8tZ6sHp5HZrtEz/Ktmlz1oU8v3pxGV4q7Raf9wFVOMZ6kdxV3paVx0/dt/aL62rIufmq4nXf/+u+Tw6E5x1/Gp++6Sf5x9MT51rrptYcUF2ApXbTpEkdWGC+NTy7qjBjb4ixPjU9esA4zJjBvjU6dDZAy5cjIbZqWXqO1rfg2D8almHg1DrsJhJBEr5eBtAE16fY/B8UR2R5bH7XpV1fvxeF9/rNbbI9l2jgbBMeSC8kOms8VwgjSQYjJczEg2dBW4eeXPZohtbfACJ/XWXKuzoB7+wWQDl7uS9ClluTOEkck1oEkp9a1i9FZave1NXy+bYOPwQGsEm9q6MeS11h6lgTyWsY5j5lhoput06RMvwV17HYZHKyh1KGO+3/+PNBxHq64BVWqmXthJhsqilv5lyb06sGFuXep+vmYZ7/O16v28Pb5UcVw9W9WPIlT+y4hxFD6o7MeaMc4uVJWyYbOMucKeT5ldO5U7emXyVqRifGzYfYgPRZ3MeDxIhb/7wj59M1SOKCuO1z8FfPcvqTmShKERH9CGm+7939ySjiMZeceMEo1rU/4ITstxi359uwk6zxDALTVwJMnF7/3zR+FIUi+7KLF4IX67+lLj07jQhhW5n//Rh3sBE6yAuOPuD6XuBhibp35hJLiLyJEkJ9cSBsjLmoj2HMhxkJGIrzhl968UHGmFGOKrW3+vkPezD1gqjgHqGtUuRRRI+LmOxyEEEp8sXarkglQtdwfRcYgCiRkr+zJyJCpki2spHLfoF/5pY/8pkSCHu2EZONDGZV0lEtbrknl+3MghcthNz7a9BJnHYp4rM3Ogs4K24yYMQ46cFDQOIeAcpOXPQNx33p5O4xAZ/Be7vUSwm80YKcgcQsAZnJ1NOQX0D1hXXcgcyBA8tenu47AVQucQ4hX829CiJOi/c0a3NhxIL9nSS8pBSQ0XhLDkEAJE2yndnsHh28ntxGXJgTjhdIN2aj864jPqthwiBwMPuW1J8OgbD4Rw4BDiBXxW6rgF+xebMXTg8Pg5u/aDSw6GT7lwCAH2SCyIxQEHx8qYauTGAd0M4hiaO1elQY4csG2ltPAKPGflFKjlyoEMPjTzDOZJLUypRs4ciDmgzXYC/4TFGnpwQJtIm3MEgwTHaQIfDhgdnSlPgb4+9QH4lheHEGBGh+JpgL7O4MF7csDwijKOggZJNT9q+XJAE03ptuAhm0AGlTcHDPQoHxeMdb593Z8D9naKRQAOiqc5ZOAQRftpyqRQe4Tw9Bg5OKBJ2JgfkS7wavFwgGaSmh95b5fp5aAwccCOazYkk/YjPnPwXBzQkzcvAYIZMY/laDYOuNXKPF8IDLvDItG3+DjEpf0Ss2kHa9LOvi8jB3Q3zBEJWEx13bHBySHq9mvMbwHegOP6DisH/FVmv4kJhJcDzn2aN2jzNC1mDpemxdLZuTlcOjsYfh22SbFziEv7Xebhl8Eg8nO4GER/FyUAh3hrv83song7jSE4xLb9OrPT6OvGB+FwceNBYHW2KjEMh1O0B0Jdmw05gTicQl3QHC0mHwJxwMkHyhZRj+mgUBzQQ6FMB7lP0AXjcJugc54yDcfhNmXqOokdkAOu9JCWy92WFQJyOC4ruC30hORwXehxWXoLygE/Le1UDOjt5p0GYTlgF6EtM9svT4flcF6ett4wEJgDTjNS/VjLLRyhOSTY/UuN9ex2sYTm8NhUY7XNKTgH3OZE34kBN54pe1d4DrgvkR6z0rcChudAtgLS3XH4Ea74P0bgEOCAlLp5QIG2hU+IxeCAJ9ZsZkPgBuZn5L9icCAbmG3u5SjgcR445EXhgFvKN1bL5XCTP6iSKBzI8Q+7fYlgvhFUSRwO72MXyJf4fXo5DoeEB2FeLV+BHGf8uVAShwMui9gfTUIOi23+DZQjcSBHCBUGTSPkgOufeflIHNDLcll2wk64lnE5kJ6+dDibilTJuYjJkSNHXF3WAQvk2r51RA6sYVkfp/wSMmTc3INoHNBNct28gF3BMfqIxTFBDua7XsSBdDaF+Dly7CIT58MG0JuPxQFXaRKfLXAH4j0f/BxgIifxuwjp0hEHdt2Ex8Yx1GmLwYENWMnRa9vu3Hw5ET8Hepdi6rmP+vIgHD43B31Jwpg5MAd+9ys2Z2Cnd92lvLH6eTJluO4bu0EoHAc27iZMh7eVt8QHsOeYHUy87237llRlUfAZ2FFNFBcyO99H1RLq99w0Yr7Cdqzojg3b2e2D6jpezktZcyT++NKS8V5/pV08s52rzmJck3srJvTFxarqYL9LUXGj6U0b/1sCZa28kD5O5PmtxvOjZRrX1PvIHZSGJHn26CqlJgtIGoDj1rp0nvCrY60MdL5cAM/hS5k2F8K1sk9JUGmTToyCJVGa6/NWjV5sSpbZiz7YWQZM1nMwJRlarmlZDmW2NiXzaoLmt8nN2atGp0r/KeW8mpkTqZwCp0qkZUyaPu/Gc8R9Keb73TMpxw+Pv6vVgJ5sqDmtF5eqHu/r6rJ428JsqMoPESVX2rs++mXQc5T0T7fmdQmUH+2u9CNelrQ5OVmrvY5RM28Gq5RRFTsp4oE6w22lbaTe8UsZewq+hvvWV6JkbUqqZaXzvrtcrgVf1tDOMob+QWFJR3utu094LAfe+RFfw2cNpGmy80ivu9k9SMrmL8nh1smwjLYPkK25pXxMyHL4S9PtsPuegUqWi4ZYMelxRcuc2JmKbHUyDGTn06V80KpoKy/rxfa4adVOujy+LOoycOgXRPlhXmaD4dMgK+eH/yJAr169evXq1atXr169epn1N0efasFREO7gAAAAAElFTkSuQmCC'
# my_dict = {'country': 'india',
#            'city': 'rajkot',
#            'age_group': '[17-21]',
#            'gender': 'male',
#            'height': '120-130 cm',
#            'weight': '90-100',
#            'body_shape': 'oval',
#            'skin_tone': 'gray',
#            'hair_color': 'black',
#            'cloth_patterns': ['bike', 'motor'],
#            'cloth_colors': ['black blue', 'megend'],
#            'body_part': ['leg', 'hand', 'body'],
#            # put the description here
#            'fav_topwear': ['blackshirt', 'blue t-shirt', 'pop-t-shirt'],
#            'fav_bottomwear': ['pant', 'trousers'],
#            'fav_footwear': ['addidas', 'chelsi boot']}


# inp = st.text_input('please enter any text')

# if st.button('go for it'):
#     if inp is not None:
#         Product_ids, socre_list = do_globle_search_by_description([inp])
#         product = Product_ids[0]

#         try:
#             il = get_image_link(product)
#         except BaseException:
#             il = default_image

#         st.image(il, width=200)

#         Product_ids, socre_list, cat_list = get_good_fit_products_for_selected_product(
#             user_input=my_dict, product_id=product, num_recommended_products=5)
#         st.write(Product_ids)

#         st.write(cat_list)

#         st.title('good_fit_product')
#         for i in range(len(Product_ids)):
#             col_1, col_2 = st.columns(2)
#             try:
#                 i_link = get_image_link(Product_ids[i])
#             except BaseException:
#                 i_link = default_image

#             col_1.image(i_link, width=350)
#             st.divider()


# # p1_ids , score , p1_cat_ = get_good_fit_products_for_selected_product(my_dict , Product_ids[0],num_recommended_products = 5)

# # st.title('product 1')
# # try :
# #     image_link = get_image_link(Product_ids[0])
# # except :
# #     image_link = default_image
# # st.image(image_link,width = 300)
# # for i in range(len(p1_ids)):
# #     col_1, col_2 = st.columns(2)
# #     try :
# #         image_link = get_image_link(p1_ids[i])
# #     except :
# #         image_link = default_image

# #     col_1.image(image_link, width=350)
# #     st.divider()


# # p2_ids , score , p2_cat_ = get_good_fit_products_for_selected_product(my_dict , Product_ids[1],num_recommended_products = 5)
# # st.title('product 2')
# # try :
# #     image_link = get_image_link(Product_ids[1])
# # except :
# #     image_link = default_image
# # st.image(image_link,width = 300)

# # for i in range(len(p2_ids)):
# #     col_1, col_2 = st.columns(2)
# #     try :
# #         image_link = get_image_link(p2_ids[i])
# #     except :
# #         image_link = default_image

# #     col_1.image(image_link, width=350)
# #     st.divider()


# # p3_ids , score , p3_cat_ = get_good_fit_products_for_selected_product(my_dict , Product_ids[2],num_recommended_products = 5)
# # st.title('product 3')
# # try :
# #     image_link = get_image_link(Product_ids[2])
# # except :
# #     image_link = default_image
# # st.image(image_link,width = 300)
# # for i in range(len(p3_ids)):
# #     col_1, col_2 = st.columns(2)
# #     try :
# #         image_link = get_image_link(p3_ids[i])
# #     except :
# #         image_link = default_image

# #     col_1.image(image_link, width=350)
# #     st.divider()


# ________________________________________________________________________________________________
# ________________________________________________________________________________________________


# import os
# import yaml
# import torch
# import ast
# import pandas as pd
# from dotenv import load_dotenv
# from qdrant_client import QdrantClient, models
# from sentence_transformers import SentenceTransformer
# from typing import List, Tuple, Any, Dict
# load_dotenv()
# import streamlit as st
# from helper.utils import *

# MAX_RETRIES = 5
# NUM_RECOMMENDED_PRODUCTS = 10


# QDRANT_CLIENT_URL = "https://de049af4-984d-45d1-9f1b-adaec7a6bf8f.us-east4-0.gcp.cloud.qdrant.io:6333" # "http://localhost:6333"
# QDRANT_API = os.environ['QDRANT_API_KEY']
# GOOGLE_API_KEY = os.environ['GOOGLE_API_KEY']

# COLLECTION_NAMES = {'topwear': 'TOP_WEAR_COLLECATION',
#                     'bottomwear': 'BOTTOM_WEAR_COLLECATION',
#                     'footwear': 'FOOT_WEAR_COLLECATION',
#                     'outwear': 'OUT_WEAR_COLLECATION',
#                     'accesories': 'ACCESSORIES_COLLECATION',
#                     'dresses': 'DRESS_COLLECATION',
#                     'Other': 'OTHER_COLLECATION',
#                     'whole': "WHOLE_DATASET"}

# CATEGORY_LIST = [key for key in COLLECTION_NAMES.keys()]

# CUSTOM_HEADERS = {
#     'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
#     'accept-language': 'en-GB,en;q=0.9',
# }

# # load qdrant client
# # client = QdrantClient(url=QDRANT_CLIENT_URL, api_key=QDRANT_API)
# client = QdrantClient(url=QDRANT_CLIENT_URL , api_key = QDRANT_API)

# # load embedding model
# checkpoint = 'sentence-transformers/all-MiniLM-L6-v2'
# enbed_model = SentenceTransformer(checkpoint)


# def get_search_by_product_id(
#         product_id: str,
#         num_recommended_products: int = NUM_RECOMMENDED_PRODUCTS +
#         2) -> List[Any]:
#     '''
#     do similarity search based on the description of product

#     Arg  :
#     • product id : unique identification number of product from which u identify product

#     • Return :
#         Return the similart Search Object , an output of the qdrant-similarity search
#     '''

#     embedding = get_embedding_vector(product_id)
#     category = get_details(product_id)

#     search_res = client.search(
#         collection_name=COLLECTION_NAMES[category],
#         query_vector=embedding,
#         query_filter = models.Filter(
#             must = [
#                 models.models.FieldCondition(key = 'Description' ,match = models.MatchValue(value='Black') ),
#             ]
#         ),
#         limit=num_recommended_products
#     )

#     return search_res[2:]

# def show_result(search_result) -> List:
#     '''
#     Fetch the Data from similarity Search object and Provide most relevent

#     Args :
#     •search_result : similarity Search object
#     '''
#     similar_products = sorted([(search.score, search.payload['Product ID'])
#                               for search in search_result], reverse=True)
#     Product_List = [product_name[1] for product_name in similar_products]

#     return Product_List


# # p_id = "660036ec-a899-455b-bba0-d1cd9c2f396c"

# # st.write(p_id)
# # product_id, score_list = get_search_by_product_id(product_id = p_id)
# product_id = ['f70e1f0b-dd05-45cd-9fe0-2bdd5525289e',
#  '5cc52647-96a1-4771-9bed-2c953b0eb04c',
#  'd0b2ec45-13d7-49b0-b545-4fe3c1787da8',
#  '9e7a5680-f42a-4f89-bbf3-a3a83b8427c7',
#  '9c60e0de-20b8-4582-b3df-7b04008b8caf',
#  '715e0dfc-9b95-4e40-8d73-dd9399896e70',
#  'f2a73400-a79c-4008-bcda-7029b7051f0a',
#  'e756c826-fde1-4456-9678-bf54f2dd261b',
#  '4b19aac9-0e99-40c8-a96b-9dceb2b41b3b',
#  '55ea6536-16dc-4a73-82d6-ca9159a62956']

# if st.button("see image") :
#     for i in range(len(product_id)):
#         col_1, col_2 = st.columns(2)

#         col_1.image(get_image_link(product_id[i]), width=350)
#         st.divider()


from recent_search import do_recent_search_by_product_description
from similar_items import *
from helper.utils import *
import streamlit as st
st.title('hi')


p_ids = do_recent_search_by_product_description(['tshirt', 'jeans', 'pant'])


for i in p_ids:
    col_1, col_2 = st.columns(2)

    details = get_vector_details(i)
    name, desc = details.payload['Title'], details.payload['Description']
    col_1.image(eval(details.payload['Images'])[0], width=350)
    col_2.write(f'##### :violet[• {name}]')
    col_2.write(f'Product ID : :red[{i}]')
    col_2.write(f'{desc[:500]}')
    st.divider()
