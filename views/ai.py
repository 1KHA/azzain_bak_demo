from flask_restx import Namespace, Resource
from helpers.error_codes import error_codes
from responses import BaseResponse
from flask import request, g
from helpers.auth import login_required
# from tryon.remove_background import remove_background
# from tryon.check_tryon import is_available_for_tryon
from database import db
from models import TryonOutput, UserTryonInput, Products, Category
from helpers.local_storage import (
    save_image, random_name, gradio_source, TRYON_OUTPUT)
from helpers.tryon_models import garment_for_category, run_tryon
from models.tryon_output import TryonOutputSchema
# from urllib.request import urlretrieve
from request_parsers.tryon import OOTDModelRequestBody
import random
import os
from gradio_client import Client, handle_file
from logger import logger
from config import Config
import shutil
import requests
import requests
from PIL import Image
from io import BytesIO
import random
import os

ai_api = Namespace('ai', description='AI related operations')



# @ai_api.route('/remove_bg')
# class RemoveBackground(Resource):
#     @login_required
#     def post(self):
#         """
#         Remove background from the image
#         """
#         data = request.get_json()
#         image_url = data.get('image_url')

#         if not image_url:
#             return BaseResponse.bad_request(1011, error_codes[1011])

#         logger.debug("Downloading image from URL")
#         try:
#             filename = random.randbytes(16).hex()
#             input_image_path = f"./tmp/input/{filename}.jpg"
#             urlretrieve(image_url, input_image_path)

#             output_image_path = remove_background(input_image_path)
#             logger.debug("Image background removed successfully")
#             logger.debug(f"Output Image Path {output_image_path}")

#             os.remove(input_image_path)
#             # TODO:
#             # Need to upload the image to S3 and return the URL
#             return BaseResponse.success("Image background removed successfully")
#         except Exception as e:
#             logger.error(f"Error while removing background:\n {e}")
#             return BaseResponse.internal_server_error(1035, error_codes[1035])


# @ai_api.route('/check_tryon')
# class CheckTryonAvailability(Resource):
#     @login_required
#     def post(self):
#         """
#             Check if the product image is available for tryon or not
#         """
#         data = request.get_json()
#         image_url = data.get('image_url')

#         if not image_url:
#             return BaseResponse.bad_request(1011, error_codes[1011])

#         try:
#             filename = random.randbytes(16).hex()
#             input_image_path = f"./tmp/input/{filename}.jpg"
#             urlretrieve(image_url, input_image_path)

#             tryon_available = is_available_for_tryon(input_image_path)
#             os.remove(input_image_path)

#             if tryon_available:
#                 return BaseResponse.success({
#                     "tryon_available": True
#                 }, "Product is available for tryon")
#             else:
#                 return BaseResponse.success({
#                     "tryon_available": False
#                 }, "Product is not available for tryon")
#         except Exception as e:
#             logger.error(f"Error while checking tryon availability:\n {e}")
#             return BaseResponse.internal_server_error(1035, error_codes[1035])


@ai_api.route('/run-ootd')
class RunOOTDModel(Resource):
    @login_required
    def post(self):
        """
            Run the OOTD model
        """
        data = request.get_json()
        user = g.user

        try:
            validated_data = OOTDModelRequestBody(**data)
        except Exception as e:
            logger.error(f"Error while validating OOTD model request:\n {e}")
            if "garment_type" in str(e):
                return BaseResponse.bad_request(1036, error_codes[1036])
            return BaseResponse.bad_request(1006, error_codes[1006])
        logger.info(f"data: {validated_data}")

        try:


            user_input = UserTryonInput.query.filter_by(
                id=validated_data.user_tryon_input_id,
                user_id=user.id).first()
            logger.info("User Input Loaded!")
            if not user_input:
                return BaseResponse.bad_request(1041, error_codes[1041])

            # Any product may be tried on as long as the model can handle its
            # category; tryon_available is only a display hint for the app and
            # is no longer what gates the API.
            product = Products.query.filter_by(
                id=validated_data.product_id).first()
            logger.info("Product Info Loaded!")
            if not product:
                return BaseResponse.bad_request(1023, error_codes[1023])

            # Resolved by category name: ids differ between environments, and
            # an unmapped category used to raise UnboundLocalError below.
            category = Category.query.get(product.category_id)
            garment = garment_for_category(category.name if category else None)
            if garment is None:
                logger.error(
                    f"Product {product.id} category is not try-on capable")
                return BaseResponse.bad_request(1042, error_codes[1042])

            # check if we have the tryon output for this user input
            tryon_output = TryonOutput.query.filter_by(
                user_tryon_input_id=validated_data.user_tryon_input_id,
                product_id=validated_data.product_id
            ).first()
            logger.info("Tryon Output Loaded")
            if tryon_output:
                response = TryonOutputSchema().dump(tryon_output)
                return BaseResponse.success(response, "OOTD model ran successfully")

            # The garment is the product's own photo and the human image is the
            # photo the user just uploaded — both are served from this server,
            # so they are handed to the Space as local files (it uploads them)
            # rather than as URLs it would have to fetch back from us.
            if not product.image_urls:
                logger.error(f"Product {product.id} has no image")
                return BaseResponse.bad_request(1023, error_codes[1023])

            cloth_image = gradio_source(product.image_urls[0])
            human_image = gradio_source(user_input.image_url)
            logger.info(f"Cloth Image: {cloth_image}")
            logger.info(f"Human Image: {human_image}")

            result_image = run_tryon(human_image, cloth_image, garment)
            logger.info(f"Try-on model returned: {result_image}")

            # the model may return a local temp file or a URL
            if str(result_image).startswith("http"):
                output_image = Image.open(
                    BytesIO(requests.get(result_image, timeout=120).content))
            else:
                output_image = Image.open(result_image)
            logger.info("Image received from the try-on model")

            # stored next to the other static images and served by nginx
            _, output_img_url = save_image(
                output_image.convert("RGB"), TRYON_OUTPUT, random_name("jpg"))
            logger.info(f"Try-on result saved: {output_img_url}")

            new_tryon_output = TryonOutput(
                user_tryon_input_id=user_input.id,
                product_id=product.id,
                image_url=output_img_url
            )
            db.session.add(new_tryon_output)
            db.session.commit()
            return BaseResponse.success({
                "image_url": output_img_url,
                "product_id": product.id,
                "user_tryon_input_id": validated_data.user_tryon_input_id
            }, "OOTD model ran successfully")

        except Exception as e:
            # log the traceback: these failures are usually upstream (Space
            # offline, client/protocol mismatch) and str(e) is often empty
            logger.exception(f"Error while running OOTD model: {type(e).__name__}: {e}")
            return BaseResponse.internal_server_error(1035, error_codes[1035])
