from src import Database, constants
import uuid
from datetime import datetime


class Post(object):

    def __init__(self, blog_id, title, content, author, created_at=datetime.now(), _id=None):
        #  default parameters are allowed in end

        self._id = uuid.uuid4().hex if not _id else _id
        self.blog_id = blog_id
        self.title = title
        self.content = content
        self.author = author
        self.created_at = created_at

    def save_to_mongo(self):
        Database.insert(collection=constants.POST_COLLECTION,
                        data=self.json()
                        )

    def json(self):
        return {
            '_id': self._id,
            'title': self.title,
            'content': self.content,
            'author': self.author,
            'blog_id': self.blog_id,
            'created_at': self.created_at
        }

    @classmethod
    def from_mongo(cls, uid):
        post_elem = Database.find_one(
            collection=constants.POST_COLLECTION,
            query={'_id': uid}
        )
        return cls(**post_elem).json()

    @staticmethod
    def from_blog(uid):
        return [post for post in Database.find(
            collection=constants.POST_COLLECTION,
            query={'blog_id': uid}
        )]
