import random
import sqlite3
from flask import Flask, render_template, jsonify, request, url_for, redirect, make_response, session
import datetime
from config import secret_key

app = Flask("VConnect'e")
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(
    days=365
)
app.config['SECRET_KEY'] = secret_key

error = ''
y_pos = 0

SYMBS = list('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890!')

db = sqlite3.connect('users.db')
cur = sqlite3.Cursor(db)
data = cur.execute(f'''SELECT user, pwd FROM users''').fetchall()
cur.close()
db.close()

db = sqlite3.connect('chats.db')
cur = sqlite3.Cursor(db)
chat_data = cur.execute(f'''SELECT chat_name, user_member FROM chats''').fetchall()
cur.close()
db.close()


@app.route("/logout", methods=["POST", "GET"])
def logout():
    session['logged'] = False
    return redirect('/')


@app.route("/session_test")
def session_test():
    return make_response(
        f"Logged - {session['logged']}")


@app.route('/', methods=["POST", "GET"])
def index():
    logged = session.get('logged', False)
    cur_login = session.get('cur_login', '')
    session['logged'] = False
    session['cur_login'] = ''
    if session["logged"] is True:
        return redirect('/main')
    else:
        return f'''
                <!DOCTYPE html>
                <html lang="en">
                    <head class="main_page">
                        <meta charset="utf-8">
                        <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
                        <link rel="stylesheet" type="text/css" href="{url_for('static', filename='css/style.css')}" />
                        <link type="image/x-icon" href="{url_for('static', filename='img/favicon.ico')}" rel="shortcut icon">
                        <link type="Image/x-icon" href="{url_for('static', filename='img/favicon.ico')}" rel="icon">
                        <title> VConnect'e </title>
                    </head>
    
                    <body class="bg">
                        <div class="system" style="	text-align: center; font-size: 450%">
                            VConnect'e
                        
                        <form action="/login" style="text-align: center;" method="POST">
                            <p></p>
                            <div><input type="text" size="20" class="system" name=login_temp style="font-size: 50%" placeholder="Логин"/></div>
                            <div><input type="password" size="20" class="system" name=password_temp style="font-size: 50%" placeholder="Пароль"/></div>
                            <input type="submit" id=process_input class="system" value=Войти style="font-size: 50%" />
                        </form>
                        
                        <form action="/register" style="text-align: center;" method="POST">
                            <input type="submit" id=process_input class="system" value=Регистрация style="font-size: 50%" />
                        </form>
                        <p class="error" style="text-align: center;"> {error} </p>
    
                        </div>
                    </body>
                </html>
            '''


@app.route('/handler', methods=["POST", "GET"])
def handler():
    global db, cur, y_pos
    message = request.form['message']
    db = sqlite3.connect('chats.db')
    cur = sqlite3.Cursor(db)
    ex = cur.execute(f'''INSERT INTO messages (message, chat_name, user, date) VALUES ("{message}", "{session['chat_name']}", "{session['cur_login']}", "{str(datetime.datetime.now())[:-6]}")''')
    db.commit()
    ex.close()
    cur.close()
    db.close()
    return redirect(f'/chat/{session["chat_name"]}')


