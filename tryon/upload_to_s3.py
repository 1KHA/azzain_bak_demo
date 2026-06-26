import pandas as pd
from helpers.aws_bucket import upload_obj_to_s3

def upload_all_clothes_to_s3():
    # Get all the images in the clothes directory
    
    df = pd.read_csv('./tryon/final_tryon_images.csv')
    
    df_uuid = pd.read_csv('./tryon/products_uuid.csv')

    for i in range(len(df)):
        image_path = df['final_image_path'][i]
        product_id = df['product_id'][i]
        uuid = df_uuid[df_uuid['product_id'] == product_id]['product_uuid'].values[0]
        
        filename = image_path.split('/')[-1]
        file_obj = open(f'./tmp/tryon/{filename}', 'rb')

        upload_status = upload_obj_to_s3(
            file=file_obj,
            file_name=f'{uuid}.png',
            bucket_path='images/products/try_on/input/clothes'
        )
        if upload_status:
            print(f"Succesfully uploaded {filename}")
        
        file_obj.close()
        print(f"Processed {i}/{len(df)} images")