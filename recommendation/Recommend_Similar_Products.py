import streamlit as st
import numpy as np
import pandas as pd
from similar_items import get_similar_items
from recommendation.helper.utils import get_vector_details, get_search_by_product_desc
from recommendation.similar_items import get_similar_items_from_description

df = pd.read_csv("Datasets/ProductData.csv")
product_ids = df['Product ID'].tolist()

st.write('# Recommend Similar Items Based on Your Selection (product id) 🛍️', )
st.divider()


if 'Product_ID' not in st.session_state:
    st.session_state.Product_ID = '9f27d801-f70f-4473-8390-902ad2d74d60'


col_1, col_2 = st.columns(2)

with col_2:
    col_2.subheader('')
    if st.button("Change Product ID"):
        st.session_state.Product_ID = product_ids[np.random.randint(0, 4055, 1)[
            0]]


with col_1:
    s = st.selectbox('Please select Product ID ', [
                     st.session_state.Product_ID])

if st.button('Get Similar Items'):
    st.subheader(
        ':green[Below is all the details of Your Selected Productt...]')
    st.divider()
    col_1, col_2 = st.columns(2)

    detail = get_vector_details(s)
    col_1.image(eval(detail.payload['Images'])[0], width=300)
    with col_2:

        name, desc = detail.payload['Title'], detail.payload['Description']
        st.write(f'### :violet[{name}]\n {desc[:400]}')

    st.title('')
    st.subheader(
        ":red[Here's a lineup of products that are just like the one you've selected:]")
    st.divider()

    Product_ids = get_similar_items(s)
    st.title(len(Product_ids))

    for i in Product_ids:
        col_1, col_2 = st.columns(2)

        details = get_vector_details(i)

        name, desc = details.payload['Title'], details.payload['Description']
        col_1.image(eval(details.payload['Images'])[0], width=350)
        col_2.write(f'##### :violet[• {name}]')
        col_2.write(f'Product ID : :red[{i}]')
        col_2.write(f'{desc[:500]}')
        st.divider()


st.write('-' * 100)
st.write('# Recommend Similar Items Based on Your Selection (product Description) 🛍️', )
col_1, col_2 = st.columns(2)
description = col_1.text_input('Please Enter Text')
category = col_2.text_input('Pleas Enter Category')
p_g = st.selectbox('please enter gender', ['men', 'women', None])

p_ids = get_similar_items_from_description(
    description, category_name=None, preffered_gender=p_g)

if st.button('Proceed'):
    for i in p_ids:
        col_1, col_2 = st.columns(2)

        details = get_vector_details(i)
        name, desc = details.payload['Title'], details.payload['Description']
        col_1.image(eval(details.payload['Images'])[0], width=350)
        col_2.write(f'##### :violet[• {name}]')
        col_2.write(f'Product ID : :red[{i}]')
        col_2.header(details.payload['Gender'])
        col_2.header(details.payload['Category'])
        col_2.write(f'{desc[:500]}')
        st.divider()
