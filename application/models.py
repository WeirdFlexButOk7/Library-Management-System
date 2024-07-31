from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
	__tablename__ = 'user'
	ID = db.Column(db.Integer, primary_key=True, autoincrement = True)
	username = db.Column(db.String, unique = True, nullable = False)
	password = db.Column(db.String, nullable = False)
	req_count = db.Column(db.Integer, nullable = False)
	books_read = db.Column(db.Integer, nullable = False)

class Librarian(db.Model):
	__tablename__ = 'librarian'
	ID = db.Column(db.Integer, primary_key=True, autoincrement = True)
	username = db.Column(db.String, unique = True, nullable = False)
	password = db.Column(db.String, nullable = False)

class Section(db.Model):
	__tablename__ = 'section'
	ID = db.Column(db.Integer, primary_key=True, autoincrement = True)
	title = db.Column(db.String, nullable = False, unique = True)
	date = db.Column(db.String, nullable = False)
	description = db.Column(db.String, nullable = False)

class Ebook(db.Model):
	__tablename__ = 'ebook'
	ID = db.Column(db.Integer, primary_key=True, autoincrement = True)
	title = db.Column(db.String, nullable = False, unique = True)
	author = db.Column(db.String, nullable = False)
	content = db.Column(db.String, nullable = False)
	section = db.Column(db.String, db.ForeignKey(Section.title),nullable = False)
	issued_by = db.Column(db.String, db.ForeignKey(Librarian.username), nullable = False)
	issue_date = db.Column(db.String, nullable = False)

class Request(db.Model):
	__tablename__ = 'request'
	ID = db.Column(db.Integer, primary_key=True, autoincrement = True)
	username = db.Column(db.String, db.ForeignKey(User.username), nullable = False)
	title = db.Column(db.String, db.ForeignKey(Ebook.title), nullable = False)
	date = db.Column(db.String, nullable = False)

class UserEbook(db.Model):
	__tablename__ = 'user_ebook'
	ID = db.Column(db.Integer, primary_key=True, autoincrement = True)
	username = db.Column(db.String, db.ForeignKey(User.username), nullable = False)
	title = db.Column(db.String, db.ForeignKey(Ebook.title),nullable = False)
	status = db.Column(db.String, nullable = False) # "Yet to read", "Finished", "Reading"
	has = db.Column(db.Integer,nullable=False)
	date = db.Column(db.String)
	feedback = db.Column(db.String)

def getUser():
	return User.query

def getLibrarian():
	return Librarian.query

def getEBook():
	return Ebook.query

def getSection():
	return Section.query

def getRequests():
	return Request.query

def getUserEbook():
	return UserEbook.query

def add(qu):
	db.session.add(qu)

def remove(qu):
	db.session.delete(qu)

def commit_changes():
	db.session.commit()
