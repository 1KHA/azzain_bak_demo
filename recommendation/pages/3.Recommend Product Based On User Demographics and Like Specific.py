import streamlit as st
import numpy as np
from user_demographics_and_likes_specific import get_recommendation_by_user_demographics
from helper.utils import build_user_input
from helper.utils import get_vector_details
import random

st.title('Recommend Product Based on User Demographics')
st.divider()
st.subheader('enter your detail : ')
col1, col2 = st.columns(2)
with col1:
    country = col1.text_input('enter your country')
    city = col1.text_input("enter your city")
    age_group = col1.selectbox('select your age group', [
                               "12-16", "17-30", "31-45", "above 45"])
    height = col1.select_slider('provide your height', np.arange(90, 251))
    weight = col1.select_slider('provide your Weight', np.arange(30, 251))
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


if st.button("Recommend"):

    Product_ids = get_recommendation_by_user_demographics(User_input)

    for i in Product_ids:
        col_1, col_2 = st.columns(2)

        details = get_vector_details(i)
        name, desc = details.payload['Title'], details.payload['Description']
        col_1.image(eval(details.payload['Images'])[0], width=350)
        col_2.write(f'##### :violet[• {name}]')
        col_2.write(f'Product ID : :red[{i}]')
        col_2.write(f'{desc[:500]}')
        st.divider()
