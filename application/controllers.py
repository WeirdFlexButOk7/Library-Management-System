from application.models import *
from flask import session,url_for
from datetime import datetime
import matplotlib.pyplot as plt
plt.switch_backend("agg")

def isLibrarian(username,password):
	for i in getLibrarian().all():
		if(i.username == username and i.password == password):
			return True
	return False

def isUser(username,password):
	for i in getUser().all():
		if(i.username == username and i.password == password):
			return True
	return False

def newUserRegis(username,password1,password2):
	if(password1 != password2):
		return "diff_pass"
	for i in getUser().all():
		if(i.username == username):
			return "same_user"
	
	newUser = User(username = username, password = password1, req_count = 0, books_read = 0)
	add(newUser)

	for book in getEBook():
		user_book_obj = UserEbook(username=username,title=book.title,status="Yet to read",has=0)
		add(user_book_obj)

	commit_changes()
	return "ok"

def getSearchSection(search_text):
	if(search_text == None):
		return getSection().all()
	return getSection().filter(Section.title.ilike(f"%{search_text}%")).all()

def acceptRequest(req_ID):
	req_obj = getRequests().filter_by(ID = req_ID).first()
	title = req_obj.title
	name = req_obj.username
	remove(req_obj)
	user_book_obj = getUserEbook().filter_by(username = name,title=title).first()
	user_book_obj.has = 1
	user_book_obj.date = datetime.today().date()
	user_obj = getUser().filter_by(username = name).first()
	user_obj.req_count -= 1
	commit_changes()

def rejectRequest(req_ID):
	req_obj = getRequests().filter_by(ID = req_ID).first()
	name = req_obj.username
	remove(req_obj)
	user_obj = getUser().filter_by(username = name).first()
	user_obj.req_count -= 1
	commit_changes()

def addBook(title,author,content,section,username):
	books_all = getEBook().all()
	for i in books_all:
		if(i.title == title):
			return False
	new_book_obj = Ebook(title=title,author=author,content=content,section=section,issued_by=username,issue_date=datetime.today().date())
	add(new_book_obj)

	for user in getUser().all():
		user_book_obj = UserEbook(username=user.username,title=title,status="Yet to read",has=0)
		add(user_book_obj)

	commit_changes()
	return True

def editBook(title,author,content,section,ID):
	book_obj = getEBook().filter_by(ID=ID).first()
	user_book_objs = getUserEbook().filter_by(title=book_obj.title).all()
	req_objs = getRequests().filter_by(title=book_obj.title).all()
	for item in [user_book_objs,req_objs]:
		for obj in item:
			obj.title = title

	book_obj.title = title
	book_obj.author = author
	book_obj.content = content
	book_obj.section = section

	commit_changes()
	return True

def getSearchSectionBooks(sec_title,search_text,search_type):
	if(search_text):
		if(search_type == "title"):
			text_filter = getEBook().filter(Ebook.title.ilike(f"%{search_text}%")).all()
		else:
			text_filter = getEBook().filter(Ebook.author.ilike(f"%{search_text}%")).all()
	else:
		text_filter = getEBook().all()

	section_objs = []
	for i in text_filter:
		if(i.section == sec_title):
			section_objs.append(i)
	return section_objs

def getUserBooks(name,text,type):
	books_info = [ [] for i in range(2)]
	for book in getUserEbook().filter_by(username=name,has=1).all():
		books_info[0].append(book.title)
		books_info[1].append(book.status)

	finished,reading,yet_to = [],[],[]
	if(text):
		if(type == "section"):
			filter_books = getEBook().filter(Ebook.section.ilike(f"%{text}%")).all()
		elif(type == "author"):
			filter_books = getEBook().filter(Ebook.author.ilike(f"%{text}%")).all()
		else:
			filter_books = getEBook().filter(Ebook.title.ilike(f"%{text}%")).all()
	else:
		filter_books = getEBook().all()

	for book in filter_books:
		if(book.title in books_info[0]):
			idx = books_info[0].index(book.title)
			if(books_info[1][idx] == "Finished"):
				finished.append(book)
			elif(books_info[1][idx] == "Reading"):
				reading.append(book)
			else:
				yet_to.append(book)
	return finished,reading,yet_to

def getLibStats(name):
    books_issued = getEBook().filter_by(issued_by=name).all()
    total_issues = len(books_issued)
    data = {}
    
    for sec in getSection().all():
        data[sec.title] = 0
	
    for book in books_issued:
        data[book.section] += 1

    data = dict(sorted(data.items()))
    cats = list(data.keys())
    vals = list(data.values())

    plt.figure(figsize=(8, 6))
    plt.bar(cats, vals, color='skyblue')
    plt.title('Books Issued in each Section')
    plt.xlabel('Section')
    plt.ylabel('Number of Books Issued')
    plt.xticks(rotation=45)
    plt.tight_layout()

    pic_name = f"lib_{name}_stats.png"
    path = "static/" + pic_name
    plt.savefig(path)
    plt.close()

    return pic_name, total_issues

def getAllSearchBooks(search_text,search_type):
	if(search_text):
		if(search_type == "title"):
			text_filter = getEBook().filter(Ebook.title.ilike(f"%{search_text}%")).all()
		elif(search_type == "author"):
			text_filter = getEBook().filter(Ebook.author.ilike(f"%{search_text}%")).all()
		else:
			text_filter = getEBook().filter(Ebook.section.ilike(f"%{search_text}%")).all()
	else:
		text_filter = getEBook().all()
	return text_filter

