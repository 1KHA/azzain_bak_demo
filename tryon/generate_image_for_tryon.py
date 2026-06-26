import pandas as pd
from check_tryon import is_available_for_tryon, background_remover_cloth
from remove_background import remove_background
import requests
import random
import os
from PIL import Image
from io import BytesIO
import shutil
import numpy as np

def generate_image_for_tryon():
    df = pd.read_csv("products_tryon.csv")
    similarity_df = pd.read_csv("Similarity_Mapping.csv")
    output_df = pd.DataFrame(
        columns=['product_id', 'category', 'subcategory',
                 'image_tryon_url', 'score', 'raw_image_path']
    )

    for i in range(len(df)):
        image_urls = eval(df.loc[i, 'image_urls'])
        product_id = df.loc[i, 'product_id']
        category = df.loc[i, 'category']
        sub_category = df.loc[i, 'subcategory']
        tryon_available = False

        # image_with_max_score_index = np.argmax(
        #     similarity_df[similarity_df['Product ID'] == product_id]['Score']
        # )
        score_list = similarity_df[
            similarity_df['Product ID'] == product_id
        ]['Score'].to_list()

        if len(score_list) == 0:
            continue
        j = 0
        for image_url in image_urls:

            try:
                response = requests.get(image_url,
                                        headers={'User-Agent': 'Mozilla/5.0'},
                                        timeout=30)
                image = Image.open(BytesIO(response.content))
                # Determine file extension based on image format
                extension = image.format or 'jpg'
                extension = extension.lower()
                input_image_path = f'../tmp/input/{product_id}_{j+1}.{extension}'
                image.save(input_image_path)
            except Exception as e:
                print(f"Error while downloading image: {e}")
                j += 1
                continue

            tryon_available = is_available_for_tryon(input_image_path)
            if not tryon_available:
                os.remove(input_image_path)
                j += 1
                continue

            # output_image_path = remove_background(input_image_path)
            # output_image_path = background_remover_cloth(input_image_path)

            # copy the output image to ./tmp/tryon
            # final_image_path = f"../tmp/tryon/{product_id}_{j+1}.png"
            # shutil.copyfile(output_image_path, final_image_path)

            # os.remove(input_image_path)

            output_df.loc[len(output_df)] = [
                product_id,
                category,
                sub_category,
                image_url,
                score_list[j],
                input_image_path
            ]

            break

        print(f"Processed products {i+1}/{len(df)}")
        output_df.to_csv("products_tryon_output.csv", index=False)


if __name__ == "__main__":
    generate_image_for_tryon()
