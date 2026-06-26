from datetime import datetime
from database import db,ma

class SkinTone(db.Model):
    __tablename__ = 'skin_tones'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    color_code = db.Column(db.String, nullable=False)
    created_at = db.Column(db.TIMESTAMP, nullable=False,
                           default=datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, nullable=False,
                           default=datetime.utcnow, onupdate=datetime.utcnow)

    # def __repr__(self):
    #     return f"SkinTone(id={self.id}, name={self.name}, color_code={self.color_code})"
    
class SkinToneSchema(ma.Schema):
    class Meta:
        fields = ('id','name','color_code','created_at', 'updated_at')
        model = SkinTone