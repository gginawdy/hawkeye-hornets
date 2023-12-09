from flask import Flask, render_template, request, redirect, url_for,session
from pymongo import MongoClient 
from ubidots import ApiClient
from bson import ObjectId  # Impor ObjectId dari bson
from datetime import datetime, timedelta



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
client = MongoClient("mongodb+srv://distraokta:distraokta1228@cluster0.cybfqid.mongodb.net/?retryWrites=true&w=majority")
db = client.agendaguru
collection = db.isiagenda

db_siswa = client.datasiswa
collection_siswa = db.siswa


@app.route('/input')
def input_attendance():
    # Mengambil data nama guru, mata pelajaran, dan kelas dari MongoDB
    guru_names = [entry['name'] for entry in db.guru_info.find({"name": {"$exists": True}})]
    mata_pelajaran = [entry['subject'] for entry in db.guru_info.find({"subject": {"$exists": True}})]
    kelas = [entry['classroom'] for entry in db.guru_info.find({"classroom": {"$exists": True}})]

    # Menggunakan set untuk menghilangkan duplikasi
    guru_names = list(set(guru_names))
    mata_pelajaran = list(set(mata_pelajaran))
    kelas = list(set(kelas))

    return render_template('input.html', guru_names=guru_names, mata_pelajaran=mata_pelajaran, kelas=kelas)


@app.route('/save_attendance', methods=['POST'])
def save_attendance():
    date = request.form['date']
    name = request.form['name']
    subject = request.form['subject']
    classroom = request.form['classroom']

    # Menambahkan timestamp saat entri dibuat
    timestamp = datetime.now()

    entry = {
        'date': date,
        'name': name,
        'subject': subject,
        'classroom': classroom,
        'timestamp': timestamp  # Tambahkan timestamp saat entri dibuat
    }

    collection.insert_one(entry)
    return {'success': True}


@app.route('/attendance', methods=['GET'])
def attendance_data():
    # Dapatkan semua data kehadiran dari MongoDB
    data = list(collection.find())

    # Dapatkan parameter filter dari URL
    filter_name = request.args.get('filter_name')
    filter_subject = request.args.get('filter_subject')
    filter_classroom = request.args.get('filter_classroom')

    # Buat daftar _id yang akan dihapus dari parameter query
    ids_to_exclude = request.args.getlist('exclude')

    # Dapatkan waktu sekarang
    current_time = datetime.now()

    # Buat daftar data yang tidak termasuk dalam _ids_to_exclude dan berusia kurang dari 24 jam
    filtered_data = []
    for entry in data:
        if str(entry['_id']) not in ids_to_exclude and 'timestamp' in entry:
            timestamp = entry['timestamp']
            time_difference = current_time - timestamp
            if time_difference < timedelta(days=1):
                filtered_data.append(entry)

    # Terapkan filter berdasarkan nama guru, mata pelajaran, dan kelas jika disediakan
    if filter_name:
        filtered_data = [entry for entry in filtered_data if entry['name'] == filter_name]

    if filter_subject:
        filtered_data = [entry for entry in filtered_data if entry['subject'] == filter_subject]

    if filter_classroom:
        filtered_data = [entry for entry in filtered_data if entry['classroom'] == filter_classroom]

    return render_template('attendance_data.html', data=filtered_data)

@app.route('/delete/<string:data_id>', methods=['GET'])
def delete_attendance(data_id):
    # Menghapus data dengan _id yang sesuai dari MongoDB
    collection.delete_one({'_id': ObjectId(data_id)})
    
    # Redirect kembali ke halaman data kehadiran dengan parameter exclude
    return redirect(f'/attendance?exclude={data_id}')

# Perbarui fungsi attendance_data_siswa
@app.route('/attendance_siswa', methods=['GET'])
def attendance_data_siswa():
    # Dapatkan semua data kehadiran siswa dari MongoDB (collection_siswa)
    data_siswa = list(collection_siswa.find())

    # Dapatkan parameter filter dari URL
    filter_name = request.args.get('filter_name')
    filter_subject = request.args.get('filter_subject')
    filter_classroom = request.args.get('filter_classroom')

    # Buat daftar _id yang akan dihapus dari parameter query
    ids_to_exclude = request.args.getlist('exclude')

    # Buat daftar data yang tidak termasuk dalam _ids_to_exclude
    filtered_data = [entry for entry in data_siswa if str(entry['_id']) not in ids_to_exclude]

    # Terapkan filter berdasarkan nama guru, mata pelajaran, dan kelas jika disediakan
    if filter_name:
        filtered_data = [entry for entry in filtered_data if entry['name'] == filter_name]

    if filter_subject:
        filtered_data = [entry for entry in filtered_data if entry['subject'] == filter_subject]

    if filter_classroom:
        filtered_data = [entry for entry in filtered_data if entry['classroom'] == filter_classroom]

    # Kirim data ke template siswa.html
    return render_template('siswa.html', kehadiran=filtered_data)

@app.route('/update_attendance/<string:data_id>', methods=['POST'])
def update_attendance(data_id):
    date = request.form['date']
    name = request.form['name']
    subject = request.form['subject']
    classroom = request.form['classroom']

    # Update data kehadiran berdasarkan _id
    collection.update_one({'_id': ObjectId(data_id)}, {'$set': {'date': date, 'name': name, 'subject': subject, 'classroom': classroom}})

    # Redirect kembali ke halaman data kehadiran guru
    return redirect('/attendance')


@app.route('/edit/<string:data_id>', methods=['GET'])
def edit_attendance(data_id):
    # Dapatkan data kehadiran berdasarkan _id
    entry = collection.find_one({'_id': ObjectId(data_id)})

    # Mengambil data nama guru, mata pelajaran, dan kelas dari MongoDB
    guru_names = [entry['name'] for entry in db.guru_info.find({"name": {"$exists": True}})]
    mata_pelajaran = [entry['subject'] for entry in db.guru_info.find({"subject": {"$exists": True}})]
    kelas = [entry['classroom'] for entry in db.guru_info.find({"classroom": {"$exists": True}})]

    # Menggunakan set untuk menghilangkan duplikasi
    guru_names = list(set(guru_names))
    mata_pelajaran = list(set(mata_pelajaran))
    kelas = list(set(kelas))

    return render_template('edit_attendance.html', entry=entry, guru_names=guru_names, mata_pelajaran=mata_pelajaran, kelas=kelas)







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
