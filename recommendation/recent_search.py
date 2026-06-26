from typing import List
from recommendation.helper.utils import NUM_RECOMMENDED_PRODUCTS
from recommendation.similar_items import get_similar_items, get_similar_items_from_description


def do_recent_search_by_product_ids(
        product_ids: List[str], num_recommended_products: int = NUM_RECOMMENDED_PRODUCTS) -> List[str]:
    '''
    Search Most Relevant Products according to your Provided Product id List

    • Args :
        product_ids: list of product's unique id on which you want to perform similar search
        num_recommended_products: how many number of products you want as recommended Product (default value from global variable)

    • Return :
        Product_id_list: recommended Product ID list
    '''

    Product_id_List = []

    for id_ in product_ids:
        product_id = get_similar_items(
            id_, num_recommended_products=num_recommended_products // len(product_ids))
        Product_id_List.extend(product_id)

    return Product_id_List[:num_recommended_products]


def do_recent_search_by_product_description(description_list: List[str],
                                            category_list: List[str] = None,
                                            preffered_gender=None,
                                            num_recommended_products: int = NUM_RECOMMENDED_PRODUCTS) -> List[str]:
    '''
    Search Most Relevant Products according to your Provided Product's Description List :

    • Args :
        description_list: List of description of Products  on which you want to perform similar search
        category_list : List of the categories you want to do similar search for product on it
        preffered_gender : gender name you want to generated output 
        num_recommended_products: how many number of products you want as recommended Product (default value from global variable)

    • Return :
        Product_id_list: recommended Product ID list
    '''

    Product_id_List = []

    if category_list is not None:
        for desc, category_name in zip(description_list, category_list):

            product_id = get_similar_items_from_description(
                desc, category_name, preffered_gender=preffered_gender, num_recommended_products=num_recommended_products // len(description_list))
            Product_id_List.extend(product_id)
    else:
        for desc in description_list:

            product_id = get_similar_items_from_description(
                desc, category_name=None, preffered_gender = preffered_gender ,num_recommended_products=num_recommended_products + 3)

            product_id = [
                x for x in product_id if x not in Product_id_List][:num_recommended_products // len(description_list)]
            Product_id_List.extend(product_id)

    return Product_id_List[:num_recommended_products]
