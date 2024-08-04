from flask_sqlalchemy import SQLAlchemy
from flask_alembic import Alembic

db = SQLAlchemy()
alembic_ = Alembic()


class Buyer(db.Model):
    id = db.Column(db.Integer, primary_key=True, index=True)
    name = db.Column(db.String(length=30))
    password = db.Column(db.String(length=30))
    balance = db.Column(db.Float(decimal_return_scale=2), default=0)
    age = db.Column(db.SmallInteger())
    buyers_game = db.relationship('Game', secondary='buyer_game', back_populates='games_buyer')

    def __str__(self):
        return self.name


class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True, index=True)
    title = db.Column(db.String(length=30))
    cost = db.Column(db.Float(decimal_return_scale=2), default=0)
    size = db.Column(db.Float(decimal_return_scale=2))
    description = db.Column(db.String())
    age_limited = db.Column(db.Boolean(), default=False)
    games_buyer = db.relationship('Buyer', secondary='buyer_game', back_populates='buyers_game')

    def __str__(self):
        return self.title+'\t|\t'+str(self.cost)


class BuyerGame(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    buyer_id = db.Column(db.Integer, db.ForeignKey('buyer.id'))
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))

