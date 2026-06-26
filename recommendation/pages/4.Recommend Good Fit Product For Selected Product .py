import streamlit as st
import numpy as np
from good_fit_for_this_cloths import get_good_fit_products_for_selected_product
from helper.utils import get_vector_details, build_user_input
import random
st.title('Good Fit Products for Selected Product :')

st.divider()
st.subheader('enter your detail : ')
col1, col2 = st.columns(2)
with col1:
    country = col1.text_input('enter your country')
    city = col1.text_input("enter your city")
    age_group = col1.selectbox('select your age group', [
                               "12-16", "17-30", "31-45", "above 45"])
    height = col1.select_slider('provide your height', np.arange(90, 251))
    weight = col1.select_slider('provide your height', np.arange(30, 251))
    body_shape = col1.text_input('enter your body shape')
    skin_tone = col1.text_input('enter your  skintone')
    hair_color = col1.text_input('enter your hair colour')

with col2:
    cloth_patterns = col2.selectbox('select which pattern combination you like', [
                                    ["Bikes", "Cars"], ['Flower', 'Moon']])
    cloth_colors = col2.selectbox('select color combination', [
                                  ['rec', 'blue', 'white'], ['black', 'blue'], ['yellow', 'red', 'pink']])
    body_part = col2.selectbox('body parts comfortable revealing', [
                               ['hand', 'legs'], ['neck', 'hand'], ['legs', 'head']])
    gender = col2.selectbox('select your gender', ['male', 'female'])

    if gender == 'male':

        n1, n2 = random.sample(range(5), 2)

        man_topwear = [
            '52043a55-063a-4c6a-86c9-d2e2c1eb38bb',
            '13a59c9b-7fc7-4d74-89b5-1defbb7a401d',
            '043a1b87-2a9f-4479-a5c8-f4dc66c86c21',
            '596ccc07-7e4b-4318-8417-1a8f6dd58fa5',
            '4fd9fb52-9475-4d84-b8c3-5b6c6f3d58ba']
        man_bottomwear = [
            '7fc7560c-e091-49e8-88d3-9f58f40c68f7',
            'db23385e-0c70-44b8-9253-2cbb82cb2679',
            '18383aba-5364-4f84-9dea-275e1911cc01',
            'bf44db63-78fa-4b84-95a8-81ab30054655',
            '181af158-868c-4d34-94a4-398cfb172c58']
        man_footwear = [
            '5e1ae703-069d-43a9-ad7a-73ac57d63e1a',
            '2afa1d97-2e70-4e71-9056-2899942f3bb6',
            '4da57529-8f8e-4d9d-91c2-b9c603502819',
            'fb9a2424-b85c-4d72-9161-f987bd86f6be',
            'a1d85bd8-c6e4-4837-849c-97f76c44149e']

        fav_topwear = col2.selectbox('Select list of your fav TopWear', [
                                     [man_topwear[n1], man_topwear[n2]]])
        fav_bottomwear = col2.selectbox('Select list of your fav BottomWear', [
                                        [man_bottomwear[n1], man_bottomwear[n2]]])
        fav_footwear = col2.selectbox('Select list of your fav Footwear', [
                                      [man_footwear[n1], man_footwear[n2]]])

    else:
        n1, n2 = random.sample(range(5), 2)

        woman_topwear = ['MAK1231-YAX554', 'MAK1230-YAX554',
                         'TSK290-YAX554', 'FZXB24ARVCF0DM7', 'FZX199AR8EF1MTR']
        woman_bottomwear = [
            '7E1392EKVF0ABB',
            '7E1392AD7VF1C2F',
            '8E8035EKVF1C3Y',
            '7L1663AQX9F1NLP',
            '7E1392EKVF0AGX']
        woman_footwear = [
            '7E1392AD7VF1C2F',
            '8E8452AQ70F1MEN',
            '7E1392EKVF0ABB',
            '8E8452AQ70F1MEO',
            '7U1458ADMKF1DV5']

        fav_topwear = col2.selectbox('Select list of your fav TopWear', [
                                     [woman_topwear[n1], woman_topwear[n2]]])
        fav_bottomwear = col2.selectbox('Select list of your fav BottomWear', [
                                        [woman_bottomwear[n1], woman_bottomwear[n2]]])
        fav_footwear = col2.selectbox('Select list of your fav Footwear', [
                                      [woman_footwear[n1], woman_footwear[n2]]])


User_input = build_user_input(
    country=country,
    city=city,
    age_group=age_group,
    gender=gender,
    height=height,
    weight=weight,
    body_shape=body_shape,
    skin_tone=skin_tone,
    hair_color=hair_color,
    cloth_patterns=cloth_patterns,
    cloth_colors=cloth_colors,
    body_part=body_part,
    fav_topwear=fav_topwear,
    fav_bottomwear=fav_bottomwear,
    fav_footwear=fav_footwear, )


st.title('')

if 'Product_ID' not in st.session_state:
    st.session_state.Product_ID = 'db23385e-0c70-44b8-9253-2cbb82cb2679'


col_1, col_2 = st.columns(2)

# with col_2:
#     col_2.subheader('')
#     if st.button("Change Product ID"):
#         st.session_state.Product_ID = Product_IDS_List[np.random.randint(0, 4055, 1)[
#             0]]


with col_1:
    s = st.selectbox('Please select Product ID ', [
                     st.session_state.Product_ID])


if st.button('Recommend'):
    st.subheader(
        ':green[Below is all the details of Your Selected Productt...]')
    st.divider()

    details = get_vector_details(s).payload
    col_1, col_2 = st.columns(2)
    col_1.image(eval(details['Images'])[0], width=300)
    with col_2:
        desc = details['Description']
        st.write(f'### :{desc[:400]}')

    st.title('')
    st.subheader(
        ":red[Here's a lineup of products that are Good-Fits with  one you've selected:]")
    st.divider()

    Product_ids, Category_list = get_good_fit_products_for_selected_product(
        User_input, s)
    idx = 0
    for i in range(len(Product_ids)):
        if i % 2 == 0:
            st.subheader(Category_list[idx])
            idx += 1

        col_1, col_2 = st.columns(2)

        details = get_vector_details(Product_ids[i]).payload
        desc = details['Description']
        image_link = eval(details['Images'])[0]
        col_1.image(image_link, width=350)
        col_2.write(f'Product ID : :red[{Product_ids[i]}]')
        col_2.write(f'{desc[:500]}')
        st.divider()
