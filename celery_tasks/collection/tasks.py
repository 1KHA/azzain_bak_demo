from query.collection_query import CollectionQuery
from celery import shared_task
from logger import logger
from helpers.recommendation import get_user_data
from database import db


@shared_task
def create_generic_collection_for_user(user_id: int):
    logger.info(f"Creating generic collection for user {user_id}")
    user_data = get_user_data(user_id)
    try:
        CollectionQuery.create_generic_collection_for_user(user_data)
    except Exception as e:
        logger.exception(f"Error creating generic collection for user {user_id}")
        return False
    db.session.commit()
    logger.success(f"Generic collection created for user {user_id}")
    return True

