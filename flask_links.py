from flask import Flask, render_template, request, make_response, redirect, url_for
from database.models import Link, User
import shelve

app = Flask(__name__)
UsersDB = None
LinksDB = None


@app.route('/')
def index():
    login = request.cookies.get('LinkLoader')
    if login:
        return redirect('/userpage_{}'.format(login), 302)
    return render_template('registration_form.html')


@app.route('/login_user', methods=['POST'])
def login_user():
    login = request.form['login_field']
    password = request.form['password_field']
    if 'need_new_user' in request.form:
        code = add_new_user(login, password)
        if not code:
            return 'User already exists!'
    if login not in UsersDB:
        return 'User doesnt exist'
    response = make_response('', 302)
    response.headers['Location'] = '/userpage_{}'.format(login)
    response.set_cookie('LinkLoader', login)
    return response


def add_new_user(login, password):
    if login in UsersDB:
        return False
    UsersDB[login] = User(login, password, [])
    UsersDB.sync()
    return True

@app.route('/userpage_<login>')
def user_page(login):
    cookie_login = request.cookies.get('LinkLoader')
    if cookie_login != login or login not in UsersDB:
        return redirect(url_for('index'))
    return render_template('user_page.html', user_links=get_user_links(login))

@app.route('/add_link', methods=['POST', ])
def add_link():
    long_link = fix_url(request.form['long_link'])
    if not long_link:
        return redirect(url_for('index'))
    LinksDB['Last'] += 1
    short_link = hex(LinksDB['Last'])[2:]
    LinksDB.sync()
    login = request.cookies.get('LinkLoader')
    if login:
        flag = 'need_delete' in request.form
        LinksDB[short_link] = Link(short_link, long_link, flag)
        UsersDB[login].links.append(short_link)
        UsersDB.sync()
        return redirect('/userpage_{}'.format(login))
    else:
        return 'Unregistered user'


def get_user_links(login):
    links = []
    for short in UsersDB[login].links:
        links.append(LinksDB[short])
    return links


@app.route('/delete_link_<short>', methods=['POST'])
def delete_link(short):
    login = request.cookies.get('LinkLoader')
    if login:
        delete_link_from(short, login)
        return redirect('/userpage_{}'.format(login), 302)
    return 'Bad user'


def delete_link_from(short, login):
    if not login:
        login = list(filter(lambda u: short in u.links, UsersDB.values()))[0].name
    user_links = UsersDB[login].links
    user_links.remove(short)
    UsersDB[login].links = user_links
    UsersDB.sync()
    del LinksDB[short]
    LinksDB.sync()


@app.route('/<short>')
def get_long_link(short):
    if short in LinksDB:
        link = LinksDB[short]
        if link.flag:
            delete_link_from(short, None)
        link.count += 1
        return redirect('http://' + link.long)
    return "Bad short link"


def fix_url(url):
    if not url:
        return None
    if url.startswith('http://'):
        url = url[7:]
    return url


if __name__ == '__main__':
    UsersDB = shelve.open('database/users', writeback=True)
    LinksDB = shelve.open('database/links', writeback=True)
    try:
        app.debug = True
        app.run()
    finally:
        UsersDB.close()
        LinksDB.close()