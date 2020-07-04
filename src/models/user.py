from src import Database, constants
import uuid
from flask import session
from src.models import Blog


class User(object):
    def __init__(self, email, password, _id=None):
        self.email = email
        print(email, "  ", type(self.email))
        self.password = password
        self._id = uuid.uuid4().hex if not _id else _id

    @classmethod
    def get_by_email(cls, email):
        user = Database.find_one(collection=constants.USER_COLLECTION,
                                 query={"email": email})
        if user:
            print(user)
            return cls(**user)
        return None

    @classmethod
    def get_by_id(cls, _id):
        user = Database.find_one(collection=constants.USER_COLLECTION,
                                 query={"_id": _id})
        if user:
            return cls(**user)
        return None

    def is_login_valid(self):
        """
        Check if the email and password are valid
        :return: Boolean
        """
        user = User.get_by_email(self.email)
        if user:
            return user.password == self.password
        return False

    @classmethod
    def register(cls, email, password):
        if not len(email) or not len(password):
            return False
        user = cls.get_by_email(email)
        if not user:
            new_user = cls(email, password)
            new_user.save_to_mongo()
            session.__setitem__('email', email)
            return True
        return False

    @staticmethod
    def login(email):
        session.__setitem__('email', email)

    @staticmethod
    def logout():
        session.__setitem__('email', None)

    def get_blogs(self):
        return Blog.find_by_author_id(self._id)

    def new_blog(self, title, description):
        blog = Blog(
            author=self.email,
            title=title,
            description=description,
            author_id=self._id
        )
        blog.save_to_mongo()

    @staticmethod
    def new_post(blog_id, title, content):
        blog = Blog.from_mongo(blog_id)
        blog.new_post(title=title, content=content)

    def json(self):
        return {
            'email': self.email,
            '_id': self._id,
            "password": self.password
        }

    def save_to_mongo(self):
        Database.insert(
            constants.USER_COLLECTION,
            self.json()
        )

    def update_user(self, new_email, new_password=None):
        Database.update(
            constants.USER_COLLECTION,
            {"email": self.email},
            {"$set":
                 {
                     "email": new_email if new_email else self.email,
                     "password": new_password if new_password else self.password
                 }
            }
        )
