from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_required, login_user, logout_user, current_user, UserMixin
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import pandas as pd
import pickle
import os
import uuid

app = Flask(__name__)
app.secret_key = "super secret key"
app.config['UPLOAD_FOLDER'] = os.path.join('static','images', 'uploads')
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

model_file = open('model.pkl', 'rb')
model = pickle.load(model_file)
model_file.close()


class User(UserMixin):
    def __init__(self, user_id, full_name, email, password,sex,age,about,username,profile_path,role):
        self.id = user_id
        self.name = full_name
        self.email = email
        self.password = password
        self.sex = sex
        self.age = age
        self.about = about
        self.username = username
        self.profile_path = profile_path
        self.role = role


@login_manager.user_loader
def load_user(user_id):
    con = sqlite3.connect("akal.db")
    cur = con.cursor()
    cur.execute("SELECT * FROM user WHERE user_id = ?", (user_id,))
    user = cur.fetchone()
    if user:
        return User(user_id=user[0], full_name=user[1], email=user[2], password=user[3],sex=user[4],age=user[5],about=user[6],username=user[7],profile_path=user[8],role=user[9])
    return None

@app.route('/')
def index():
    length = getCartItems()

    return render_template("index.html",length=length)

@login_required
def getCartItems():
    con = sqlite3.connect("akal.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute('''
        SELECT 
            owned.name, 
            owned.many, 
            fertilizer.price, 
            fertilizer.land_src
        FROM 
            owned
        JOIN 
            fertilizer 
        ON 
            owned.name = fertilizer.name
        WHERE 
            owned.user_id = ?
    ''', (current_user.id,))
    
    results = cur.fetchall()
    con.close()
    length = len(results)
    return length

@login_required
def getMessagesLength():
    con = sqlite3.connect("akal.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("SELECT * FROM message ")
    msgs = cur.fetchall()
    cur.close()
    con.close()
    length= len(msgs)
    return length

@app.route('/contact')
def contact():
    length = getCartItems()
    messagesLength=getMessagesLength()
  
    return render_template("contact.html",length=length,messagesLength=messagesLength)

@app.route('/contactRequest',methods=['GET', 'POST'])
def contactRequest():
    if request.method == 'POST':
        name= request.form['name']
        email= request.form['email']
        message= request.form['message']
        con = sqlite3.connect("akal.db")
        cur = con.cursor()
        cur.execute("INSERT INTO message (name, email, message,opened) VALUES (?, ?, ?,?)", (name, email, message,0))
        con.commit()
        con.close()
        return redirect(url_for('contact'))



@app.route('/profile')
@login_required
def profile():
    length = getCartItems()
    messagesLength=getMessagesLength()
    return render_template("profile.html",current_user=current_user,length=length,messagesLength=messagesLength)

@app.route('/add', methods=['GET', 'POST'])
def add():
    
    return render_template("add.html")



@app.route('/editFerilizer', methods=['GET', 'POST'])
def editFerilizer():
    length = getCartItems()
    messagesLength=getMessagesLength()
    if request.method == 'POST':
            fertilizer_name = request.form['fertilizer_name']
            con = sqlite3.connect("akal.db")
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            cur.execute("SELECT * FROM fertilizer WHERE name = ?", (fertilizer_name,))
            fertilizer = cur.fetchone()
            con.commit()
            con.close()
            
            if land and current_user.role == 1:
                return render_template('editFerilizer.html', info=fertilizer)
            else :
                return render_template('notFound.html', length=length,messagesLength=messagesLength)
    if current_user.role == 1:
        return render_template('editFerilizer.html', info=fertilizer,messagesLength=messagesLength)
    else :
        return render_template('notFound.html', length=length,messagesLength=messagesLength)

@app.route('/editRequest', methods=['GET', 'POST'])
def editRequest():
    if request.method == 'POST':
            con = sqlite3.connect("akal.db")
            cur = con.cursor()
            fertilizer_name = request.form['fertilizer_name']
            cur.execute("SELECT description FROM fertilizer WHERE name = ?", (fertilizer_name,))
            original = cur.fetchone()
            description = request.form['description']  if request.form['description'] else original[0]
            price = request.form['price']
            quantity = request.form['quantity']
            cur.execute("UPDATE fertilizer SET price = ?, quantity = ? ,description = ? WHERE name = ?", (price,quantity,description, fertilizer_name))
            con.commit()
            con.close()
            return redirect(url_for('manageFertilizers'))
            

@app.route('/edit_user', methods=['GET', 'POST'])
@login_required
def edit_user():
    if request.method == 'POST':
        id = current_user.id
        new_username = request.form.get('username') 
        new_email =  request.form.get('email')
        new_name = request.form.get('name') 
        new_sex = request.form.get('sex')
        new_age = request.form.get('age') if request.form.get('age') else current_user.age
        new_about = request.form.get('about') if request.form.get('about') else current_user.about
        
        con = sqlite3.connect("akal.db")
        cur = con.cursor()
        cur.execute("SELECT * FROM user WHERE user_id = ?", (id,))
        user = cur.fetchone()

        if user:
            cur.execute("UPDATE user SET username = ?, email = ? ,full_name = ?, sex = ? ,age = ?, about = ? WHERE user_id = ?", (new_username, new_email,new_name,new_sex,new_age,new_about, id))
            con.commit()
        con.close()
        return redirect(url_for('profile'))
    return render_template('profile.html')

@app.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    if request.method == 'POST':
    
            land_id = request.form['land_id']
            con = sqlite3.connect("akal.db")
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            cur.execute("SELECT * FROM land WHERE land_id = ?", (land_id,))
            land = cur.fetchone()
            con.commit()
            con.close()
            
            if land:
                return render_template('edit.html', info=land)
    return render_template('edit.html')

@app.route('/delete', methods=['GET', 'POST'])
@login_required
def delete():
    id=request.form['land_id']
    con = sqlite3.connect("akal.db")
    cur = con.cursor()
    cur.execute("DELETE FROM land WHERE land_id = ?", (id,))
    con.commit()
    cur.close()
    con.close()
    return redirect(url_for('land'))

@app.route('/essai')
def essai():

    return render_template("essai.html")


@app.route('/result')
def result():

    return render_template("result.html")

@app.route('/manageUsers')
@login_required
def manageUsers():
    messagesLength=getMessagesLength()
    con = sqlite3.connect("akal.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("SELECT user_id, username, role, profile_path, email  FROM user")
    users = cur.fetchall()  
    con.close()
    if current_user.role == 1:
        return render_template("manageUsers.html",users=users,messagesLength=messagesLength)
    else:
        return render_template("profile.html",current_user=current_user)
    

@app.route('/deleteUsers', methods=['GET', 'POST'])
@login_required
def deleteUsers():
    id=request.form['user_id']
    con = sqlite3.connect("akal.db")
    cur = con.cursor()
    cur.execute("DELETE FROM user WHERE user_id = ?", (id,))
    con.commit()
    cur.close()
    con.close()
    return redirect(url_for('manageUsers'))

@app.route('/manageFertilizers')
@login_required
def manageFertilizers():
    con = sqlite3.connect("akal.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("SELECT * FROM fertilizer")
    fertilizers = cur.fetchall()  
    con.close()
    messagesLength=getMessagesLength()
    if(current_user.role == 1):
        return render_template("manageFertilizers.html" , datas=fertilizers,messagesLength=messagesLength)
    else:
        return render_template("profile.html",current_user=current_user)



@app.route('/shopAll')
@login_required
def shopAll():
    con = sqlite3.connect("akal.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("SELECT * FROM fertilizer")
    fertilizers = cur.fetchall()  
    con.close()
    length = getCartItems()
    messagesLength=getMessagesLength()

    return render_template("shopAll.html",datas=fertilizers,length=length,messagesLength=messagesLength)


@app.route('/shopFull')
@login_required
def shopFull():
    con = sqlite3.connect("akal.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("SELECT * FROM fertilizer WHERE quantity > 0")
    fertilizers = cur.fetchall()  
    con.close()
    length = getCartItems()
    messagesLength=getMessagesLength()

    return render_template("shopFull.html",datas=fertilizers,length=length,messagesLength=messagesLength)


@app.route('/shopOut')
@login_required
def shopOut():
    con = sqlite3.connect("akal.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("SELECT * FROM fertilizer WHERE quantity = ? ", (0,))
    fertilizers = cur.fetchall()  
    con.close()
    length = getCartItems()
    messagesLength=getMessagesLength()

    return render_template("shopOut.html",datas=fertilizers,length=length,messagesLength=messagesLength)

@app.route('/buy',methods=['POST','GET'])
@login_required
def buy():
    if request.method == 'POST':
        name = request.form['fertilizer_name']
        con = sqlite3.connect("akal.db")
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute("SELECT * FROM fertilizer WHERE name = ?", (name,))
        fertilizer = cur.fetchone()
        con.commit()
        con.close()
        length = getCartItems()
        messagesLength=getMessagesLength()
            
        if fertilizer:
            return render_template('buy.html', info=fertilizer,length=length,messagesLength=messagesLength)


@app.route('/buyRequest',methods=['POST','GET'])
@login_required
def buyRequest():
    many = float(request.form['many'])
    name = request.form['name']
    user =  current_user.id
    con = sqlite3.connect("akal.db")
    cur = con.cursor()
    cur.execute("SELECT * FROM owned WHERE name = ? and user_id = ?", (name,user))
    fertilizer = cur.fetchone()
    if(fertilizer) :
        cur.execute('UPDATE owned SET many = ? WHERE user_id = ? AND name = ?', (fertilizer[2] + many, user,name))
    else :
        cur.execute("INSERT INTO owned (user_id, name, many) VALUES (?, ?, ?)", (user, name, many))
    cur.execute("SELECT quantity FROM fertilizer WHERE name = ? ", (name,))
    old = cur.fetchall() 
    oldNumber = int(old[0][0])
    cur.execute('UPDATE fertilizer SET quantity = ? WHERE name = ?', (oldNumber - many,name))
    con.commit()
    con.close()
    
    return redirect(url_for('shopAll'))


@app.route('/cart')
@login_required
def cart():
    user = current_user.id
    con = sqlite3.connect("akal.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute('''
        SELECT 
            owned.name, 
            owned.many, 
            fertilizer.price, 
            fertilizer.land_src
        FROM 
            owned
        JOIN 
            fertilizer 
        ON 
            owned.name = fertilizer.name
        WHERE 
            owned.user_id = ?
    ''', (user,))
    
    results = cur.fetchall()
    con.close()
    length = len(results)
    messagesLength=getMessagesLength()

    return render_template("cart.html",datas=results,length=length,messagesLength=messagesLength)

@app.route('/messages')
@login_required
def messages(): 
    con = sqlite3.connect("akal.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("SELECT * FROM message ")
    msgs = cur.fetchall()
    cur.close()
    con.close()
    messagesLength=getMessagesLength()

    if current_user.role == 1:
        return render_template("messages.html",msgs=msgs,messagesLength=messagesLength)
    else :
        return render_template("notFound.html",)


@app.route('/messageDetails',methods = ['GET','POST'])
@login_required
def messageDetails():
    if request.method == 'POST':
        length = getCartItems()
        id= request.form['msg_id']
        con = sqlite3.connect("akal.db")
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute("SELECT * FROM message WHERE message_id=?",(id,))
        msg = cur.fetchone()
        cur.execute("UPDATE message SET opened =? WHERE message_id=?",(1,id,))
        con.commit()
        cur.close()
        con.close()
        messagesLength=getMessagesLength()
        if current_user.role == 1:
            return render_template("messageDetails.html",msg=msg,messagesLength=messagesLength)
        else :
            return render_template("notFound.html",length=length,messagesLength=messagesLength)

@app.route('/deleteMessage',methods = ['GET','POST'])
@login_required
def deleteMessage():
    if request.method == 'POST':
        id= request.form['msg_id']
        con = sqlite3.connect("akal.db")
        cur = con.cursor()
        cur.execute("DELETE FROM message WHERE message_id=?",(id,))
        con.commit()
        cur.close()
        con.close()
        return redirect(url_for('messages'))


@app.route('/land')
@login_required
def land():
    con = sqlite3.connect("akal.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("""
            SELECT l.name,l.land_id, l.moisture, l.temperature, l.phosphore, f.name AS fertilizer_name,f.land_src AS land_src
            FROM land AS l
            INNER JOIN fertilizer AS f ON l.fertelizer = f.name
            WHERE l.user = ?
        """, (current_user.id,))
    land = cur.fetchall()  
    con.close()
    length=getCartItems()
    messagesLength=getMessagesLength()
    if current_user.role ==1 :
        return render_template("profile.html",messagesLength=messagesLength)
    else:
        return render_template("land.html",datas=land,length=length)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        con = sqlite3.connect("akal.db")
        cur = con.cursor()
        cur.execute("SELECT * FROM user WHERE email = ?", (email,))
        user = cur.fetchone()
        if user and check_password_hash(user[3], password):
            user_obj = User(user_id=user[0], full_name=user[1], email=user[2], password=user[3],sex=user[4],age=user[5],about=user[6],username=user[7],profile_path=user[8],role=user[9])
            login_user(user_obj)
            return redirect(url_for('profile'))
        else:
            flash('Invalid email or password.', 'error')
        cur.close()
        con.close()
    return render_template("login.html")

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        con = sqlite3.connect("akal.db")
        cur = con.cursor()
        cur.execute("SELECT * FROM user WHERE email = ?", (email,))
        existingUser = cur.fetchone()
        if(existingUser) :
            flash("This Email Alrady Exists")
            return redirect(url_for("signup"))
        else :
            cur.execute("INSERT INTO user (username, email, password,role) VALUES (?, ?, ?,?)", (name, email, hashed_password,0))
            con.commit()
            return redirect(url_for("login"))
    return render_template("signup.html")

@app.route('/predict', methods=['GET', 'POST'])
def predict():
    if request.method == 'POST':
            moisture = float(request.form['moisture'])
            temperature = float(request.form['temperateur'])
            humidity = float(request.form['humidity'])
            nitrogen = float(request.form['netrogen'])
            potassium = float(request.form['potassium'])
            phosphorous = float(request.form['phosphore'])
            
            input_data = pd.DataFrame({
                'Temparature': [temperature],
                'Humidity': [humidity],
                'Moisture': [moisture],
                'Nitrogen': [nitrogen],
                'Potassium': [potassium],
                'Phosphorous': [phosphorous],
            })
        
            prediction = model.predict(input_data)
            if '/' in prediction[0]:
                parts = prediction[0].split('/')
                year = parts[2].replace('20', '', 1)  
                result = f"{parts[0]}-{parts[1]}-{year}"
            else :
                result=prediction[0]

        
            con = sqlite3.connect("akal.db")
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            cur.execute("SELECT * FROM fertilizer WHERE name = ?", (result,))
            fer = cur.fetchone()

            land_id = request.form.get('land_id') 

            if not land_id: 
                if current_user.is_authenticated:
                    user = current_user.id
                    name = request.form['name']
                    cur.execute("INSERT INTO land (name,temperature, humidity, moisture,netrogen,phosphore,potassium,user,fertelizer) VALUES (?,?,?,?,?, ?, ?,?,?)",
                        (name, temperature, humidity, moisture, nitrogen, phosphorous, potassium, user, result))
            else: 
                cur.execute("UPDATE land SET  moisture = ?, temperature = ?, humidity = ?, potassium = ?, phosphore = ?, fertelizer = ?, netrogen = ? WHERE land_id = ?",
                    ( moisture, temperature, humidity, potassium, phosphorous,result, nitrogen, land_id))
            con.commit()
            cur.close()
            con.close()
            return render_template('result.html', data=fer)
    

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_file():
    if request.method == 'POST':
            file = request.files['file']
            if file:
                unique_filename = str(uuid.uuid4()) + os.path.splitext(file.filename)[1]
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                file.save(filepath)
                con = sqlite3.connect("akal.db")
                cur = con.cursor()
                cur.execute('UPDATE user SET profile_path = ? WHERE user_id = ?', (filepath, current_user.id))
                con.commit()
                cur.close()
                con.close()
                return redirect(url_for('profile'))

@app.route("/delete_image", methods=['GET', 'POST'])
@login_required
def delete_image():
    con = sqlite3.connect("akal.db")
    cur = con.cursor()
    cur.execute('UPDATE user SET profile_path = ? WHERE user_id = ?', (None, current_user.id))
    con.commit()
    cur.close()
    con.close()
    return redirect(url_for('profile'))

@app.route('/<path:path>')
def notFound(path):
    return render_template("notFound.html")

# @app.errorhandler(404)
# def page_not_found(e):
#     return render_template('notFound.html')

# @app.errorhandler(500)
# def internal_server_error(e):
#     return render_template('notFound.html')


if __name__ == '__main__':
    app.run(debug=True)
