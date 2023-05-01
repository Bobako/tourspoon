##
# @file 
#
# @brief Файл с эндпоинтами.
#
# @section desctiption_routes Description
# Файл содержит функции, используемые программой для получения, обработки и ответа на запросы клиента.

from flask import render_template, redirect, url_for, request, flash, abort
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import check_password_hash, generate_password_hash


from app import app, db, manager
from app.models import User, Tour, TourBlock,TourReaction, TourTag
from app.logic import process_tour, save_file
from app import config


@manager.unauthorized_handler
def unauthorized():
    """! Служебная функция для модуля flask_login, перенаправляет неавторизованных пользователей,
    попытавшихся войти на страницу, требующую авторизации, на страницу авторизации"""
    return redirect(url_for("login_page") + f"?next={request.url}")

@app.route("/login", methods=['post', 'get'])
def login_page():
    """! Эндпоинт авторизации"""
    if current_user:
        logout_user()
    if request.method == "POST":
        login = request.form.get("login")
        password = request.form.get("password")
        if not (user := db.session.query(User).filter(User.login == login).first()):
            flash("Пользователь не найден")
        else:
            if not(check_password_hash(user.password_hash, password)):
                flash("Неверный пароль")
            else:
                login_user(user)
                user.is_authenticated = True
                next_page = request.args.get('next')
                if not next_page:
                    next_page = url_for('index_page')
                db.session.commit()
                return redirect(next_page)
    return render_template("login.html")

@app.route('/reg', methods=['post', 'get'])
def reg():
    """! Эндпоинт регистрации"""
    if request.method == 'POST':
        login = request.form.get('login')
        password = request.form.get('password')
        repass = request.form.get('repass')

        if password != repass:
            flash("Введенные пароли не совпадают")
        elif login == "" or password == "":
            flash("Поля не должны быть пустыми")
        elif db.session.query(User).filter(User.login == login).first():
            flash("Имя пользователя занято")
        else:
            db.session.add(User(login, generate_password_hash(password)))
            db.session.commit()
            user = db.session.query(User).filter(User.login == login).one()
            login_user(user)
            user.is_authenticated = True
            db.session.commit()
            return redirect(url_for("index_page"))

    return render_template("reg.html", warning="")
    
@app.route('/', methods=['get'])
def index_page():
    """! Эндпоинт главной страницы.
    Отрисовывает страницу, включая туда путеводители, полученные из бд, исходя из фильтров переданных в аргументах.
    """
    search = request.args.get("s")
    category_id = request.args.get("c")
    by_user_id = request.args.get("u")
    
    not_moderated = False    # получать ТОЛЬКО не модерированные туры, для модераторов
    user = None
    if current_user:
        if not current_user.is_anonymous:
            user = current_user
            if current_user.is_moderator:
                not_moderated = request.args.get("nm")
                
    moderation_enabled = config["SITE"]["moderation_enabled"] != "0"
    query = db.session.query(Tour)
    
    check_self = False # посмотерть свои публикации, включая не модерированные
    
    if search:
        query = query.filter(Tour.name.like(f"%{search}%"))
    if by_user_id:
        query = query.filter(Tour.created_by_id == by_user_id)
        if user:
            if by_user_id == user.id:
                check_self = True
                
    if (moderation_enabled and not not_moderated) and (not check_self):
        query = query.filter(Tour.moderated_by_id != None)
        
    if not_moderated:
        query = query.filter(Tour.moderated_by_id == None)
    
    if not check_self:
        query = query.filter(Tour.archived==False)
    tours = query.all()
    
    if category_id:
        category = db.session.query(TourTag).filter(TourTag.id == category_id).first()
        tours = [tour for tour in tours if category in tour.tags]
    
    tags = db.session.query(TourTag).all()
    
    return render_template("index.html", tours=tours, user=user, tags=tags)
        
        
        
    
    
    

