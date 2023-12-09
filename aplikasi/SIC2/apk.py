from flask import Flask, render_template, request, redirect, url_for, session
from pymongo import MongoClient

app = Flask (__name__)

# Konfigurasi MongoDB
client = MongoClient("mongodb+srv://distraokta:distraokta1228@cluster0.cybfqid.mongodb.net/?retryWrites=true&w=majority")
db = client.agendaguru
collection = db.isiagenda

if __name__=='__main__' :
    app.run(debug=True)
