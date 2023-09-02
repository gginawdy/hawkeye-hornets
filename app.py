from flask import Flask, render_template, request, redirect, url_for,session
from pymongo import MongoClient 
from ubidots import ApiClient

app = Flask(__name__)


@app.route('/')
def awal():
    return render_template('awal.html')



@app.route('/menu')
def menu():
    return render_template('menu.html')



@app.route('/submenu')
def submenu():
    return render_template('submenu.html')



# Konfigurasi MongoDB
client = MongoClient("mongodb+srv://distraokta:hawkeye161@cluster0.cybfqid.mongodb.net/?retryWrites=true&w=majority")
db = client.Agenda
collection = db.attendance



@app.route('/input')
def input_attendance():
    return render_template('input.html')

@app.route('/save_attendance', methods=['POST'])
def save_attendance():
   
    date = request.form['date']
    name = request.form['name']
    subject = request.form['subject']
    classroom = request.form['classroom']

    entry = {
      
        'date': date,
        'name': name,
        'subject': subject,
        'classroom': classroom
    }

    collection.insert_one(entry)
    return {'success': True}

@app.route('/attendance')
def attendance_data():
    data = list(collection.find())
    return render_template('attendance_data.html', data=data)




# Ubah dengan token dan label yang sesuai dari Ubidots
API_TOKEN = "BBFF-thUhhRPJojoHiUB78bozuZuPy2dKTv"
LABEL_LAMPU = "64cb734bdfc2f3000b9aec5b"
LABEL_KIPAS = "64cc7d13b2f3f5000e41c9d1"
LABEL_TombolGorden = "64d1f43ae26c5fcc5a9e7fb3"
LABEL_SliderGorden = "64cc7d2b97713e000da27763"

api = ApiClient(token=API_TOKEN)
variable_lampu = api.get_variable(LABEL_LAMPU)
variable_kipas = api.get_variable(LABEL_KIPAS)
variable_TombolGorden = api.get_variable(LABEL_TombolGorden)
variable_SliderGorden = api.get_variable(LABEL_SliderGorden)

def toggle_value(current_value):
    if current_value == 0:
        return 1
    else:
        return 0

@app.route('/lampu', methods=['GET', 'POST'])
def lampu():
    if request.method == 'POST':
        current_value = variable_lampu.get_values(1)[0]['value']
        new_value = toggle_value(current_value)
        variable_lampu.save_value({'value': new_value})

    current_value = variable_lampu.get_values(1)[0]['value']
    return render_template('lampu.html', current_value=current_value)


@app.route('/kipas', methods=['GET', 'POST'])
def kipas():
    if request.method == 'POST':
        current_value = variable_kipas.get_values(1)[0]['value']
        new_value = toggle_value(current_value)
        variable_kipas.save_value({'value': new_value})

    current_value = variable_kipas.get_values(1)[0]['value']
    return render_template('kipas.html', current_value=current_value)


@app.route("/roll_blind", methods=["GET", "POST"])
def control_blinds():
    if request.method == "POST":
        slider_value = int(request.form["slider_value"])
        switch_value = int(request.form.get("switch_value", 0))

        if slider_value is not None:
            variable_SliderGorden.save_value({"value": slider_value})

        if switch_value is not None:
            current_value = variable_TombolGorden.get_values(1)[0]['value']
            new_value = toggle_value(current_value)
            variable_TombolGorden.save_value({'value': new_value})

        return redirect(url_for("control_blinds"))

    current_value = variable_TombolGorden.get_values(1)[0]['value']
    return render_template("roll_blind.html", current_value=current_value)


if __name__ == '__main__':
    app.run(debug=True)
