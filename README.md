<h1 align="center">
<img src="largelogo.png" width="200" height="40">
</h1>

<h6 align="center">
Brought to you by: barbequedveggies
</h6>

# What is Edministrator?

Edministrator is an MVP(Minimum Viable Product) of a web application for education/tuition centres to better manage student, class, tutor and classroom data. This platform was developed as part of the
Final Project submission for CS50x Introduction to Computer Science 2020.

To get an overview and demo of the platform, you can visit this [link](https://youtu.be/QApYQU7mK64)

Current Programming Experience: ~ 4 weeks

# Motivation

I come from Singapore where tuition centres are very prevalent. These are typically small businesses which employ a few tutors and have anywhere between 20 to a few hundred students. However,
a large number of these centres continue to use pen/paper or Microsoft Excel to manage their day to day operations. As such, this project was developed in hope to digitalise the entire
management process and allow the backend staff to focus on more value-added work like expanding the business or marketing rather than allocating a large amount of time to handle these administrative affairs.

# Code Framework

This project is built on the model-view-controller framework.<br />
View: Configured using CSS, HTML and Jinja integration<br />
Controller: Configured using Python's flask module<br />
Model: Data is stored in a SQLite 3 database

# Available Functions

## Student Portal

**Student Dashbaord**
* View the classes currently enrolled in together with their relevant details which include timing, location and tutor
* Unenroll from current classes

**Enroll Function**
* View the list of available classes and enroll in them, if desired

## Admin Portal

**Management Dashboard**
* A management dashboard which displays the list of classes scheduled for today with their relevant details which include timing, location and tutor
* Displays the occupation status of each classroom

**Registration Function**
* Register new students and tutors

**Class Management Tool**
* View the list of classes currently available toegther with their relevant details which include timing, location, tutor and students enrolled
* Create and remove classes
* Remove specific students from a particular class

**Student Management Tool**
* View the list of registered students and the classes they are currently enrolled in
* Remove students
* Remove students from a specific class

# Usage

**Admin Account Details**
* Username:admin
* Password:1234567890Qa

**Student Account Details**
* Username:mickeymouse
* Password:1234567890Qa

Note: All the currrent users in the database are using the same password as well



