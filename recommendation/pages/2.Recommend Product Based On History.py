import streamlit as st
from helper.utils import get_vector_details
from recent_search import do_recent_search_by_product_ids, do_recent_search_by_product_description

st.write('# Recommend Similar Items Based on Your Recent Search')
st.divider()

y = ['07a50be5-ee78-46b8-80e8-36bd29f6c356', 
     '07a50be5-ee78-46b8-80e8-36bd29f6c356', 
     '3c191e05-5354-4b55-b6b0-3ae521bf961f', '13f8c1c5-487d-4815-960d-d76435f14fbd', '0472ea30-7844-41e5-b64f-74f7b8e9fa31']

if 'Product_IDs' not in st.session_state:
    st.session_state.Product_IDs = y

col_1, col_2 = st.columns(2)

# with col_2:
#     col_2.subheader('')
#     if st.button("Change Product IDs"):
#         n = list(random.sample(range(0, 4055), 5))
#         new_y = [Product_IDS_List[n[i]] for i in range(5)]
#         st.session_state.Product_IDs = new_y

with col_1:
    history = st.selectbox('Select Your Recent History :', [
                           st.session_state.Product_IDs])

if st.button('show'):
    st.subheader(
        ':green[Below is all the details of Your Recent Search Product...]')
    st.divider()

    for i in history:
        col_1, col_2 = st.columns(2)

        details = get_vector_details(i)
        name, desc = details.payload['Title'], details.payload['Description']
        col_1.image(eval(details.payload['Images'])[0], width=350)
        col_2.write(f'##### :violet[• {name}]')
        col_2.write(f'Product ID : :red[{i}]')
        col_2.write(f'{desc[:500]}')
        st.divider()

    st.divider()
    st.subheader(
        ":red[Here's a lineup of products that are just like the one Based on your Recent Search:]")
    st.title('')

    Product_ids = do_recent_search_by_product_ids(history )

    for i in Product_ids:
        col_1, col_2 = st.columns(2)

        details = get_vector_details(i)
        name, desc = details.payload['Title'], details.payload['Description']
        col_1.image(eval(details.payload['Images'])[0], width=350)
        col_2.write(f'##### :violet[• {name}]')
        col_2.write(f'Product ID : :red[{i}]')
        col_2.write(f'{desc[:500]}')
        st.divider()


st.divider()
st.write('# Recommend Similar Items Based on Your history Search')

history = ['tshirt', 'tshirt', 'tshirt', 'tshirt', 'tshirt',
           'sunglasses', 'tshirt', 'tshirt', 'tshirt', 'tshirt']

st.write(f'history is : {history}')

if st.button('recommend based on history search'):
    p_ids = do_recent_search_by_product_description(history)
    for i in p_ids:
        col_1, col_2 = st.columns(2)

        details = get_vector_details(i)
        name, desc = details.payload['Title'], details.payload['Description']
        col_1.image(eval(details.payload['Images'])[0], width=350)
        col_2.write(f'##### :violet[• {name}]')
        col_2.write(f'Product ID : :red[{i}]')
        col_2.write(details.payload['Category'])
        col_2.write(details.payload['Gender'])
        col_2.write(f'{desc[:500]}')
        st.divider()
