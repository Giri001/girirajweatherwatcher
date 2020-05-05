import requests 
from flask import Flask , render_template , url_for , request , redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Configruation

app = Flask(__name__)

ENV = 'deployment'

if ENV =='dev':
	app.debug = True
	app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Postgresql@9131@localhost/Weather'
else:
	app.debug = False
	app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://ezaddtrvenrtyv:4d21027524dfdc52e235b38481d46a80d93f8547791c3607c8805c200a9c97b0@ec2-54-175-117-212.compute-1.amazonaws.com:5432/d7bngo9ptoaqsv'

app.config['SQLALCHEMY_TRACK_MODIFICATION'] = False

db=SQLAlchemy(app)

class Weather(db.Model):
	__tablename__ = 'Weather'
	id = db.Column(db.Integer, primary_key=True)
	city = db.Column(db.String(100),unique=True, nullable=False)
	temperature = db.Column(db.String(100), nullable=False)
	description = db.Column(db.String(30), nullable=False)
	icon = db.Column(db.String(10), nullable=False)
	date = db.Column(db.DateTime, default=datetime.utcnow)

	def __init__(self,city,temperature,description,icon):
		self.city = city
		self.temperature = temperature
		self.description = description
		self.icon = icon

 # Server Routing Starts from here

@app.route('/')
def index():
	return render_template('weather.html',weather=Weather.query.all())

@app.route('/post',methods=['GET','POST'])
def post():
	all_cities = Weather.query.all()		# Fetch all data from DataBase
	city = request.form['city']
	for i in all_cities:					# This loop checks if entered city is exist in DataBase or not
		if city.lower() == i.city.lower():
			available = True
			on = False
			return render_template('weather.html',weather=Weather.query.all(),city=city,on=on,available=available)

	if request.method == 'POST':			# POST Request from form
		on = True
		if city=='':						# If search box is empty
			return redirect('/')
		else:					
			try:
				url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid=0605788b966a722ad1f556497852e825'			# Fetch the weather data from openweathermap.org from API
				r=requests.get(url).json()
				db.session.add(Weather(city=city.capitalize(), temperature=str(int(r['main']['temp'])-273), description = r['weather'][0]['description'], icon = r['weather'][0]['icon'] ))
				db.session.commit()
				status = True
				return render_template('weather.html',weather=Weather.query.all(),city=city,status=status,on=on)

			except:						# if entered city is not exist
				status = False
				return render_template('weather.html',weather=Weather.query.all(),city=city,status=status,on=on)

	else : 
		return redirect('/')

@app.route('/update_all')				# for updating weather condition of all the cities stored in DataBase
def update_all():
	all_data = Weather.query.all()
	for i in all_data:
		url = f'http://api.openweathermap.org/data/2.5/weather?q={i.city}&appid=0605788b966a722ad1f556497852e825'
		r=requests.get(url).json()
		i.temperature = str(int(r['main']['temp'])-273)
		i.description = r['weather'][0]['description']
		i.icon = r['weather'][0]['icon']
		db.session.commit()
	return redirect('/')

@app.route('/delete/<int:id>')			#For deleting a particular city data
def delete(id):
	dlt_data = Weather.query.get(id)
	db.session.delete(dlt_data)
	db.session.commit()
	return redirect('/')

@app.route('/delete_all')				# For deleting data of all the cities
def delete_all():
	dlt_all=Weather.query.all()
	for i in dlt_all:
			db.session.delete(i)
			db.session.commit()
	return redirect('/')










