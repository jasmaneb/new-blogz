from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'HappyFeet'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(120))
    body = db.Column(db.Text)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
 
    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.String(120), unique = True)
    password = db.Column(db.String(120))
    name = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, email, password, name):
        self.email = email
        self.password = password
        self.name = name

@app.before_request
def require_login():
    allowed_routes = ['signup', 'login', 'index', 'getblogs']
    if request.endpoint not in allowed_routes and 'email' not in session:
        return redirect('/login')


@app.route('/signup', methods = ['POST', 'GET'])
def signup():
    if request.method == 'POST':
        email = str(request.form['email'])
        password = str(request.form['password'])
        verify = str(request.form['verify'])
        verify_error = ""
        username_error = ""
        password_error = ""

        if len(email) < 3:
            username_error = 'Username must contain at least 3 characters'
            flash("Email must contain at least 3 characters", 'error')

        if len (email) == 0:
            username_error = "You need to enter an email address"
            flash("You need to enter an email address", 'error')

        if len(password) == 0:
            password_error = "You need to enter a password"
            flash("You need to enter a password", 'error')

        if len(verify) == 0:
            verify_error = "You need to verify your password"
            flash("You need to verify your password", 'error')

        if password != verify:
            flash("Your password and verify field must match", 'error')
            verify_error ="Your passwords do not match, Please try again"
            return redirect('/signup')

        if not verify_error and not username_error:
        
            existing_user = User.query.filter_by(email=email).first()
            if not existing_user:
                new_user = User(email, password)
                db.session.add(new_user)
                db.session.commit()
                session['email'] = email
                return redirect('/newpost')
        else: 
            return render_template('signup.html', verify_error = verify_error, username_error = username_error, password_error = password_error)

    return render_template('signup.html')

@app.route('/login', methods = ['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.password == password:
            session['email'] = email
            flash(" You are Logged In", 'success')
            print(session)
            return redirect('/newpost')
        else:
            flash("User password is incorrect or user does not exist", 'error')

    return render_template('/login.html')

@app.route('/logout')
def logout():
    del session['email']
    return redirect('/')

@app.route('/newpost', methods=['POST','GET'])
def newpost():
    if request.method == 'GET':
        
        return render_template('/newpost.html', title = "Enter Your Blog Entry")    
    
    if request.method == 'POST':
        owner = User.query.filter_by(email=session['email']).first() 
        blog_title = request.form['title']
        blog_body = request.form['body']
        body_error = ""
        title_error = ""

        if len(blog_title) == 0:
            title_error = "Invalid Entry, You need to create a title for this blog!"
        
        if len(blog_body) == 0:
            body_error = "Invalid Entry, You need to create a body for this blog!"

        if len(title_error) > 0 or len(body_error) > 0:
            return render_template('/newpost.html', title_error = title_error, body_error = body_error, blog_title = blog_title, blog_body = blog_body)

        else: 
            new_blog = Blog(blog_title, blog_body, owner)
            db.session.add(new_blog)
            db.session.commit()
            blogs = Blog.query.filter_by(owner = owner). all()
            blogentry = Blog.query.get(new_blog.id) 
            return redirect ('/blog?blogid='+ str(new_blog.id ))

@app.route('/blog')
def getblogs(id=0):
    blog_id = request.args.get('blogid', id)
    user_id = request.args.get('userid', id)
    
    if blog_id != 0:
        blog = Blog.query.get(blog_id)
        return render_template('/current.html', title = "Here is your specified Blog Post", entry = blog)

    elif user_id != 0:
        user = User.query.get(user_id)
        return render_template('/singleUser.html', title = "Here are the post by your chosen Blogger", user = user)

    else:
        blogs = Blog.query.all()
        return render_template('/blog.html', title = "Listing of Blogs", entries = blogs)

@app.route('/', methods=['GET'])
def index():
    users = User.query.all()
    return render_template('index.html', title = "Welcome to Your Home Page", users=users)
 

if __name__ == '__main__':
    app.run()