@app.route('/tour/<tour_id>', methods=['get', 'post'])
def tour_page(tour_id):
    """! Эндпоинт просмотра/изменения/создания путеводителя. Для просмотра или изменения требует id, для создания id=create"""
    if tour_id != 'create':
        tour = db.session.query(Tour).filter(Tour.id == tour_id).first()
        if not tour:
            abort(404)
        edit_mode = request.args.get("edit_mode")
        if edit_mode:
            if not current_user:
                return redirect(url_for("login_page")+"?next="+request.path)
            if tour.created_by_id != current_user.id:
                abort(403)  # permission denied
            if request.method == "POST":
                process_tour(request.form, tour_id, current_user, request.files)
            return render_template("edit_tour.html", 
                                   tour=tour,
                                   tags = db.session.query(TourTag).all())            
        else:
            user = None
            if current_user:
                if not current_user.is_anonymous:
                    user = current_user
            if request.method == 'POST':
                reaction = TourReaction(
                    request.form.get("text"),
                    int(request.form.get("beauty_criteria")),
                    int(request.form.get("route_smoothness_criteria")),
                    int(request.form.get("attractions_criteria")),
                    int(request.form.get("accessibility_criteria")),
                    user.id,
                    tour_id                    
                )
                db.session.add(reaction)
                db.session.commit()
            return render_template("tour.html",
                                   tour = tour,
                                   user = user
                                    )
    else:
        if not current_user:
            return redirect(url_for("login_page")+"?next="+request.path)
        if current_user.is_anonymous:
            return redirect(url_for("login_page")+"?next="+request.path)
        else:
            if request.method == "POST":
                new_tour_id = process_tour(request.form, tour_id, current_user, request.files)
                return redirect(url_for('tour_page', tour_id=new_tour_id))
            return render_template("edit_tour.html",
                                   tour=None,
                                   tags = db.session.query(TourTag).all())
            

@app.route('/cab', methods=['get', 'post'])
@login_required
def cab_page():
    """! Эндпоинт личного кабинета"""
    if request.method == "POST":
        if current_user.is_moderator:
            grant_login = request.form.get("grant")
            if grant_login:
                grant_user = db.session.query(User).filter(User.login == grant_login).first()
                if grant_user:
                    grant_user.is_moderator = True
                    db.session.commit()
                else:
                    flash("Пользователь не найден")
                
        login = request.form.get("login")
        bio = request.form.get("bio")
        password = request.form.get("password")
        repass = request.form.get("repass")
        
        photo = request.files.get("profile_phote")
        
        if photo:
            profile_photo_path = save_file(photo)
            current_user.profile_photo_path = profile_photo_path
        
        if login:
            if db.session.query(User).filter(User.login == login).first():
                flash("Логин занят")
            else:
                current_user.login = login
                
        if password:
            if password != repass:
                flash("Пароли не совпадают")
            else:
                current_user.password_hash = generate_password_hash(password)
        current_user.bio = bio
        
        db.session.commit()
    return render_template("cab.html", user=current_user)
            
@app.route('/api/get_tour_canvas/<tour_id>', methods=['get'])
def get_tour_canvas(tour_id):
    """! Эндпоинт получения элементов путеводителя."""
    tour = db.session.query(Tour).filter(Tour.id == tour_id).first()
    return render_template("tour_canvas.html", tour=tour)
    
        

@app.route('/api/delete')
def delete():
    """! Эндпоинт удаления путеводителя/комментария. Требует передачи типа и идентификатора в аргументах запроса."""
    type_ = request.args.get("t")
    id_ = request.args.get("id")
    if type_ == "tour":
        tour = db.session.query(Tour).filter(Tour.id == id_).first()
        db.session.delete(tour)
    elif type_ == "reaction":
        reaction = db.session.query(TourReaction).filter(TourReaction.id == id_).first()
        db.session.delete(reaction)
    db.session.commit()
    return "ok"
    
@app.route('/api/moderate')
def moderate():
    """! Эндпоинт, чтобы отметить путеводитель как модерированный, требует перадачи идентификаторов путеводителя и модератора в аргументах запроса."""
    tour_id = request.args.get("tid")
    moderator_id = request.args.get("mid")
    tour = db.session.query(Tour).filter(Tour.id == tour_id).first()
    tour.moderated_by_id = moderator_id
    db.session.commit()
    return "ok"
    