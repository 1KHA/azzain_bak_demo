from database import db
from app import app
from models import Products
import pandas as pd

def update_tryon_status():
    """
        Set tryon_available flag to True for all the products
        present in the final_tryon_images.csv file
    """
    with app.app_context():
        df = pd.read_csv('./tryon/final_tryon_images.csv')
        for i in range(len(df)):
            product = Products.query.filter_by(
                product_id=df['product_id'][i]).first()
            if not product:
                print(f"Product with id {df['product_id'][i]} not found")
                continue
            product.tryon_available = True
            db.session.commit()
            print(f"Processed products {i+1}/{len(df)}")












            