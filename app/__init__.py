##
# @mainpage Сайт пользовательских путеводителей
#
# @section description_main Description
# Позволяет пользователям создавать путеводители в специальном редактор, просматрировать и комментировать их.

##
# @file 
#
# @brief Файл инициализации пакета.
#
# @section desctiption_init Description
# В данном файле производится инициализация приложения и базы данных. Отсюда приложение app можеть быть импортировано и дополнено/запущено в любом другом файле.

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

from app.config import config

app = Flask(__name__)
app.secret_key = config["SITE"]["secret_key"]
app.config['SQLALCHEMY_DATABASE_URI'] = config["DATABASE"]["uri"]
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = config["SITE"]["upload_folder"]
db = SQLAlchemy(app)
manager = LoginManager(app)

from app import models, routes
from app import logic

with app.app_context():
    db.create_all()
    logic.init_db()
    