@app.route('/chat/<chat_name>', methods=["POST", "GET"])
def chat(chat_name):
    global db, cur, y_pos
    db = sqlite3.connect('chats.db')
    cur = sqlite3.Cursor(db)
    ex = cur.execute(f'''SELECT message, chat_name, user FROM messages''')
    content = []
    y_pos = 6
    cur_chat_name = session.get('chat_name', chat_name)
    session['chat_name'] = chat_name
    for i in ex:
        if i[1] == chat_name and i[2] == session['cur_login']:
            content.append(
                f'''
                    <div style='color: #14A819; position: absolute; top: {y_pos}%; left: 52%' class="big-container">{i[2]}</div>
                    <div style='position: absolute; top: {y_pos + 6}%; left: 52%' class="big-container">{i[0]}</div>
                 '''
            )
            y_pos += 25
        elif i[1] == chat_name:
            content.append(
                f'''
                    <div style='color: #FF3B48; position: absolute; top: {y_pos}%; left: 12%' class="big-container">{i[2]}</div>
                    <div style='position: absolute; top: {y_pos + 6}%; left: 12%' class="big-container">{i[0]}</div>
                '''
                )
            y_pos += 25
    script__scroll = '''
            <script>
                setInterval(function(){   
                    $('html, body').animate({scrollTop: $('html, body').get(0).scrollHeight}, 1000);
                }, 0);
            </script>
        '''

    content.append(
        f'''
            <br>
            <form action="/handler" method="POST">
                <input type="text" class="system" name=message style="font-size: 200%; width: 1450px; height: 50px; position: absolute; top: {y_pos + 25}%" placeholder=""/>
            </form>
        '''
    )

    return f'''
        <!DOCTYPE html>
        <html lang="en">
            <head class="main_page">
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
                <link rel="stylesheet" type="text/css" href="{url_for('static', filename='css/style.css')}" />
                <link type="image/x-icon" href="{url_for('static', filename='img/favicon.ico')}" rel="shortcut icon">
                <link type="Image/x-icon" href="{url_for('static', filename='img/favicon.ico')}" rel="icon">
                <script src="//ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js"></script>
                    {script__scroll}
                <title> VConnect'e </title>
            </head>

            <body class="bg">
                <a href='/main' class="system" style="font-size: 250%"> VConnect'e </a>
                {''.join(content)}
                <a href='/main' class="system" style="font-size: 250%; position: absolute; top: {y_pos + 25}%; left: 85%"> VConnect'e </a>
                <a href='/generate_link' class="system" style="font-size: 250%; position: absolute; top: {y_pos + 20}%; left: 3%"> Пригласить </a>
            </body>
        </html> 
    '''


@app.route('/accept_action', methods=["POST", "GET"])
def accept_action():
    global db, cur, chat_data
    if request.method == "POST":
        chat_name = request.form['name_chat']
        db = sqlite3.connect('chats.db')
        cur = sqlite3.Cursor(db)
        ex = cur.execute(f'''INSERT INTO chats (chat_name, user_member) VALUES ("{chat_name}", "{session['cur_login']}")''')
        db.commit()
        chat_data = cur.execute(f'''SELECT chat_name, user_member FROM chats''').fetchall()
        ex.close()
        return redirect('/main')


@app.route('/generate_link', methods=["POST", "GET"])
def generate_link():
    global db, cur, chat_data
    if session["logged"] is not True:
        return redirect('/')
    else:
        link = []
        for i in range(39):
            link.append(SYMBS[random.randint(0, 62)])
        db = sqlite3.connect('chats.db')
        cur = sqlite3.Cursor(db)
        ex = cur.execute(f'''SELECT chat_name FROM chats''')
        for i in ex:
            if i[0] == session['chat_name']:
                exe = cur.execute(f'''UPDATE chats SET chat_key = "{''.join(link)}" WHERE chat_name = "{session['chat_name']}"''')
                db.commit()
        ex.close()
        cur.close()
        db.close()

        return f'''
                <!DOCTYPE html>
                <html lang="en">
                    <head class="main_page">
                        <meta charset="utf-8">
                        <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
                        <link rel="stylesheet" type="text/css" href="{url_for('static', filename='css/style.css')}" />
                        <link type="image/x-icon" href="{url_for('static', filename='img/favicon.ico')}" rel="shortcut icon">
                        <link type="Image/x-icon" href="{url_for('static', filename='img/favicon.ico')}" rel="icon">
                        <title> VConnect'e </title>
                    </head>

                    <body class="bg">
                        <a href='/main' class="system" style="font-size: 250%"> VConnect'e </a>
                        <div style='background: #666; width: 80%; height: 87%; position: absolute; top: 7%; left: 10%' id="rectangle">
                            <form action="/generation" method="POST">
                                <div class="system" style="font-size: 150%; width: 500px; height: 30px; position: absolute; top: 15%; left: 32%">https://longe.serveo.net/invite/{''.join(link)}</div>
                                <input type="submit" id=process_input class="system" value="Сгенерировать ссылку" style="font-size: 250%; position: absolute; top: 25%; left: 35%" />
                            </form>
                        </div>
                    </body>
                </html> 
            '''


