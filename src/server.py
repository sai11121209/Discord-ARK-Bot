from flask import Flask, request, jsonify, make_response
from threading import Thread
from mcrcon import MCRcon
import subprocess
import winrm
import os
import time

app = Flask("")

try:
    from local_settings import *
except ImportError:
    if os.getenv("IPADDRESS"):
        USER_AGENT = os.getenv("USER_AGENT")
        CONTENT_TYPE = os.getenv("CONTENT_TYPE")
        IPADDRESS = os.getenv("IPADDRESS")
        MACADDRESS = os.getenv("MACADDRESS")
        USER = os.getenv("USER")
        PASSWORD = os.getenv("PASSWORD")
        RCONPORT = os.getenv("RCONPORT")


@app.route("/")
def main():
    return "Bot is aLive!"


@app.route("/commands/wake_on_lan")
def WakeOnLan():
    if not request.headers.get("User-Agent") == USER_AGENT:
        error_message = {"state": 0, "error": "Invalid User-Agent."}
        return make_response(jsonify(error_message), 400)
    if not request.headers.get("Content-Type") == CONTENT_TYPE:
        error_message = {"state": 0, "error": "Invalid Content-Type."}
        return make_response(jsonify(error_message), 400)
    try:
        res = subprocess.call(
            f"/home/pi/tools/wol {IPADDRESS} {MACADDRESS}", shell=True
        )
        success_message = {"state": 1, "body": "The request was executed successfully."}
    except:
        success_message = {
            "state": 0,
            "body": "The request was processed successfully, but the startup process was not executed properly.",
        }
    return make_response(jsonify(success_message), 200)


@app.route("/commands/shutdown")
def Shutdown():
    if not request.headers.get("User-Agent") == USER_AGENT:
        error_message = {"state": 0, "error": "Invalid User-Agent."}
        return make_response(jsonify(error_message), 400)
    if not request.headers.get("Content-Type") == CONTENT_TYPE:
        error_message = {"state": 0, "error": "Invalid Content-Type."}
        return make_response(jsonify(error_message), 400)
    try:
        mcr = MCRcon(IPADDRESS, PASSWORD, RCONPORT)
        mcr.connect()
        resp = mcr.command("saveworld")
        mcr.command(
            "Broadcast The world has been saved. The server will be shutdown in 1 minute."
        )
        time.sleep(60)
        resp = mcr.command("saveworld")
        mcr.command("Broadcast Stop the server.")
        mcr.command("DoExit")
        print(resp)
        mcr.disconnect()
    except:
        pass
    session = winrm.Session(IPADDRESS, auth=(USER, PASSWORD))
    try:
        session.run_ps("shutdown -s -f -t 120")
        success_message = {"state": 1, "body": "The request was executed successfully."}
    except:
        success_message = {
            "state": 0,
            "body": "The request was processed successfully, but the shutdown process was not executed properly.",
        }
    return make_response(jsonify(success_message), 200)


def run():
    app.run(host="0.0.0.0", port=80)


def keep_alive():
    server = Thread(target=run)
    server.start()


if __name__ == "__main__":
    keep_alive()
