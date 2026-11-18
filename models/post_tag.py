"""Post_Tag (liga posts e tags): responsável Ian."""
from extensoes import db


class Post_Tag(db.Model):
    __tablename__ = "post_tag"

    post_id = db.Column(db.Integer, db.ForeignKey("post.id"), primary_key=True)
    tag_id = db.Column(db.Integer, db.ForeignKey("tag.id"), primary_key=True)