@app.route('/generation', methods=["POST", "GET"])
def generation():
    if session["logged"] is not True:
        return redirect('/')
    else:
        return redirect('/generate_link')


@app.route('/create_chat', methods=["POST", "GET"])
def create_chat():
    if session["logged"] is not True:
        return redirect('/')
    else:
        return f'''
                <!DOCTYPE html>
                <html lang="en">
                    <head class="main_page">
                        <meta charset="utf-8">
                        <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
                        <link rel="stylesheet" type="text/css" href="{url_for('static', filename='css/style.css')}" />
                        <link type="image/x-icon" href="{url_for('static', filename='img/favicon.ico')}" rel="shortcut icon">
                        <link type="Image/x-icon" href="{url_for('static', filename='img/favicon.ico')}" rel="icon">
                        <title> VConnect'e </title>
                    </head>

                    <body class="bg">
                        <a href='/main' class="system" style="font-size: 250%"> VConnect'e </a>
                        <div style='background: #666; width: 80%; height: 87%; position: absolute; top: 7%; left: 10%' id="rectangle">
                            <form action="/accept_action" method="POST">
                                <input type="text" class="system" name=name_chat style="font-size: 150%; width: 500px; height: 30px; position: absolute; top: 15%; left: 34%" placeholder="Название беседы"/>
                                <input type="submit" id=process_input class="system" value="Подтвердить" style="font-size: 250%; position: absolute; top: 25%; left: 42%" />
                            </form>
                            
                        </div>
                    </body>
                </html> 
            '''


@app.route('/invite/<link>', methods=["POST", "GET"])
def invite(link):
    global db, cur
    if session["logged"] is not True:
        return redirect('/')
    else:
        db = sqlite3.connect('chats.db')
        cur = sqlite3.Cursor(db)
        ex = cur.execute('''SELECT chat_name, chat_key FROM chats''')
        for i in ex:
            if link == i[1]:
                exe = cur.execute(f'''INSERT INTO chats (chat_name, user_member) VALUES ("{i[0]}", "{session['cur_login']}")''')
                db.commit()
        ex.close()
        cur.close()
        db.close()
    return redirect('/main')


@app.route('/main', methods=["POST", "GET"])
def main():
    if session["logged"] is not True:
        return redirect('/')
    else:
        list_of_dependences = []
        y_percent = 10
        for i in chat_data:
            if session['cur_login'] == i[1]:
                list_of_dependences.append(f'''
                    <form action="/chat/{i[0]}" method="POST">
                        <input type="submit" id=process_input class="system" value="{i[0]}" style="font-size: 200%; position: absolute; top: {y_percent}%; left: 12%" />
                    </form>
                ''')
                y_percent += 10

        return f'''
                <!DOCTYPE html>
                <html lang="en">
                    <head class="main_page">
                        <meta charset="utf-8">
                        <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
                        <link rel="stylesheet" type="text/css" href="{url_for('static', filename='css/style.css')}" />
                        <link type="image/x-icon" href="{url_for('static', filename='img/favicon.ico')}" rel="shortcut icon">
                        <link type="Image/x-icon" href="{url_for('static', filename='img/favicon.ico')}" rel="icon">
                        <title> VConnect'e </title>
                    </head>
    
                    <body class="bg">
                        <a href='/main' class="system" style="font-size: 250%"> VConnect'e </a>
                        <div id="rectangle" class="big-container" style="width: 80%; height: 80%; position: absolute; top: 7%; left: 10%;"></div>
                        <form action="/logout" method="POST">
                            <input type="submit" id=process_input class="system" value="Выйти из аккаунта" style="font-size: 100%; position: absolute; top: 2%; left: 91%" />
                        </form>
                        <form action="/create_chat" method="POST">
                            <input type="image" src="/static/img/add.webp" alt="Кнопка «input»" id=process_input class="system" style="width: 75px; height: 75px; position: absolute; top: 10%; left: 85%" />
                        </form>
                        {''.join(list_of_dependences)}
                    </body>
                </html> 
            '''


