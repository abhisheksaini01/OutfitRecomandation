from flask import Flask, render_template, request, redirect, url_for, jsonify
import requests
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException 
from datetime import datetime


app = Flask(__name__)

# Configuration
OPENWEATHERMAP_API_KEY = 'f00c38e0279b7bc85480c3fe775d518c'
TWILIO_ACCOUNT_SID = 'AC8bc0054195b0122cdfe646b0f6f064c2'
TWILIO_AUTH_TOKEN = '9e5f3b7d5dc9e2a7a6eb33554cc45305'
TWILIO_PHONE_NUMBER = '+13142549174'

# Global variable to store weather data temporarily
weather_data = {}

def fetch_weather(city):
    url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHERMAP_API_KEY}&units=metric'
    response = requests.get(url)
    response.raise_for_status()
    return response.json()


def get_time_of_day():
    current_hour = datetime.now().hour
    print(current_hour)
    if 6 <= current_hour < 18:  # Assuming day is from 6 AM to 6 PM
        return "day"
    else:
        return "night"



# def recommend_outfit(temperature):
#     if temperature < 10:
#         return "Wear a heavy coat, gloves, and a hat."
#     elif 10 <= temperature < 20:
#         return "Wear a light jacket and long pants."
#     else:
#         return "Wear a t-shirt and shorts."




def recommend_outfit(temperature,humidity,wind_speed,time_of_day,occasion,gender):
    outfit_recommendation = ""

    # Basic temperature-based recommendations
    if temperature < 10:
        outfit_recommendation += "Wear a heavy coat, gloves, and a hat."
    elif 10 <= temperature < 20:
        outfit_recommendation += "Wear a light jacket and long pants."
    else:
        outfit_recommendation += "Wear a t-shirt and shorts."

    # Humidity-based recommendations
    if humidity > 70:
        outfit_recommendation += " Since it's humid, consider breathable fabrics."
    elif humidity < 30:
        outfit_recommendation += " With low humidity, you might feel dry, so lightweight clothing is ideal."

    # Wind-based recommendations
    if wind_speed > 15:  # Assuming wind speed is in m/s
        outfit_recommendation += " It's quite windy, so a windbreaker would be a good choice."

    # Day or Night recommendations
    if time_of_day == "night":
        outfit_recommendation += " At night, it can get cooler, so a light sweater or jacket might be necessary."

    # Occasion-based recommendations based on gender
    if occasion == "casual":
        if gender == "male":
            outfit_recommendation += " For casual wear, consider a comfortable t-shirt and jeans."
        else:
            outfit_recommendation += " For casual wear, consider a nice blouse and jeans."
    elif occasion == "formal":
        if gender == "male":
            outfit_recommendation += " For formal occasions, wear a suit and dress shoes."
        else:
            outfit_recommendation += " For formal occasions, wear a formal dress and heels."
    elif occasion == "sports":
        outfit_recommendation += " For sports, wear comfortable athletic wear and sneakers."
    elif occasion == "party":
        if gender == "male":
            outfit_recommendation += " For a party, wear a smart casual shirt and chinos."
        else:
            outfit_recommendation += " For a party, wear a nice dress or a stylish outfit."
    elif occasion == "wedding":
        if gender == "male":
            outfit_recommendation += " For a wedding, consider a suit or a tuxedo."
        else:
            outfit_recommendation += " For a wedding, wear an elegant dress."
    elif occasion == "engagement":
        if gender == "male":
            outfit_recommendation += " For an engagement, a nice blazer with smart trousers is suitable."
        else:
            outfit_recommendation += " For an engagement, a beautiful dress or gown would be perfect."
    elif occasion == "reception":
        if gender == "male":
            outfit_recommendation += " For a reception, wear a formal suit with a tie."
        else:
            outfit_recommendation += " For a reception, opt for a chic dress."

    return outfit_recommendation

#/////----------------------------------------------------






def send_whatsapp_message(name, number, city, outfit):
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    message = (f"Hello {name},\n\n"
               f"The current weather in {city} is as follows:\n"
               f"Temperature: {weather_data['main']['temp']}°C\n"
               f"Humidity: {weather_data['main']['humidity']}%\n"
               f"Pressure: {weather_data['main']['pressure']} hPa\n"
               f"Weather: {weather_data['weather'][0]['description']}\n"
               f"Wind Speed: {weather_data['wind']['speed']} m/s\n\n"
               f"We recommend you to {outfit}.\n\n"
               f"Stay comfortable and have a great day!")
    try:
        print(f"Sending message to {number}...")
        msg = client.messages.create(
            body=message,
            from_=TWILIO_PHONE_NUMBER,
            # whatsapp:
            to=f'{number}'
        )
        print(f"Message sent: SID={msg.sid}")
    except TwilioRestException as e:
        print(f"Failed to send message: {e}")
        print(f"Twilio Error Code: {e.code}")
        print(f"Twilio Error Message: {e.msg}")
        print(f"More information: {e.more_info}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    global weather_data
    
    # name = request.form['name']
    # number = request.form['number']
    # city = request.form['city']

    name = request.form['name']
    number = request.form['number']
    gender = request.form['gender']  # New gender input from the form
    city = request.form['city']
    occasion = request.form['occasion']  # Occasion input from the form
   
      


    
    try:
        weather_data = fetch_weather(city)
        temperature = weather_data['main']['temp']
        humidity = weather_data['main']['humidity']
        wind_speed = weather_data['wind']['speed']
        time_of_day = get_time_of_day()# Time of day input from the form
        outfit = recommend_outfit(temperature,humidity,wind_speed,time_of_day,occasion,gender)
        
        send_whatsapp_message(name, number, city, outfit)
        
        return redirect(url_for('details', name=name, city=city))
    except requests.exceptions.HTTPError as http_err:
        return jsonify({'error': f'HTTP error occurred: {http_err}'}), 500
    except Exception as err:
        return jsonify({'error': f'An error occurred: {err}'}), 500

@app.route('/details')
def details():
    global weather_data
    if not weather_data:
        return redirect(url_for('index'))

    temperature = weather_data['main']['temp']
    humidity = weather_data['main']['humidity']
    pressure = weather_data['main']['pressure']
    weather_description = weather_data['weather'][0]['description']
    wind_speed = weather_data['wind']['speed']
    time_of_day=get_time_of_day()
    name=request.args.get('name')
    city=request.args.get('city')
    occasion=request.args.get('occasion')
    gender=request.args.get('gender')

    outfit = recommend_outfit(temperature,humidity,wind_speed,time_of_day,occasion,gender)
    
    name = request.args.get('name')
    city = request.args.get('city')
    
    return render_template('details.html', temperature=temperature, humidity=humidity, pressure=pressure, weather_description=weather_description, wind_speed=wind_speed, outfit=outfit, name=name, city=city)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)