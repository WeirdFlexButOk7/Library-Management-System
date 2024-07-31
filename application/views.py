from application.controllers import *
from flask import current_app as app, render_template, request, redirect, url_for, session

@app.route("/", methods=["GET", "POST"])
def dashboard():
    return render_template("homepage.html")

@app.route("/lib/login", methods=["GET", "POST"])
def lib_login():
    if request.method == "GET":
        return render_template("librarian_login.html")

    username = request.form.get("username")
    password = request.form.get("password")
    if isLibrarian(username, password):
        session["librarian_username"] = username
        return redirect(url_for("lib_stats",username = username))
    return render_template("message.html",m1 ="Error logging in",m2 ="Invalid username or password",m3="/lib/login",m4="Try again")

@app.route("/user/login", methods=["GET", "POST"])
def user_login():
    if request.method == "GET":
        return render_template("user_login.html")

    username = request.form.get("username")
    password = request.form.get("password")
    if isUser(username, password):
        session["user_username"] = username
        return redirect(url_for("user_stats",username = username))
    return render_template("message.html",m1 ="Error logging in",m2 ="Invalid username or password",m3="/user/login",m4="Try again")

@app.route("/user/register",methods = ["GET","POST"])
def user_register():
    if request.method == "GET":
        return render_template("user_register.html")

    username = request.form.get("username")
    password1 = request.form.get("password1")
    password2 = request.form.get("password2")
    
    result = newUserRegis(username,password1,password2)
    regis_link = "/user/register"
    log_link = "/user/login"

    if result == "ok":
        return render_template("message.html",m1 ="Successful registration",m2 ="User "+ username + " registered",m3=log_link,m4="Go back")
    elif result == "same_user":
        return render_template("message.html",m1 ="Error registering",m2 = "Username " + username + " already chosen",m3=regis_link,m4="Try again")
    elif result == "diff_pass":
        return render_template("message.html",m1 ="Error registering",m2 = "Different passwords entered",m3=regis_link,m4="Try again")

@app.route("/logout")
def logout():
    if "librarian_username" in session:
        session.pop("librarian_username")
        return redirect(url_for("lib_login"))

    if "user_username" in session:
        session.pop("user_username")
        return redirect(url_for("user_login"))
    
    return redirect(url_for("dashboard"))

##########################################

@app.route("/lib/<username>/stats", methods = ["GET"])
def lib_stats(username):
    if "librarian_username" in session:
        username = session["librarian_username"]
        file,total_issues = getLibStats(username)
        return render_template("lib_stats.html",name=username,file=file,total=total_issues)
    return redirect(url_for("lib_login"))

@app.route("/lib/<username>/add_section", methods = ["GET","POST"])
def lib_action_section(username):
    if request.method == "GET":
        ID = request.args.get("ID")
        section = request.args.get("section")
        desc = request.args.get("desc")
        print(ID,section,desc)
        return render_template("libAddSection.html",name=username,section=section,description=desc,ID=ID)
    
    section_name = request.form.get("section_name")
    desc = request.form.get("description")
    ID = request.args.get("ID")

    url = f"/lib/{username}/add_section?ID={ID}&section={section_name}&desc={desc}"
    if(ID == "None"):
        if(addSection(section_name,desc)):
            url = f"/lib/{username}/add_section"
            return render_template("message.html",m1="Section successfully created.",m2="",m3=url,m4="Go back")
        return render_template("message.html",m1="Error occured",m2="Section could not be added",m3=url,m4="Try again")
    else:
        if(editSection(section_name,desc,ID)):
            url = url_for("lib_show_all_section",username=username)
            return render_template("message.html",m1="Section successfully edited.",m2="",m3=url,m4="Go back")
        return render_template("message.html",m1="Failed to edit",m2="Section was not changed",m3=url,m4="Try again")

@app.route("/lib/<username>/sections", methods = ["GET"])
def lib_show_all_section(username):
    search_text = request.args.get("search_text")
    sections = getSearchSection(search_text)
    return render_template("libSections.html", name=username,sections = sections,txt=(search_text if search_text else ''))

@app.route("/lib/<username>/requests", methods = ["GET","POST"])
def lib_requests(username):
    if request.method == "GET":
        return render_template("requests.html",name=username,requests=getRequests().all())

@app.route("/lib/<username>/requests/<ID>/<type>", methods = ["GET","POST"])
def lib_request_modify(username,ID,type):
    if(type == "accept"):
        acceptRequest(ID)
    else:
        rejectRequest(ID)
    return redirect(url_for("lib_requests",username=username))

@app.route("/lib/<username>/books", methods=["GET","POST"])
def lib_books(username):
    if request.method == "GET":
        search_text = request.args.get("search_text")
        search_type = request.args.get("search_type")
        books = getAllSearchBooks(search_text,search_type)
        return render_template("lib_books.html",name=username,books=books,txt=(search_text if search_text else ''),search_type=search_type)

@app.route("/lib/<username>/issue_book", methods = ["GET","POST"])
def lib_issue_book(username):
    issue_book_url = f"/lib/{username}/issue_book"
    if request.method == "GET":
        return render_template("lib_issue_book.html",name=username,sections=getSection().all(),title='')
    
    title = request.form.get("title")
    author = request.form.get("author")
    content = request.form.get("content")
    section = request.form.get("section")
    print(title,author,content,section)
    if(addBook(title,author,content,section,username)):
        return render_template("message.html",m1="Book successfully added.",m2="",m3=issue_book_url,m4="Go back")
    return render_template("message.html",m1="Error adding book.",m2="You either entered invalid inputs or book already exists",m3=issue_book_url,m4="Try again")

