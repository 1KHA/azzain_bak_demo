from typing import List
from recommendation.helper.utils import get_search_by_product_id, get_search_by_product_desc, NUM_RECOMMENDED_PRODUCTS


def get_similar_items(product_id: str,
                      num_recommended_products: int = NUM_RECOMMENDED_PRODUCTS) -> List[str]:
    '''
    do a similarity search based on Description of given product id

    • Args :
        product_id: Unique Product ID  on which you want to perform similar search
        num_recommended_products: how many number of products you want as recommended Product (default value from global variable)

    • Return :
        Product_id_list: recommended Product ID list
        Score_List: list which contains similarity score of each recommended Product
    '''

    product_id_list = get_search_by_product_id(
        product_id, num_recommended_products=num_recommended_products)
    return product_id_list


def get_similar_items_from_description(description: str,
                                       category_name: str = None,
                                       preffered_gender=None,
                                       num_recommended_products: int = NUM_RECOMMENDED_PRODUCTS) -> List[float]:
    '''
    do a similarity search based on Description of given product's description

    • Args :
        description: Unique Product ID  on which you want to perform similar search
        category_name :  Category of given Product
        num_recommended_products: how many number of products you want as recommended Product (default value from global variable)

    • Return :
        Product_id_list: recommended Product ID list
        Score_List: list which contains similarity score of each recommended Product
    '''

    product_id_list = get_search_by_product_desc(description=description,
                                                 category_name=None if category_name is None else category_name,
                                                 preffered_gender=preffered_gender,
                                                 num_recommended_products=num_recommended_products)

    return product_id_list[:num_recommended_products]
