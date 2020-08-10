import os
import calendar

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import date, datetime, time

from helpers import apology, login_required

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///project.db")
db.execute("PRAGMA foreign_keys = ON")


@app.route("/")
def index():

    # Landing Page
    return render_template("landing.html")


@app.route("/admindashboard")
@login_required
def adash():

    # Go to admin dashboard and extract list of classes for today
    cal = (date.today()).strftime("%A %d %B")
    rows = db.execute("SELECT * FROM classes WHERE day = ?", date.today().isoweekday())
    occupied = []
    subject = {}
    time = {}
    row = db.execute("SELECT first,last FROM adminusers WHERE id = ?", session["user_id"])
    name = row[0]["first"] +  " " + row[0]["last"]

    # Configure fields for classroom status
    for x in rows:
        if datetime.now().time() > datetime.strptime(x["start"],'%H:%M').time() and datetime.now().time() < datetime.strptime(x["end"],'%H:%M').time():
            occupied.append(x["classroom"])
            subject[str(x["classroom"])] = str(x["subject"]) + " " + str(x["level"])
            time[str(x["classroom"])] = x["start"] + " to " + x["end"]
    return render_template("adashboard.html", rows=rows, cal=cal, occupied=occupied, subject=subject, time=time, name=name)


@app.route("/register", methods=["GET", "POST"])
@login_required
def register():

    # Registration form for student/tutor
    if request.method == "GET":
        row = db.execute("SELECT first,last FROM adminusers WHERE id = ?", session["user_id"])
        name = row[0]["first"] +  " " + row[0]["last"]
        return render_template("register.html", name=name)

    # Upon submit of form
    else:
        spassword = request.form.get("spassword")
        sconfirmation = request.form.get("confirmation")
        susername = request.form.get("susername")
        sfirst = request.form.get("sfirst")
        slast = request.form.get("slast")
        tfirst = request.form.get("tfirst")
        tlast = request.form.get("tlast")

        # Validations for student registration form
        if request.form['submit'] == 'student':
            rows = db.execute("SELECT username FROM studentusers WHERE username = :username", username=susername)
            if sconfirmation != spassword:
                errormsg = "Passwords do not match!"
            elif not susername or not spassword or not sfirst or not slast:
                errormsg = "Please fill in all fields before submitting form!"
            elif len(rows) != 0:
                errormsg = "Username taken!"
            else:
                db.execute("INSERT INTO studentusers (username, hash, first, last) VALUES (?,?,?,?)", susername, generate_password_hash(spassword), sfirst, slast)
                flash("Student Registered!")
                return redirect("/register")

        # Validations for tutor registration form
        if request.form['submit'] == 'tutor':
            if not tfirst or not tlast:
                errormsg = "Please fill in all fields before submitting form!"
            else:
                db.execute("INSERT INTO tutors (first, last, full) VALUES (?,?,?)", tfirst, tlast, tfirst + " " + tlast)
                flash("Tutor Registered!")
                return redirect("/register")
        flash(errormsg,"error")
        return redirect("/register")


@app.route("/manage", methods=["GET", "POST"])
@login_required
def manage():

    # Goes to Class Management page and extracts lists of classes/students enrolled
    if request.method =="GET":
        row = db.execute("SELECT first,last FROM adminusers WHERE id = ?", session["user_id"])
        name = row[0]["first"] +  " " + row[0]["last"]
        rows = db.execute("SELECT * FROM classes")
        for classes in rows:
            classes["day"] = calendar.day_name[(classes["day"] - 1)]
            classes["classlist"] = db.execute("SELECT * FROM studentusers WHERE id IN (SELECT student_id FROM enrollment WHERE class_id = ?)", classes["id"])
            for y in classes["classlist"]:
                y["id"] = str(y["id"]) + "," + str(classes["id"])
        return render_template("manage.html", rows=rows, name=name)

    # Delete functions for classes/students
    else:
        if "remove" in request.form:
            removed = request.form['remove']
            db.execute("DELETE FROM classes WHERE id = ?", removed)
            db.execute("DELETE FROM enrollment WHERE class_id = ?", removed)
            flash("Class removed!")
        elif "sremove" in request.form:
            studentremove = request.form['sremove'].split(",")
            db.execute("DELETE FROM enrollment WHERE student_id = ? AND class_id = ?", int(studentremove[0]), int(studentremove[1]))
            flash("Student removed!")
        return redirect("/manage")


