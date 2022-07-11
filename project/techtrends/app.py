import sqlite3
from logging import getLogger, config
import os
import sys
from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort


stdout_fileno = sys.stdout
stderr_fileno = sys.stderr

db_connection_count = 0
with open("logging.json") as f:
    config.dictConfig(json.load(f))

logger = getLogger(os.path.basename(__file__).replace(".py",""))

def get_db_connection():
    global db_connection_count
    db_name = 'database.db'

    connection = sqlite3.connect(db_name)
    connection.row_factory = sqlite3.Row
    db_connection_count += 1
    return connection

def get_posts():
    connection = get_db_connection()
    posts = connection.execute('SELECT COUNT(id) FROM posts').fetchone()[0]
    logger.info("get all posts: {}".format(posts))
    return posts

def is_exist_table(table):
    connection = get_db_connection()
    table = connection.execute("SELECT COUNT(*) FROM sqlite_master WHERE TYPE='table' AND name='{}'"
                                .format(table)).fetchone()[0]
    if table > 0:
        return True
    else:
        return False

# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()
    return post

# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

# Define the main route of the web application
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    title = post[2]
    logger.info("Article {} retrieved!".format(title))
    stdout_fileno.write("Article {} retrieved!\n".format(title))
    if post is None:
        return render_template('404.html'), 404
    else:
        return render_template('post.html', post=post)

# Define the healthz page
@app.route('/healthz')
def healthz():
    if not is_exist_table("posts"):
        response = app.response_class(
                response=json.dumps({"result":"ERROR - unhealthy"}),
                status=500,
                mimetype='application/json'
        )
        return response
    response = app.response_class(
            response=json.dumps({"result":"OK - healthy"}),
            status=200,
            mimetype='application/json'
    )
    return response

# Define the metrics page
@app.route('/metrics')
def metrics():
    response = app.response_class(
            response=json.dumps({"db_connection_count": db_connection_count, "post_count": get_posts()}),
            status=200,
            mimetype='application/json'
    )
    return response

# Define the About Us page
@app.route('/about')
def about():
    logger.info("retrieved About Us page")
    stdout_fileno.write("retrieved About Us page\n")
    return render_template('about.html')

@app.errorhandler(404)
def page_not_found(e):
    logger.error("page not found: {}".format(e))
    stderr_fileno.write("page not found: {}\n".format(e))
    return render_template("404.html"), 404

# Define the post creation functionality
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            connection.close()
            logger.info("create new article title: {}".format(title))

            return redirect(url_for('index'))
    return render_template('create.html')

# start the application on port 3111
if __name__ == "__main__":
    app.run(host='0.0.0.0', port='3111')
