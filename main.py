from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:build-a-blog@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(120))
    body = db.Column(db.Text)

    def __init__(self, title, body):
        self.title = title
        self.body = body

@app.route('/', methods=['GET'])
def index():

    blogs = Blog.query.all()
    
    return render_template('todos.html', title = "Welcome to Your Home Page", entries = blogs)
 
@app.route('/newpost', methods=['POST','GET'])
def newpost():
    if request.method == 'GET':
        
        return render_template('/newpost.html', title = "Enter Your Blog Entry")    
    
    if request.method == 'POST':
              
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
            new_blog = Blog(blog_title, blog_body)
            db.session.add(new_blog)
            db.session.commit()
            blogentry = Blog.query.get(new_blog.id)
            
            return render_template('/current.html', title = "Enter Your New Blog Post", entry = blogentry)

@app.route('/blog', methods=['GET', 'POST'])
def getblogs(id=0):

    blog_id = request.args.get('id', id)

    
    if blog_id != 0:
        blog = Blog.query.get(blog_id)

        return render_template('/current.html', title = "Enter Your New Blog Post", entry = blog)

    else:
        blogs = Blog.query.all()

        return render_template('/blog.html', title = "Listing of Blogs", entries = blogs)

if __name__ == '__main__':
    app.run()