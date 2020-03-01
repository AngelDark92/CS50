import cs50
import csv
import os

from flask import Flask, jsonify, redirect, render_template, request

# Configure application
app = Flask(__name__)

# Reload templates when they are changed
app.config["TEMPLATES_AUTO_RELOAD"] = True


@app.after_request
def after_request(response):
    """Disable caching"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/", methods=["GET"])
def get_index():
    return redirect("/form")


@app.route("/form", methods=["GET"])
def get_form():
    return render_template("form.html")


@app.route("/form", methods=["POST"])
def post_form():
    # Making sure that all the forms are completed if bootstrap and javascript fail
    if not request.form.get("name") or not request.form.get("surname") or not request.form.get("favourite"):
        return render_template("error.html", message="You must provide all fields")
    # Opening the csv file to write
    file = open("survey.csv", "a", newline="")
    fieldnames = ["name", "surname", "favourite", "sex"]
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    # initialises the .csv file if it's empty or /sheet will not find the keys when reading.
    if os.stat("survey.csv").st_size == 0:
        writer.writerow({"name": "name", "surname": "surname", "favourite": "favourite", "sex": "sex"})
    if not request.form.get("check_privacy"):
        writer.writerow({"name": "Non Disclosed Name...", "surname": "...or surname",
                         "favourite": request.form.get("favourite"), "sex": request.form.get("sex")})
    else:
        writer.writerow({"name": request.form.get("name"), "surname": request.form.get("surname"),
                         "favourite": request.form.get("favourite"), "sex": request.form.get("sex")})
    file.close()
    # redirect goes to the app.route called as per flask
    return redirect("/sheet")


@app.route("/sheet", methods=["GET"])
def get_sheet():
    with open("survey.csv", "r") as file:
        # transform the read file to a list that can be displayed
        reader = csv.DictReader(file)
        lista = list(reader)
    return render_template("sheet.html", lista=lista)