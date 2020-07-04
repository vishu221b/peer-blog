from flask import (
    Flask, render_template, request,
    session, redirect, url_for
)
from src.models import User
from src import Database, constants
from src.models import Blog, Post


app = Flask(__name__)
app.secret_key = "NotSecure"


@app.before_first_request
def initialize_db():
    Database.initialize()


@app.route('/')
def home():
    posts = Database.find(constants.POST_COLLECTION, {})
    return render_template(
        'home.html', blogs=[post for post in posts]
    )


@app.route('/profile/update', methods=['POST'])
@app.route('/profile')
def my_profile():
    prompt_message = ""
    prompt_success = ""
    if request.method == 'POST':
        new_email = request.form.get('updateEmail')
        user = User.get_by_email(new_email)
        if user and user.email != session.get('email'):
            prompt_message = 'A user with the same email already exists.'
        elif not user and len(new_email):
            new_password = request.form.get('updatePassword')
            p = new_password if len(new_password) > 0 else None
            current_user = User.get_by_email(session.get('email'))
            current_user.update_user(new_email, p)
            session.__setitem__('email', new_email)
            prompt_success = 'Details updated successfully'
        elif not len(new_email):
            new_password = request.form.get('updatePassword')
            p = new_password if len(new_password) > 0 else None
            current_user = User.get_by_email(session.get('email'))
            current_user.update_user(None, p)
            prompt_success = "Password updated successfully."
    return render_template('profile.html', prompt_message=prompt_message, prompt_success=prompt_success)


# ------------------------auth----------------------------------
@app.route('/register')
def register():
    return render_template('register.html', prompt_message = "")


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/logout')
def logout():
    User.logout()
    return redirect('/')


@app.route('/auth/login', methods=['POST'])
def login_user():
    email = request.form['email']
    password = request.form['password']
    user = User(email=email, password=password)
    if user.is_login_valid():
        user.login(email)
    else:
        session.__setitem__('email', None)
    return redirect('/', code=302)


@app.route('/auth/register', methods=['POST'])
def register_user():
    # prompt_alert = ""
    email = request.form.get('email')
    password = request.form.get('password')
    if not len(email) or not len(password):
        prompt_alert = "Please enter valid email and password values."
    elif User.register(email, password):
        return redirect('/', code=302)
    else:
        prompt_alert = 'User with the same email already exists!'
    return render_template('register.html', prompt_message=prompt_alert)


@app.route('/search')
def search():
    pattern = request.args['pattern']
    result = Database.find(constants.BLOG_COLLECTION,
                           {"$or": [{"title": {"$regex": u"{}".format(pattern)}},
                                    {"author": {"$regex": u"{}".format(pattern)}}
                                    ]
                            }
                           )
    li = [r for r in result]
    print(li)
    return render_template('search.html', email=li)

# ----------------------------Blogs-----------------------------------


@app.route('/blog/<user_id>')
@app.route('/myblogs')
def get_blogs(user_id=None):
    user = None
    if user_id:
        user = User.get_by_id(user_id)
    elif not user_id:
        user = User.get_by_email(session.get('email'))
    if not user:
        return render_template('error_404.html')
    user_blogs = user.get_blogs()
    return render_template('myblogs.html', blogs=user_blogs, email=session.get('email'), c=0)


@app.route('/blog/create', methods=['POST'])
def create_new_blog():
    user = User.get_by_email(session.get('email'))
    title = request.form.get('blogTitle')
    description = request.form.get('blogDescription')
    blog = Blog(title=title, description=description, author=user.email, author_id=user._id)
    blog.save_to_mongo()
    return redirect('/myblogs')


# -----------------------------Posts----------------------------------
@app.route('/post/<blog_id>/create', methods=['GET', 'POST'])
def create_new_post(blog_id):
    if request.method == 'POST':
        title = request.form.get('postTitle')
        content = request.form.get('postContent')
        blog = Blog.from_mongo(blog_id)
        response = blog.new_post(title=title, content=content)
        return redirect('/post/{}'.format(response.get('_id')), code=302)
    else:
        return render_template('create-post.html', blog_id=blog_id)


@app.route('/posts/<blog_id>')
def get_posts_for_blog(blog_id):
    blog = Blog.from_mongo(blog_id)
    posts = blog.get_posts()
    return render_template("all-posts.html", posts=posts, blog_title=blog.title, blog_id=blog._id)


@app.route('/post/<post_id>', methods=['GET'])
def get_single_post(post_id=None):
    post = Post.from_mongo(post_id)
    return render_template('single-post.html', post=post)


if __name__ == "__main__":
    app.run(port=5000, debug=True)