@app.route("/lib/<username>/section/<section_title>", methods = ["GET"])
def lib_show_single_section(username,section_title):
    search_text = request.args.get("search_text")
    search_type = request.args.get("search_type")
    books_sec = getSearchSectionBooks(section_title,search_text,search_type)
    return render_template("lib_one_section.html",name=username,books=books_sec,title=section_title,txt=(search_text if search_text else ''),search_type=search_type)

@app.route("/lib/<username>/book/<title>", methods=["GET", "POST"])
def lib_edit_book(username, title):
    if request.method == "GET":
        author = request.args.get("author")
        section = request.args.get("section")
        content = request.args.get("content")
        ID = request.args.get("ID")
        return render_template("lib_issue_book.html", name=username, sections=getSection().all(), title=title, author=author, content=content, _section=section, ID=ID)

    title = request.form.get("title")
    author = request.form.get("author")
    section = request.form.get("section")
    content = request.form.get("content")
    ID = request.args.get("ID")
    if(editBook(title,author,content,section,ID)):
        url = url_for("lib_books",username=username)
        return render_template("message.html",m1="Book successfully modified.",m2="",m3=url,m4="Go back")
    url = url_for("lib_edit_book",username=username,title=title)
    return render_template("message.html",m1="Error modifying book",m2="Invalid inputs",m3=url,m4="Try again")

@app.route("/lib/<username>/book/<title>/stats", methods=["GET","POST"])
def lib_book_stats(username,title):
    max_days_book_check()
    if request.method == "POST":
        name = request.form.get('username')
        changeUserBook(name,title)

    search_text = request.args.get("search_text")
    users = getBookStats(title,search_text)

    return render_template("lib_book_stats.html",name=username,title=title,stats=users,txt=(search_text if search_text else ''))

@app.route("/lib/<username>/book/<title>/delete", methods=["GET"])
def book_delete(username,title):
    url = url_for('lib_books',username=username)
    m4="Go Back"
    if(deleteBook(title)):
        return render_template("message.html",m1="Book removed successfully",m2='',m3=url,m4=m4)
    return render_template("message.html",m1="Error occured",m2="Book was not removed",m3=url,m4=m4)

@app.route("/lib/<username>/section/<sec_name>/delete", methods=["GET"])
def section_delete(username,sec_name):
    url = url_for('lib_show_all_section',username=username)
    if(deleteSection(sec_name)):
        return render_template("message.html",m1="Section deleted successfully",m2='',m3=url,m4="Go back")
    return render_template("message.html",m1="Error occured",m2="Section was not deleted",m3=url,m4="Go back")


##########################################


@app.route("/user/<username>/stats",methods=["GET"])
def user_stats(username):
    if "user_username" in session:
        username = session["user_username"]
        file,total_read = getUserStats(username)
        return render_template("user_stats.html",name=username,file=file,total=total_read)
    return redirect(url_for("user_login"))

@app.route("/user/<username>/my_books",methods=["GET","POST"])
def user_my_books(username):
    max_days_book_check()
    if request.method == "GET":
        search_text = request.args.get("search_text")
        search_type = request.args.get("search_type")
        finished,reading,yet_to = getUserBooks(username,search_text,search_type)
        return render_template("user_my_books.html",name=username,read=finished,reading=reading,yet_to=yet_to,txt=(search_text if search_text else ''),search_type=search_type)

@app.route("/user/<username>/books",methods=["GET","POST"])
def user_books(username):
    max_days_book_check()
    if request.method == "GET":
        search_text = request.args.get("search_text")
        search_type = request.args.get("search_type")
        books,req_list = getUserFilterBooks(username,search_text,search_type)
        return render_template("user_books.html",name=username,books=books,txt=(search_text if search_text else ''),search_type=search_type,reqs=req_list)

@app.route("/user/<username>/books/<title>/req",methods=["GET","POST"])
def user_book_request(username,title):
    modifyRequest(username,title)
    return redirect(url_for('user_books',username=username))

@app.route("/user/<username>/book/<title>/feedback",methods=["GET","POST"])
def user_book_feedback(username,title):
    if request.method == "GET":
        return render_template("user_feedback.html",name=username,title=title)
    
    feedback = request.form.get("feedback")
    storeFeedback(username,title,feedback)
    return render_template("message.html",m1="Feedback submitted successfully",m2='',m3=url_for("user_my_books",username=username),m4="Go back")

@app.route("/user/<username>/book/<title>/<type>",methods=["GET","POST"])
def user_book_interact(username,title,type):
    if(type == "start"):
        url = bookStarted(username,title)
        return render_template("display_book.html",url=url)
    elif(type == "finish"):
        bookFinish(username,title) 
        url = url_for("user_book_feedback",username=username,title=title)
        return render_template("message.html",m1="You finished reading a book!",m2="Submit a feedback!",m3=url,m4="Write feedback")
    else:
        bookReturn(username,title)
        return redirect(url_for('user_my_books',username=username))
