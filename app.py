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

    return render_template("index.html")

@app.route('/contact')
def contact():

    return render_template("contact.html")

@app.route('/profile')
@login_required
def profile():

    return render_template("profile.html",current_user=current_user)

@app.route('/add', methods=['GET', 'POST'])
def add():
    return render_template("add.html")

@app.route('/edit_user', methods=['GET', 'POST'])
@login_required
def edit_user():
    if request.method == 'POST':
        id = current_user.id
        new_username = request.form.get('username') if request.form.get('username') else current_user.username
        new_email =  request.form.get('email') if request.form.get('email') else current_user.email
        new_name = request.form.get('name') if request.form.get('name') else current_user.name
        new_sex = request.form.get('sex') if request.form.get('sex') else current_user.sex
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
    
    return render_template("land.html",datas=land)
    

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
            cur.execute("INSERT INTO user (full_name, email, password,role) VALUES (?, ?, ?,?)", (name, email, hashed_password,0))
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
            if current_user.is_authenticated:
                user = current_user.id
                name = request.form['name']
                cur.execute("INSERT INTO land (name,temperature, humidity, moisture,netrogen,phosphore,potassium,user,fertelizer) VALUES (?,?,?,?,?, ?, ?,?,?)",
                        (name, temperature, humidity, moisture, nitrogen, phosphorous, potassium, user, result))
                con.commit()
                cur.close()
                con.close()
            return render_template('result.html', data=fer)
    

@app.route('/editLand', methods=['GET', 'POST'])
@login_required
def editLand():
    if request.method == 'POST':
        land_id = request.form.get('land_id')
        con = sqlite3.connect("akal.db")
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute("SELECT * FROM land WHERE land_id = ?", (land_id,))
        land = cur.fetchone()
        print(land)

        moisture = float(request.form['moisture']) if request.form['moisture'] else land["moisture"]
        temperature = float(request.form['temperateur']) if request.form['temperateur'] else land["temperature"]
        humidity = float(request.form['humidity']) if request.form['humidity'] else land["humidity"]
        nitrogen = float(request.form['netrogen']) if request.form['netrogen'] else land["netrogen"]
        potassium = float(request.form['potassium']) if request.form['potassium'] else land["potassium"]
        phosphorous = float(request.form['phosphore']) if request.form['phosphore'] else land["phosphore"]

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

        cur.execute("SELECT * FROM fertilizer WHERE name = ?", (result,))
        fer = cur.fetchone()
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


if __name__ == '__main__':
    app.run(debug=True)
