from models import Products
from app import app
from database import db
import requests
from io import BytesIO
from PIL import Image
import os
from helpers.aws_bucket import upload_obj_to_s3
from tryon.remove_background import remove_background
from logger import logger
from config import Config

def remove_image_background_db():
    with app.app_context():
        try:
            product_data = Products.query.all()
            logger.info(f"Number of products retrieved: {len(product_data)}")
            total_products = len(product_data)
            current_count = 0
            for product in product_data:
                if len(product.image_urls) == 0:
                    logger.error(f"No image URLs found for product: {product.id}")
                    current_count += 1
                    continue
                first_image_url = product.image_urls[0]
                logger.debug(f"First image URL: {first_image_url}")
                try:
                    response = requests.get(first_image_url,
                                            headers={'User-Agent': 'Mozilla/5.0'},
                                            timeout=30)
                    image = Image.open(BytesIO(response.content))
                    extension = image.format or 'jpg'
                    extension = extension.lower()
                    input_image_path = f'./tmp/input/{product.id}.{extension}'
                    image.save(input_image_path)
                except Exception as e:
                    logger.error(f"Error while downloading image: {e}")
                    current_count += 1
                    continue
                # logger.debug(f"Image downloaded successfully: {input_image_path}")
                output_image_path = remove_background(input_image_path)
                # logger.debug(f"Image background removed successfully: {output_image_path}")

                filename = output_image_path.split('/')[-1]
                file_obj = open(output_image_path, 'rb')
                upload_status = upload_obj_to_s3(
                    file=file_obj,
                    file_name=f"{product.product_uuid}.png",
                    bucket_path='images/products/bg_removed'
                )
                if not upload_status:
                    logger.error(f"Failed to upload image to S3: {filename}")
                
                product.bg_remove_url = f"https://{Config.AWS_BUCKET_NAME}.s3.{Config.AWS_REGION_NAME}.amazonaws.com/images/products/bg_removed/{product.product_uuid}.png"
                db.session.commit()
                # break
                current_count += 1
                logger.info(f"Processed {current_count}/{total_products} products")

        except Exception as e:
            logger.error(f"An error occurred: {e}")