def getBookStats(title,text):
	text_filter = getUserEbook().filter(UserEbook.username.ilike(f"%{text}%")).all()
	ret_objs = []
	for obj in text_filter:
		if(obj.title == title):
			ret_objs.append(obj)
	return ret_objs

def changeUserBook(name,title):
	userBookObj = getUserEbook().filter_by(username=name,title=title).first()
	userBookObj.has = (userBookObj.has ^ 1)
	if(userBookObj.has):
		userBookObj.date = datetime.today().date()
	else:
		userBookObj.date = None
	commit_changes()

def deleteBook(title):
	req_objs = getRequests().filter_by(title=title).all()
	user_book_objs = getUserEbook().filter_by(title=title).all()
	book_objs = getEBook().filter_by(title = title).all()
	
	for obj in book_objs:
		remove(obj)
	for obj in user_book_objs:
		if(obj.status == "Finished"):
			user_obj = getUser().filter_by(username=obj.username).first()
			user_obj.books_read -= 1
		remove(obj)
	for obj in req_objs:
		user_obj = getUser().filter_by(username=obj.username).first()
		user_obj.req_count -= 1
		remove(obj)

	commit_changes()
	return True

def addSection(name,desc):
	for i in getSection().all():
		if(i.title == name):
			return False
	newSection = Section(title=name,description=desc,date=datetime.today().date())
	add(newSection)
	commit_changes()
	return True

def deleteSection(sec_name):
	if(sec_name == "Uncategorised"):
		return False
	book_objs = getEBook().filter_by(section=sec_name).all()
	for book in book_objs:
		book.section = "Uncategorised"
	sec_obj = getSection().filter_by(title = sec_name).first()
	remove(sec_obj)
	commit_changes()
	return True

def editSection(sec_name,desc,ID):
	sec = getSection().filter_by(ID=ID).first()
	old_title = sec.title
	if(sec.title != "Uncategorised"):
		sec.title = sec_name
	elif(sec_name != sec.title):
		return False
	sec.description = desc

	book_objs = getEBook().filter_by(section = old_title).all()
	for obj in book_objs:
		obj.section = sec_name
	commit_changes()
	return True

def getUserFilterBooks(name,text,filter):
	books_not_owned = [obj.title for obj in getUserEbook().filter_by(has = 0,username=name).all()]
	if(text):
		if(filter == "section"):
			objs_filter = getEBook().filter(Ebook.section.ilike(f"%{text}%")).all()
		elif(filter == "author"):
			objs_filter = getEBook().filter(Ebook.author.ilike(f"%{text}%")).all()
		else:
			objs_filter = getEBook().filter(Ebook.title.ilike(f"%{text}%")).all()
	else:
		objs_filter = getEBook().all()
	
	book_objs = []
	for obj in objs_filter:
		if(obj.title in books_not_owned):
			book_objs.append(obj)

	reqs = [obj.title for obj in getRequests().filter_by(username=name)]
	return book_objs,reqs

def modifyRequest(name,title):
	user_obj = getUser().filter_by(username=name).first()
	if(user_obj.req_count == 5): #max books a user can request = 5.
		return False
	for req in getRequests().all():
		if(req.username == name and req.title == title):
			remove(req)
			user_obj.req_count -= 1
			commit_changes()
			return
		
	req_obj = Request(username=name,title=title,date=datetime.today().date())
	add(req_obj)
	user_obj.req_count += 1
	commit_changes()
	return True

def bookStarted(name,title):
	user_book_obj = getUserEbook().filter_by(username=name,title=title).first()
	user_book_obj.status = "Reading"
	commit_changes()
	book_obj = getEBook().filter_by(title = title).first()
	return book_obj.content

def bookFinish(name,title):
	user_book_obj = getUserEbook().filter_by(username=name,title=title).first()
	user_book_obj.status = "Finished"
	user_obj = getUser().filter_by(username=name).first()
	user_obj.books_read += 1
	commit_changes()

def bookReturn(name,title):
	user_book_obj = getUserEbook().filter_by(username=name,title=title).first()
	user_book_obj.has = 0
	user_book_obj.date = None
	commit_changes()

def getUserStats(name):
    books_read = [obj.title for obj in getUserEbook().filter_by(username=name, status="Finished").all()]
    total_read = len(books_read)
    data = {}
    
    for sec in getSection().all():
        data[sec.title] = 0
	    
    for title in books_read:
        book = getEBook().filter_by(title=title).first()
        data[book.section] += 1
	
    data = dict(sorted(data.items()))
    cats = list(data.keys())
    vals = list(data.values())
    plt.figure(figsize=(8, 6))
    plt.bar(cats, vals, color='skyblue')
    plt.title('Books read in each Section')
    plt.xlabel('Section')
    plt.ylabel('Number of Books read')
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    pic_name = f"user_{name}_stats.png"
    path = "static/" + pic_name
    plt.savefig(path)
    plt.close()
    
    return pic_name, total_read

def storeFeedback(name,title,feedback):
	user_book_obj = getUserEbook().filter_by(username=name,title=title).first()
	user_book_obj.feedback = feedback
	commit_changes()

def max_days_book_check():
	user_book = getUserEbook().all()
	today_date = datetime.today().date()
	date_format = "%Y-%m-%d"
	for obj in user_book:
		if(obj.has == 0):
			continue
		user_date = datetime.strptime(obj.date, date_format).date()
		days_had = today_date - user_date
		if(days_had.days > 7): #Max days a user can have a book is 7 days.
			obj.has =0
			obj.date = None
	
	commit_changes()