@app.route('/check_valid', methods=["POST", "GET"])
def check_valid():
    global error, data, cur, db
    if request.method == "POST":
        login_name = request.form['login_temp']
        password_name = request.form['password_temp']
        password_name_conf = request.form['password_temp_conf']
        db = sqlite3.connect('users.db')
        cur = sqlite3.Cursor(db)
        if password_name_conf != password_name:
            error = 'Пароли не совпадают!'
            data = cur.execute(f'''SELECT user, pwd FROM users''').fetchall()
            return redirect('/register')
        for i in data:
            if i[0] == login_name:
                error = 'Пользователь с такиим именем уже существует!'
                return redirect('/register')
        ex = cur.execute(f'''INSERT INTO users (user, pwd) VALUES ("{login_name}", "{password_name}")''')
        db.commit()
        data = cur.execute(f'''SELECT user, pwd FROM users''').fetchall()
        ex.close()
        logged = session.get('logged', True)
        cur_login = session.get('cur_login', login_name)
        session['logged'] = True
        session['cur_login'] = login_name
        return redirect('/main')


@app.route('/login', methods=["POST", "GET"])
def login():
    global error, data, cur, db
    if session["logged"] is True:
        return redirect('/main')
    else:
        if request.method == "POST":
            login_name = request.form['login_temp']
            password_name = request.form['password_temp']
            if not login_name:
                error = "Введите логин или зарегистрируйтесь!"
                return redirect('/')

            elif not password_name:
                error = "Введите пароль или зарегистрируйтесь!"
                return redirect('/')

            for i in data:
                if str(i[0]) == login_name:
                    if str(i[1]) == password_name:
                        error = ''
                        logged = session.get('logged', True)
                        cur_login = session.get('cur_login', login_name)
                        session['logged'] = True
                        session['cur_login'] = login_name
                        return redirect('/main')

                    elif str(i[1]) != password_name:
                        error = 'Неправильное имя пользователя или пароль'
                        return redirect('/')
                elif str(i[0]) != password_name and data[data.index(i)] == data[-1]:
                    error = 'Неправильное имя пользователя или пароль'
                    return redirect('/')


@app.route('/register', methods=["POST", "GET"])
def register():
    if session["logged"] is True:
        return redirect('/main')
    else:
        return f'''
            <!DOCTYPE html>
            <html lang="en">
                <head class="main_page">
                    <meta charset="utf-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
                    <link rel="stylesheet" type="text/css" href="{url_for('static', filename='css/style.css')}" />
                    <link type="image/x-icon" href="{url_for('static', filename='img/favicon.ico')}" rel="shortcut icon">
                    <link type="Image/x-icon" href="{url_for('static', filename='img/favicon.ico')}" rel="icon">
                    <title> VConnect'e </title>
                </head>
        
                <body class="bg">
                    <div class="system" style="	text-align: center; font-size: 450%">
                        VConnect'e
                    
                    <form action="/check_valid" style="text-align: center;" method="POST">
                        <p></p>
                        <div><input type="text" size="20" class="system" name=login_temp style="font-size: 50%" placeholder="Имя пользователя"/></div>
                        <div><input type="password" size="20" class="system" name=password_temp style="font-size: 50%" placeholder="Пароль"/></div>
                        <div><input type="password" size="20" class="system" name=password_temp_conf style="font-size: 50%" placeholder="Подтвердите пароль"/></div>
                        <input type="submit" value=Зарегистрироваться class="system" style="font-size: 50%" />
                    </form>
                    
                    <form action="/" method="POST">
                        <input type="submit" id=process_input class="system" value="Уже есть аккаунт" style="font-size: 25%" />
                    </form>
                    
                    <p class="error" style="text-align: center;"> {error} </p>
        
                    </div>
                </body>
            </html> 
        '''


if __name__ == '__main__':
    app.run()
