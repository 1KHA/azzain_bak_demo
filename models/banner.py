from database import db,ma
from datetime import datetime

class Banner(db.Model):
    __tablename__ = 'banners'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    name_ar = db.Column(db.String)
    img_url = db.Column(db.String)
    redirect_url = db.Column(db.String)
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    updated_at = db.Column(
        db.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

class BannerSchema(ma.Schema):
    class Meta:
        fields = ('id','name', 'name_ar', 'img_url', 'redirect_url', 'created_at','updated_at')
        model = Banner
        