import uuid
from .post import Post
from datetime import datetime
from src import Database, constants


class Blog(object):

    def __init__(self, author_id, author, title, description, _id=None):
        self._id = uuid.uuid4().hex if _id is None else _id
        self.author = author
        self.author_id = author_id
        self.title = title
        self.description = description
        self.post = None

    def new_post(self, title, content, date=datetime.utcnow()):
        self.post = Post(
            blog_id=self._id,
            title=title,
            content=content,
            created_at=datetime.strptime(date, '%d%m%Y') if date else datetime.utcnow(),
            author=self.author
        )
        self.post.save_to_mongo()
        return self.post.json()

    def save_to_mongo(self):
        Database.insert(collection=constants.BLOG_COLLECTION,
                        data=self.json())

    def json(self):
        return {
            '_id': self._id,
            'author_id': self.author_id,
            'author': self.author,
            'title': self.title,
            'description': self.description
        }

    @classmethod
    def from_mongo(cls, __i):
        blog = Database.find_one(
            collection=constants.BLOG_COLLECTION,
            query={"_id": __i}
        )
        return cls(**blog)

    def get_posts(self):
        return Post.from_blog(self._id)

    @classmethod
    def find_by_author_id(cls, author_id):
        all_blog = Database.find(
            constants.BLOG_COLLECTION,
            {"author_id": author_id}
        )
        return [cls(**blog) for blog in all_blog]
