##
# @file 
#
# @brief Файл с некоторыми служебными функциями приложения.
#
# @section desctiption_logic Description
# В этот файл необходимо переносить все функции, логика которых слишком объемна для размещения в непосредственно в эндпоинтах routes.py, или может быть использована неоднократно.

import datetime
import uuid
import os


from app import db
from app import models
from app import app
from app.models import Tour, User, TourTag, TourReaction, TourBlock

from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage


def init_db():
    """! Добавить в БД необходимые элементы, если их там нет.
    """
    if not db.session.query(models.TourTag).first():
        tags = ["Природа", "Архитектура", "Гастро", "Развлечения"]
        for tag in tags:
            tag = models.TourTag(tag)
            db.session.add(tag)
        db.session.commit()
        
def process_tour(form, id, user, files):
    """! Обработать данные формы запроса при добавлении/изменении путеводителя добавить/изменить путеводитель в базу данных.
    @param form Форма запроса в формате, используемом Flask.
    @param id Идентификатор изменяемого путеводителя
    @param user Пользователь, вносящий изменения
    @param files Файлы формы в формате, использруемом Flask.
    
    @returns идентификатор изменненого путеводителя
    """
    blocks, tour = process_flask_form(form, ["show_on_map"])
    files_dict = {}
    for key, file in files.lists():
        key = key.split(":")[0]
        if file[0].content_type != 'application/octet-stream':
            files_dict[key] = file[0]

    for file in files_dict.values():
        file: FileStorage
        print(type(file.content_type))
                 
    if id == "create":
        tour_obj = Tour(user.id, tour["tour_name"], 50)
        db.session.add(tour_obj)
        db.session.flush()
    else:
        tour_obj = db.session.query(Tour).filter(Tour.id == id).first()
        tour_obj.name = tour["tour_name"]
        tour_obj.last_updated_at = datetime.datetime.now()
        for block in tour_obj.blocks:
            db.session.delete(block)
        db.session.commit()
    
    max_row = 0    
    for id, block in blocks.items():
        
        if id in files_dict:
            content_path = save_file(files_dict[id])
        else:
            content_path = ""
        
        if "old_content_path" in block and not content_path:
            content_path = block["old_content_path"]    
        if (this_max_row:=int(block["row"]) + int(block["height"])) > max_row:
            max_row = this_max_row
        db.session.add(
            TourBlock(block["name"], block["text"], content_path, block["type_"], block["show_on_map"],
                  block["latitude"], block["longitude"], block["column"], block["row"], block["height"],
                  block["width"], tour_obj.id)
        )
    if "tags" in tour:
        for tag_id in tour["tags"]:
            if (tag:=db.session.query(TourTag).filter(TourTag.id == tag_id).first()) not in tour_obj.tags:
                tour_obj.tags.append(tag)
    tour_obj.canvas_height = max_row - 1
    db.session.commit()
    return tour_obj.id
    
def save_file(file):
    """! Cохраняет файл и возвращает условно уникальное имя.
    @param file файл формы, в формате используемом Flask.
    
    @return Условно уникальное имя файла в директории app/static/contents
    """
    filename = str(uuid.uuid4())
    extenstion = file.filename.split(".")[-1]
    filename = filename + "." + extenstion
    filename = secure_filename(filename)
    path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(path)
    return filename
    
    
        
def process_flask_form(form, checkboxes):
    """! Преобразует форму переданную в  формате, используемом Flask, где поля ввода атрибутов нескольких объектов описывались именами вида <id>:<имя атрибута>, в
    словарь словерей вида {<id>:{<имя атрибута1>:<значение>}}. Для полей ввода без <id>: формирует отдельный словарь вида {<имя атрибута>:<значение>}
    
    @param form Форма запроса в формате, используемом Flask.
    @param checkboxes список имен чекбоксов формы, необходим
    
    @returns словарь объектов, словарь значений полей
     """
    multiples = {}
    main = {}
    for key, val in form.lists():
        if ":" in key:
            id, field_name = key.split(":")
            if not id in multiples:
                multiples[id] = {}
            multiples[id][field_name] = val[0]
        else:
            main[key] = val if len(val) > 1 else val[0]
    for obj in multiples.values():
        for cb in checkboxes:     
            obj[cb] = cb in obj.keys()
            
        
    return multiples, main