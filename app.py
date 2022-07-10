import os
import sqlite3

from flask import Flask, render_template, url_for, \
    request, session, redirect, abort, g


from werkzeug.security import generate_password_hash, check_password_hash

from FDataBase import FDataBase

DATABASE = '/tmp/auth.db'
DEBUG = True
SECRET_KEY = 'sjdlkfjaseortigfujasldkfj'

app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(dict(DATABASE=os.path.join(app.root_path, 'auth.db')))


def connect_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn


def create_db():
    db = connect_db()
    with app.open_resource('sq_db.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    db.close()


def get_db():
    if not hasattr(g, 'link_db'):
        g.link_db = connect_db()
    return g.link_db


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'link_db'):
        g.link_db.close()


dbase = None


@app.before_request
def before_request():
    global dbase
    db = get_db()
    dbase = FDataBase(db)


@app.route('/registration', methods=['POST', 'GET'])
def registration():
    if request.method == 'POST' \
            and len(request.form['username']) > 3 \
            and len(request.form['password']) > 3:
        hash = generate_password_hash(request.form['password'])
        res = dbase.addProfile(request.form['username'], hash)
        print(hash)
        if not res:
            return 'Username already taken'
        session['userLogged'] = request.form['username']
        return redirect(url_for('profile', username=session['userLogged']))
    return render_template('registration.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    #TODO: checking if the profile exists
    if 'userLogged' in session:
        return redirect(url_for('profile', username=session['userLogged']))
    elif request.method == 'POST' \
            and len(request.form['username']) > 3 \
            and len(request.form['password']) > 3:
        db_psw_hash = dbase.getProfile(request.form['username'])
        if check_password_hash(db_psw_hash, request.form['password']):
            session['userLogged'] = request.form['username']
            return redirect(url_for('profile', username=session['userLogged']))
    return render_template('login.html')


@app.route('/profile/<path:username>')
def profile(username):
    if 'userLogged' not in session or session['userLogged'] != username:
        abort(401)
    return render_template('profile.html', username=username)


@app.route('/logout')
def logout():
    session.pop('userLogged')
    return 'Logout'


if __name__ == '__main__':
    app.run(debug=DEBUG)
