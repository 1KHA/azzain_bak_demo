import os
from typing import List, Dict, Any
from qdrant_client import QdrantClient, models
from sentence_transformers import SentenceTransformer
import google.generativeai as genai
from dotenv import load_dotenv
load_dotenv()

MAX_RETRIES = 5
NUM_RECOMMENDED_PRODUCTS = 10
NUM_RECOMMENDED_PAIR = 12

# QDRANT_CLIENT_URL = "http://localhost:6333" 
QDRANT_CLIENT_URL = "https://5d044d5b-ea48-4e2f-b33c-56c5c1383ab0.europe-west3-0.gcp.cloud.qdrant.io"
QDRANT_API = os.environ['QDRANT_API_KEY']
GOOGLE_API_KEY = os.environ['GOOGLE_API_KEY']

COLLECTION_NAME = 'ProductCollection'
CATEGORY_LIST = ['topwear', 'bottomwear', 'footwear', 'outwear', 'accesories']
PAIR_CATEGORY_PARAMS = {'Buisness Meeting' : 'Modesty Level Should be High and Style Level Should Be Low',
                      'Family Gatheing' :'Modesty Level Should be High and Style Level Should be Medium in Generation', 
                      'Eid Mubarak' : 'Less Fency',
                       'Friend Gethering' : 'modestly Level Should Be Low and Style Level Should Be High',
                        'Trip to' :'Dress According to Given Country' }

PAIR_CATEGORIES = list(PAIR_CATEGORY_PARAMS.keys())

# loading gemini models :
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
gemini_pro_vision = genai.GenerativeModel('gemini-pro-vision')
gemini_pro = genai.GenerativeModel('gemini-pro')


CUSTOM_HEADERS = {
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
    'accept-language': 'en-GB,en;q=0.9',
}

client = QdrantClient(url=QDRANT_CLIENT_URL, api_key=QDRANT_API)
# client = QdrantClient(url=QDRANT_CLIENT_URL)

# load embedding model
checkpoint = 'sentence-transformers/all-MiniLM-L6-v2'
enbed_model = SentenceTransformer(checkpoint)


def get_embeddings(text: str) -> List:
    '''
    converting Text into Vector Embeddings :

    Args :
    • text = input text of which you want embeddings

    Return :
     embedding list
    '''
    return enbed_model.encode(text).tolist()


def get_vector_details(product_id: str) -> List[Any]:
    '''
    Arg :
    • product id  = unique identification number of product from which u identify product

    Return :
     returns the vector embeddings and payload of given product 
    '''

    vector_data = client.retrieve(
        collection_name=COLLECTION_NAME, ids=[product_id],
        with_vectors=True)

    if len(vector_data) == 0:
        return None
    return vector_data[0]


def build_filter(must_categories: List[str] = None,
                 must_texts: List[str] = None,
                 should_categories: List[str] = None,
                 should_texts: List[str] = None):
    '''
    take the must and should categories and text name and returns the filter object.. 

    Arg :
    • must_categories = name of the categories in which we wanted to put filter by must 
    • must_texts = filtering text for that following must category.. 
    • should_categories = name of the categories in which we wanted to put filter by should 
    • must_texts = filtering text for that following should category.. 

    Return :
     returns the filter object by using it we can filter the qdrant output 
    '''
    m, s = [], []
    if must_categories is not None:
        for key_, text_ in zip(must_categories, must_texts):
            if (key_ and text_) is not None : 
                m.append(models.FieldCondition(
                    key=key_, match=models.MatchValue(value=text_)))

    if should_categories is not None:
        for key_, text_ in zip(should_categories, should_texts):
            if (key_ and text_) is not None : 
                m.append(models.FieldCondition(
                    key=key_, match=models.MatchValue(value=text_)))

    filter_ = models.Filter(
        must=m if m is not None else [],
        should=s if s is not None else [])

    return filter_


def get_search_by_product_id(
        product_id: str,
        num_recommended_products: int = NUM_RECOMMENDED_PRODUCTS) -> List[str]:

    details = get_vector_details(product_id)
    
    if not details:
        return []

    filter_ = build_filter(must_categories=['Category','Gender'], must_texts=[details.payload['Category'],details.payload['Gender']] ,
                           should_categories=['Sub-Category'], should_texts=[details.payload['Sub-Category']])

    search_res = client.search(
        collection_name= COLLECTION_NAME,
        query_vector=details.vector,
        query_filter=filter_,
        limit=num_recommended_products + 3)

    return [x.payload['Product ID'] for x in search_res if x.payload['Product ID'] != product_id][:num_recommended_products]


def get_search_by_product_desc(description: str,
                               category_name: str = None,
                               preffered_gender: str = None,
                               num_recommended_products: int = NUM_RECOMMENDED_PRODUCTS) -> List[str]:

    embeddings = get_embeddings(description)

    must_c = ['Category','Gender']
    must_t = [category_name,  preffered_gender]
    

    filter_ = build_filter(must_categories=must_c, must_texts=must_t)

    search_res = client.search(
        collection_name=COLLECTION_NAME,
        query_vector=embeddings,
        query_filter=filter_,
        limit=num_recommended_products + 3)

    return [x.payload['Product ID'] for x in search_res][:num_recommended_products]

def build_user_input(
        country: str,
        city: str,
        age_group: List[str],
        gender: str,
        height: str,
        weight: str,
        body_shape: str,
        skin_tone: str,
        hair_color: str,
        cloth_patterns: List[str],
        cloth_colors: List[str],
        body_part: List[str],
        fav_topwear: List[str],
        fav_bottomwear: List[str],
        fav_footwear: List[str]) -> Dict:
    '''
    Take all valus and convert it into the user_input dict object

    Args :
        country        : user's country detail
        city           : user's city name
        age_group      : user falls in which age grup [0-12 , 12-17 , 17-30 , 30-45 , above 45]
        gender         : user's gender male female
        height         : user's height detail
        weight         : user's weight detail
        body_shape     : user's body shape detail
        skin_tone      : user's skintone
        hair_color     : 'user's hair colour
        cloth_patterns : list of the cloth patterns which user likes
        cloth_colors   : List[str] : list of the cloth color which user likes
        body_part      : list of the body prt which user is comforable to show
        fav_topwear    : list of the user's favriout topwear
        fav_bottomwear : list of the user's favriout bottomwear
        fav_footwear   : list of the user's favriout footwear

    Return :
     • returns the dictonary object of all the user's detail as user_input
    '''

    user_input = {'country': country,
                  'city': city,
                  'age_group': age_group,
                  'gender': gender,
                  'height': height,
                  'weight': weight,
                  'body_shape': body_shape,
                  'skin_tone': skin_tone,
                  'hair_color': hair_color,
                  'cloth_patterns': cloth_patterns,
                  'cloth_colors': cloth_colors,
                  'body_part': body_part,
                  'fav_topwear': fav_topwear,
                  'fav_bottomwear': fav_bottomwear,
                  'fav_footwear': fav_footwear}

    return user_input
