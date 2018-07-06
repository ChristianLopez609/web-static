from flask import Flask, g, render_template, jsonify, url_for, flash
from flask import request, redirect, make_response
from flask import session as login_session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from functools import wraps
from database_setup import Base, User, Post # Declaro tablas y base de datos.
#from oauth2client.client import flow_from_clientsecrets, FlowExchangeError
import random
import string
import json
import datetime
import hashlib
#import httplib2
import requests
# Importo para poder subir archivos tipo imagenes.
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Conecta con base de datos y crea la sesion de la base de datos.
engine = create_engine('sqlite:///primer_web.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

UPLOAD_FOLDER = 'static/imagenes'
ALLOWED_EXTENSIONS = set(['png','jpg','jpeg'])

# Mostrar Todo
@app.route('/', methods=['GET'])
@app.route('/index', methods=['GET'])
def showMain():
	posts = session.query(Post).all()

	if 'username' in login_session:
		username = login_session['username']
		return render_template('public.html', posts = posts, username = username) 
	else:
		return render_template('public.html', posts = posts)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Crear Post.
@app.route('/load_post', methods=['GET', 'POST'])
def upload():
	if request.method == 'GET':
		username = login_session['username']
		return render_template('load_post.html', username = username)
	else:
		if 'imagen' not in request.files:
			flash('No file part')
			return redirect(url_for('showMain'))
		file = request.files['imagen']
		if file.filename == '':
			flash('No selected file')
			return redirect(request.url)
		if file and allowed_file(file.filename):
			filename = secure_filename(file.filename)
			print(filename)
			ruta = os.path.join(UPLOAD_FOLDER, filename)
			print(ruta)
			file.save(os.path.join(UPLOAD_FOLDER, filename))
			nuevoPost = Post(
				imagen = filename,
				titulo = request.form['titulo'],
				contenido = request.form['contenido'],
				url = request.form['url']
				)
			session.add(nuevoPost)
			session.commit()
			return redirect(url_for('showMain'))

# Borrar Post.
@app.route('/delete_post/<int:id>', methods=['GET','POST'])
def delete(id):
	post = session.query(Post).filter_by(id = id).one()
	if request.method == 'GET':
		username = login_session['username']
		return render_template('delete_post.html', post = post, username= username)
	else:
		if request.method == 'POST':
			session.delete(post)
			session.commit()
			return redirect(url_for('showMain'))

def login_required(f): 
	@wraps(f)
	def decorated_function(*args, **kwargs):
		if 'username' not in login_session:
			return redirect(url_for('login'))
		return f(*args, **kwargs)
	return decorated_function

# Inicio de hasheo de contraseña para el registro en la BD.
def make_salt():
	return ''.join(random.choice(
				string.ascii_uppercase + string.digits) for x in range(32))
		
def make_pw_hash(name, pw, salt = None):
	if not salt:
		salt = make_salt()
	h = hashlib.sha256((name + pw + salt).encode('utf-8')).hexdigest()
	return '%s,%s' % (salt, h)

def valid_pw(name, password, h):
	salt = h.split(',')[0]
	return h == make_pw_hash(name, password, salt)
# Fin de hasheo

# Abrir sesion
@app.route('/login', methods=['GET', 'POST'])
def login():
	if request.method == 'GET':
		state = ''.join(random.choice(
				string.ascii_uppercase + string.digits) for x in range(32))
		# store it in session for later use
		login_session['state'] = state
		return render_template('login.html', STATE = state)
	else:
		if request.method == 'POST':
			user = session.query(User).filter_by(
				email = request.form['email']).first()

			if user and valid_pw(request.form['email'],
								request.form['password'],
								user.pw_hash):
				login_session['username'] = user.username
				return render_template('index.html', username=login_session['username'])
			else:
				error = "Usuario no Registrado!"
				return render_template('login.html', error = error)

# Cerrar sesion
@app.route('/logout')
def logout():
		
		del login_session['username']

		return redirect(url_for('showMain'))

# Registrar Usuario
@app.route('/register', methods=['GET', 'POST'])
def register():
	if request.method == 'GET':
		return render_template('register.html')
	else:
		if request.method == 'POST':
			username = request.form['username']
			password = request.form['password']
			email = request.form['email']

			pw_hash = make_pw_hash(email, password)
			nuevoUsuario = User(
				username = username,
				email = email,
				pw_hash = pw_hash)
			session.add(nuevoUsuario)
			session.commit()
			login_session['username'] = request.form['username']
			return redirect(url_for('showMain'))

# Inicializar
if __name__ == '__main__':
	app.secret_key = "secret key"
	app.debug = True
	app.run(host = '0.0.0.0', port = 8080)
