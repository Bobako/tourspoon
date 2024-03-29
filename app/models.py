##
# @file 
#
# @brief Файл с ORM моделями.
#
# @section desctiption_models Description
# Файл содержит классы, используесые программой, которые в то же время являются схемами таблиц баз данных.


import datetime

from flask_login import UserMixin

from app import db, manager


class User(db.Model, UserMixin):
    """! Класс пользователя"""
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(50))  # login can be edited, so there is separate primary key
    password_hash = db.Column(db.String(32), nullable=False)
    is_moderator = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, nullable=False)
    profile_photo_path = db.Column(db.String(50))
    bio = db.Column(db.String(200))

    # Отношения
    tours = db.relationship("Tour", back_populates="created_by", cascade="all, delete",
                            foreign_keys="[Tour.created_by_id]")
    moderated_tours = db.relationship("Tour", back_populates="moderated_by", foreign_keys="[Tour.moderated_by_id]")
    favourite_tags = db.relationship('TourTag', secondary='users_to_tags_association', lazy='dynamic', backref='users')
    reactions = db.relationship('TourReaction', back_populates='created_by', cascade="all, delete")

    # cлужебные поля для модуля flask_login
    is_authenticated = db.Column(db.Boolean)
    is_active = True
    is_anonymous = False

    def __init__(self, login, password_hash):
        self.login = login
        self.password_hash = password_hash
        self.created_at = datetime.datetime.now()

    # служебная функция для flask login
    def get_id(self):
        return self.id
    
@manager.user_loader
def load_user(id):
    return db.session.query(User).filter(User.id == id).first()


class Tour(db.Model):
    """! Класс путеводителя"""
    __tablename__ = "tours"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

    # размеры поля для добавления блоков путеводителя
    canvas_height = db.Column(db.Integer, default=8, nullable=False)
    canvas_width = db.Column(db.Integer, default=4, nullable=False)

    last_updated_at = db.Column(db.DateTime, nullable=False)
    archived = db.Column(db.Boolean, default=False, nullable=False)  # for reversible "deletion"

    # отношения
    created_by_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_by = db.relationship("User", back_populates="tours", foreign_keys=[created_by_id])
    moderated_by_id = db.Column(db.Integer, db.ForeignKey("users.id"))  # null if was not moderated
    moderated_by = db.relationship("User", back_populates="moderated_tours", foreign_keys=[moderated_by_id])

    blocks = db.relationship("TourBlock", back_populates="tour", cascade="all, delete")
    reactions = db.relationship("TourReaction", back_populates="tour", cascade="all, delete")
    tags = db.relationship('TourTag', secondary='tours_to_tags_association', lazy='dynamic', backref='tours')

    def __init__(self, created_by_id, name, canvas_height):
        self.name = name
        self.canvas_height = canvas_height
        self.canvas_width = 4
        self.last_updated_at = datetime.datetime.now()
        self.archived = False
        self.created_by_id = created_by_id

## Тип блока: текст
TOUR_BLOCK_TEXT_TYPE = 0
## Тип блока: изображения
TOUR_BLOCK_IMAGE_TYPE = 1
## Тип блока: ссылка
TOUR_BLOCK_LINK_TYPE = 2  
## Тип блока: виедо
TOUR_BLOCK_VIDEO_TYPE = 3
## Тип блока: аудио
TOUR_BLOCK_SOUND_TYPE = 4
## Тип блока: карта
TOUR_BLOCK_MAP_ROUTE_TYPE = 5 
## Тип блока: точка на карте (обычный текст, но будет связан линиями на карте, обозначая маршрут)
TOUR_BLOCK_MAP_POINT_TYPE = 6  


class TourBlock(db.Model):
    """! Класса элемента путеводителя"""
    __tablename__ = "tour_blocks"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    text = db.Column(db.Text)
    content_path = db.Column(db.String(50))  # path to media content
    type = db.Column(db.Integer, nullable=False, default=TOUR_BLOCK_TEXT_TYPE)  # one of TOUR_BLOCK_TYPES shown above

    show_on_map = db.Column(db.Boolean, nullable=False, default=False)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)

    # position & size on canvas
    column = db.Column(db.Integer, nullable=False, default=0)
    row = db.Column(db.Integer, nullable=False, default=0)
    height = db.Column(db.Integer, nullable=False, default=1)
    width = db.Column(db.Integer, nullable=False, default=1)

    # relations
    tour_id = db.Column(db.Integer, db.ForeignKey("tours.id"))
    tour = db.relationship("Tour", back_populates="blocks")

    def __init__(self, name, text, content_path, type_, show_on_map, latitude, longitude, column, row, height, width,
                 tour_id):
        self.name = name
        self.text = text
        self.content_path = content_path
        self.type = type_
        self.show_on_map = show_on_map
        self.latitude = latitude
        self.longitude = longitude
        self.column = column
        self.row = row
        self.height = height
        self.width = width
        self.tour_id = tour_id


class TourTag(db.Model):
    """! Класса категории путеводителя"""
    __tablename__ = "tour_tags"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))

    def __init__(self, name):
        self.name = name

## Ассоциативная таблица, разрешающая отношение "многие ко многим" между путеводителем и категорией
tours_to_tags_association = db.Table(
    'tours_to_tags_association', db.metadata,
    db.Column('tour_id', db.Integer(), db.ForeignKey('tours.id'), primary_key=True),
    db.Column('tag_id', db.Integer(), db.ForeignKey('tour_tags.id'), primary_key=True),
)

## Ассоциативная таблица, разрешающая отношение "многие ко многим" между путеводителем и пользователем, модерировашим его
users_to_tags_association = db.Table(
    'users_to_tags_association', db.metadata,
    db.Column('user_id', db.Integer(), db.ForeignKey('users.id'), primary_key=True),
    db.Column('tag_id', db.Integer(), db.ForeignKey('tour_tags.id'), primary_key=True),
)


class TourReaction(db.Model):
    """! Клас комментария к путеводителю"""
    __tablename__ = "tour_reactions"
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text)

    # criteria (1-10)
    beauty_criteria = db.Column(db.Integer, nullable=True, default=5)
    route_smoothness_criteria = db.Column(db.Integer, nullable=True, default=5)
    attractions_criteria = db.Column(db.Integer, nullable=True, default=5)
    accessibility_criteria = db.Column(db.Integer, nullable=True, default=5)

    overall_criteria = db.Column(db.Integer, nullable=True, default=5)

    # relations
    created_by_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    created_by = db.relationship("User", back_populates="reactions")
    tour_id = db.Column(db.Integer, db.ForeignKey("tours.id"))
    tour = db.relationship("Tour", back_populates="reactions")

    def __init__(self, text, beaty_criteria, route_smoothness_criteria, attractions_criteria, accessibility_criteria,
                 created_by_id, tour_id):
        self.text = text
        self.beauty_criteria = beaty_criteria
        self.route_smoothness_criteria = route_smoothness_criteria
        self.attractions_criteria = attractions_criteria
        self.accessibility_criteria = accessibility_criteria
        self.created_by_id = created_by_id
        self.overall_criteria = int((self.beauty_criteria + self.attractions_criteria + self.accessibility_criteria + self.route_smoothness_criteria)/4)
        self.tour_id = tour_id
