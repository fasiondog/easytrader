import functools

from flask import Flask, jsonify, request

from . import api
from .log import logger

app = Flask(__name__)

global_store = {}


def error_handle(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        # pylint: disable=broad-except
        except Exception as e:
            logger.exception("server error")
            message = "{}: {}".format(e.__class__, e)
            return jsonify({"error": message}), 400

    return wrapper


@app.before_request
def restrict_ip():
    allowed_ips = ['127.0.0.1', '192.168.0.0'] # 允许访问的 IP 列表
    if request.remote_addr not in allowed_ips:
        return 'You are not allowed to access this page', 403


@app.route("/prepare", methods=["POST"])
@error_handle
def post_prepare():
    json_data = request.get_json(force=True)

    user = api.use(json_data.pop("broker"))
    user.prepare(**json_data)

    global_store["user"] = user
    return jsonify({"msg": "login success"}), 201


@app.route("/balance", methods=["GET"])
@error_handle
def get_balance():
    user = global_store["user"]
    balance = user.balance

    return jsonify(balance), 200


@app.route("/position", methods=["GET"])
@error_handle
def get_position():
    user = global_store["user"]
    position = user.position

    return jsonify(position), 200


@app.route("/auto_ipo", methods=["GET"])
@error_handle
def get_auto_ipo():
    user = global_store["user"]
    res = user.auto_ipo()

    return jsonify(res), 200


@app.route("/today_entrusts", methods=["GET"])
@error_handle
def get_today_entrusts():
    user = global_store["user"]
    today_entrusts = user.today_entrusts

    return jsonify(today_entrusts), 200


@app.route("/today_trades", methods=["GET"])
@error_handle
def get_today_trades():
    user = global_store["user"]
    today_trades = user.today_trades

    return jsonify(today_trades), 200


@app.route("/cancel_entrusts", methods=["GET"])
@error_handle
def get_cancel_entrusts():
    user = global_store["user"]
    cancel_entrusts = user.cancel_entrusts

    return jsonify(cancel_entrusts), 200


@app.route("/buy", methods=["POST"])
@error_handle
def post_buy():
    json_data = request.get_json(force=True)
    user = global_store["user"]
    res = user.buy(**json_data)

    return jsonify(res), 201


@app.route("/sell", methods=["POST"])
@error_handle
def post_sell():
    json_data = request.get_json(force=True)

    user = global_store["user"]
    res = user.sell(**json_data)

    return jsonify(res), 201


@app.route("/cancel_entrust", methods=["POST"])
@error_handle
def post_cancel_entrust():
    json_data = request.get_json(force=True)

    user = global_store["user"]
    res = user.cancel_entrust(**json_data)

    return jsonify(res), 201


@app.route("/exit", methods=["GET"])
@error_handle
def get_exit():
    user = global_store["user"]
    user.exit()

    return jsonify({"msg": "exit success"}), 200


def run(port=1430):
    app.run(port=port)
