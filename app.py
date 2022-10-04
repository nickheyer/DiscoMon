from flask import Flask, render_template, request, jsonify

from subprocess import Popen
from datetime import date
from collections import OrderedDict
import atexit
import signal
import json
import os, sys
import requests
from sys import platform


app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Subprocesses List
bot_proc = None


def start_bot():
    global bot_proc
    op_call = None
    if platform in ["linux", "linux2", "darwin"]:
        op_call = "python3"
    elif platform == "win32":
        op_call = "python.exe"
    args = [op_call, f"bot.py"]
    err_log = open(
        os.path.join(
            os.path.dirname(__file__),
            "logs",
            "bot",
            f'BOT_{date.today().strftime("%d_%m_%Y")}.log',
        ),
        "a",
    )
    bot_proc = Popen(args, stderr=err_log, start_new_session=True)
    set_values("statemachine", "botState", True)


def kill_bot():
    global bot_proc
    set_values("statemachine", "botState", False)
    try:
        bot_proc.kill()
        bot_proc.wait()
        bot_proc.close()
    except:
        pass


def get_data(file_name):
    with open(
        os.path.join(os.path.dirname(__file__), "data", f"{file_name}.json"), "r"
    ) as fp:
        return json.load(fp)


def set_values(file_name, key, newval):
    values = get_data(file_name)
    values[key] = newval
    with open(
        os.path.join(os.path.dirname(__file__), "data", f"{file_name}.json"), "w"
    ) as fpw:
        json.dump(values, fpw)


def set_file(file_name, json_data):
    with open(
        os.path.join(os.path.dirname(__file__), "data", f"{file_name}.json"), "w"
    ) as fpw:
        json.dump(json_data, fpw)


def set_status(status):
    set_file("activity", status)
    send_request()


def restart_bot():
    kill_bot()
    start_bot()


def parse_request():
    pass


def send_request():

    req_file = get_data("request")

    url = req_file["url"]

    payload = get_data("activity")

    headers = req_file["headers"]

    response = requests.request("POST", url, headers=headers, json=payload)

    return response.text


#Function called on exit, similar to shutdown
@atexit.register
def exit_shutdown():
    kill_bot()

# Beginning Routes with default index temp func
@app.route("/")
def index():
    data_list = [get_data("statemachine"), get_data("values"), get_data("request")]
    return render_template(
        "/index.html",
        data_list=data_list,
        state=data_list[0],
        values=data_list[1],
        request=data_list[2],
    )


@app.route("/stat", methods=["POST"])
def get_status():
    return get_data("activity")


@app.route("/save", methods=["POST"])
def save_credentials():
    req = request.get_json()
    file_name = req["file"]
    json_data = req["data"]
    prev = get_data(file_name)
    dif = list()
    for x in prev:
        if prev[x] != json_data[x]:
            dif.append(x)
    set_file(file_name, json_data)
    restart_bot()
    return "Restarted"


@app.route("/data", methods=["POST"])
def return_data():
    return get_data(request.get_json()["document"])


@app.route("/on", methods=["POST"])
def turn_bot_on():
    current_state = get_data("statemachine")
    current_values = get_data("values")
    if current_state["botState"]:
        msg = f"Bot Is Already On"
        return msg
    for x, y in current_values.items():
        if x == "internalReference" or (
            "Token" in x
        ):  # Keys in values.json that the bot can start without
            pass
        elif y == None or y == "":
            msg = "Missing Values"
            return msg
    try:
        start_bot()
    except:
        kill_bot()
    msg = f"Turning Bot On"
    return msg


@app.route("/off", methods=["POST"])
def turn_bot_off():
    if get_data("statemachine")[f"botState"] == False:
        msg = "Bot is already off"
        return msg
    kill_bot()
    msg = f"Turning Bot Off"
    return msg


@app.route("/shutdown", methods=["POST"])
def shutdown():
    kill_bot()
    if sys.platform in ["linux", "linux2"]:
        os.system("pkill -f gunicorn")
    elif sys.platform == "win32":
        sig = getattr(signal, "SIGKILL", signal.SIGTERM)
        os.kill(os.getpid(), sig)
    try:
        shutdown_func = request.environ.get("werkzeug.server.shutdown")
        shutdown_func()
    except:
        pass
    sys.exit()


# Running App Loop
if __name__ == "__main__":
    app.run(debug=False)
