from flask_restx import Namespace, Resource
from helpers.error_codes import error_codes
from responses import BaseResponse
from flask import request, g
from helpers.auth import login_required
from helpers.aws_bucket import upload_obj_to_s3
# from tryon.remove_background import remove_background
# from tryon.check_tryon import is_available_for_tryon
from database import db
from models import TryonOutput, UserTryonInput, Products
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

            product = Products.query.filter_by(
                id=validated_data.product_id,
                tryon_available=True
            ).first()
            logger.info("Product Info Loaded!")
            if not product:
                return BaseResponse.bad_request(1023, error_codes[1023])
            
            if product.category_id == 2:
                garment = 'Upper-body'
            elif product.category_id == 3:
                garment = 'Lower-body'
            elif product.category_id == 7:
                garment = 'Dress'

            # check if we have the tryon output for this user input
            tryon_output = TryonOutput.query.filter_by(
                user_tryon_input_id=validated_data.user_tryon_input_id,
                product_id=validated_data.product_id
            ).first()
            logger.info("Tryon Output Loaded")
            if tryon_output:
                response = TryonOutputSchema().dump(tryon_output)
                return BaseResponse.success(response, "OOTD model ran successfully")

            # for testing
            # cloth_image_url = "https://azzain-bucket.s3.me-south-1.amazonaws.com/images/products/try_on/input/clothes/023a38ad-4330-45d0-942b-7185522a236b.png"
            cloth_image_url = f"{Config.AWS_S3_BUCKET_URL}/images/products/try_on/input/clothes/{product.product_uuid}.png"
            human_image_url = user_input.image_url
            logger.info("Cloth Image Loaded")
            logger.info("Human Image Loaded")

            client = Client(
                "levihsu/OOTDiffusion")
            logger.info("Client Loaded")

            result = client.predict(
                handle_file(human_image_url),
                handle_file(cloth_image_url),
                garment,
                1,
                Config.OOTD_PARAM_STEPS,
                Config.OOTD_PARAM_GUIDANCE_SCALE,
                Config.OOTD_PARAM_SEED,
                api_name=Config.OOTD_PARAM_API_NAME
            )
            logger.info("Response recieved from OOTD!")
            logger.info(f"Result: {result}")

            image_path = 'https://levihsu-ootdiffusion.hf.space/file=' + result[0]["image"]
            response = requests.get(image_path)
            logger.info("Image Loaded from OOTD")
            
            # copy the output image to ./tmp/output folder
            filename = random.randbytes(16).hex()
            output_image_path = f"./tmp/output/{filename}.jpg"
            webp_image = Image.open(BytesIO(response.content)).convert('RGB')
            webp_image.save(output_image_path, 'JPEG')
            # with open(output_image_path, 'wb') as file:
            #     file.write(response.content)
            logger.info("Image Downloaded")

            # shutil.copy(image_path, output_image_path)
            # os.remove(image_path)

            output_img_obj = open(output_image_path, 'rb')
            logger.info("Image Object Loaded")

            upload_status = upload_obj_to_s3(
                file=output_img_obj,
                file_name=f'{filename}.jpg',
                bucket_path='images/products/try_on/output'
            )
            logger.info("Image Object Uploaded to bucket")

            if not upload_status:
                return BaseResponse.internal_server_error(1040, error_codes[1040])

            output_img_url = f"{Config.AWS_S3_BUCKET_URL}/images/products/try_on/output/{filename}.jpg"
            new_tryon_output = TryonOutput(
                user_tryon_input_id=user_input.id,
                product_id=product.id,
                image_url=output_img_url
            )
            db.session.add(new_tryon_output)
            db.session.commit()
            output_img_obj.close()

            # os.remove(output_image_path)
            return BaseResponse.success({
                "image_url": output_img_url,
                "product_id": product.id,
                "user_tryon_input_id": validated_data.user_tryon_input_id
            }, "OOTD model ran successfully")

        except Exception as e:
            logger.error(f"Error while running OOTD model:\n {e}")
            return BaseResponse.internal_server_error(1035, error_codes[1035])
