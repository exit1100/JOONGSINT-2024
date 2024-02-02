from flask import Blueprint, render_template, request

my_calc_module = Blueprint("my_calc_module", __name__)

@my_calc_module.route("/result", methods=["POST"])
def result():
    num1 = float(request.form["num1"])
    num2 = float(request.form["num2"])
    operation = request.form["operation"]
    if operation == "add":
        result = num1 + num2
        
    elif operation == "subtract":
        result = num1 - num2

    elif operation == "multiply":
        result = num1 * num2
    elif operation == "divide":
        result = num1 / num2
    return render_template("result.html", result=result)