@app.route("/students", methods=["GET", "POST"])
@login_required
def students():

    # Goes to Student Management Page and extracts list of students and classes enrolled
    if request.method =="GET":
        row = db.execute("SELECT first,last FROM adminusers WHERE id = ?", session["user_id"])
        name = row[0]["first"] +  " " + row[0]["last"]
        rows = db.execute("SELECT * FROM studentusers")
        for student in rows:
            student["classes"] = db.execute("SELECT * FROM classes WHERE id IN (SELECT class_id FROM enrollment WHERE student_id = ?)", student["id"])
            for details in student["classes"]:
                details["day"] = calendar.day_name[(details["day"] - 1)]
                details["id"] = str(details["id"]) + "," + str(student["id"])
        return render_template("students.html", rows=rows, name=name)

    # Delete function for student/classes enrolled
    else:
        if "remove" in request.form:
            studentremove = request.form["remove"]
            db.execute("DELETE FROM studentusers WHERE id = ?", studentremove)
            db.execute("DELETE FROM enrollment WHERE student_id = ?", studentremove)
            flash("Student removed!")
        elif "cremove" in request.form:
            enrollment = request.form["cremove"].split(",")
            db.execute("DELETE FROM enrollment WHERE student_id = ? AND class_id = ?", int(enrollment[1]), int(enrollment[0]))
            flash("Removed from class!")
        return redirect("/students")


@app.route("/addclass",methods=["GET", "POST"])
@login_required
def addclass():

    # Form for creation of new class
    if request.method =="GET":
        row = db.execute("SELECT first,last FROM adminusers WHERE id = ?", session["user_id"])
        name = row[0]["first"] +  " " + row[0]["last"]
        tutor = db.execute("SELECT full FROM tutors")
        return render_template("addclass.html", tutor=tutor, name=name)

    # Upon submit
    else:
        subject = request.form.get("subject")
        level = request.form.get("level")
        classroom = request.form.get("classroom")
        tutor = request.form.get("tutor")
        day = request.form.get("day")
        start = request.form.get("start")
        end = request.form.get("end")

        # Form validations
        if not subject or not level or not classroom or not tutor or not day or not start or not end:
            errormsg = "Please input all fields"
        elif datetime.strptime(end,'%H:%M') <= datetime.strptime(start,'%H:%M'):

            errormsg = "Start time must be earlier than end time!"
        else:
            db.execute("INSERT INTO classes (subject, level, classroom, tutor, day, start, end) VALUES (?,?,?,?,?,?,?)",subject, level, classroom, tutor, day, start, end)
            flash("Class Added!")
            return redirect("/manage")
        flash(errormsg,"error")
        return redirect("/addclass")


@app.route("/studentdashboard", methods=["GET", "POST"])
@login_required
def sdash():

    # Go to student dashboard and loads enrolled classes
    if request.method =="GET":
        cal = (date.today()).strftime("%A %d %B")
        row = db.execute("SELECT first,last FROM studentusers WHERE id = ?", session["user_id"])
        name = row[0]["first"] +  " " + row[0]["last"]
        enrolled = db.execute("SELECT * FROM classes JOIN enrollment ON id = class_id WHERE student_id = ?", session["user_id"])
        for rows in enrolled:
            rows["day"] = calendar.day_name[(rows["day"] - 1)]
        return render_template("sdashboard.html", name=name, cal=cal, enrolled = enrolled)

    # Function for student to unenroll
    else:
        removed = request.form['quit']
        db.execute("DELETE FROM enrollment WHERE class_id = ?", removed)
        flash("Successfully Left!")
        return redirect("/studentdashboard")


@app.route("/enroll", methods=["GET", "POST"])
@login_required
def enroll():

    # Enroll page which loads other classes not enrolled in
    if request.method == "POST":
        new = request.form['enroll']
        db.execute("INSERT INTO enrollment(class_id, student_id) VALUES(?,?)", new, session["user_id"])
        flash("Enrolled!")
        return redirect("/enroll")

    # Function for student to enroll
    else:
        row = db.execute("SELECT first,last FROM studentusers WHERE id = ?", session["user_id"])
        name = row[0]["first"] +  " " + row[0]["last"]
        notenrolled = db.execute("SELECT * FROM classes WHERE id NOT IN (SELECT class_id FROM enrollment WHERE student_id = ?)", session["user_id"])
        for rows in notenrolled:
            rows["day"] = calendar.day_name[(rows["day"] - 1)]
        return render_template("enroll.html", notenrolled=notenrolled, name=name)


@app.route("/admin", methods=["GET", "POST"])
def alogin():
    # Admin log in page

    # Forget any user_id
    session.clear()

    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM adminusers WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/admindashboard")

    else:
        return render_template("alogin.html")


@app.route("/student", methods=["GET", "POST"])
def slogin():
    # Student log in page

    # Forget any user_id
    session.clear()

    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM studentusers WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/studentdashboard")

    else:
        return render_template("slogin.html")


@app.route("/logout")
def logout():
   # Logs user out

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


def errorhandler(e):

    # Handle error
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
