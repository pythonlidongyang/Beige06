from flask import Flask, request
from robot_service.service.dispatch.robot import robot, RobotActionService

app = Flask(__name__)


@app.route('/dispatch', methods=['POST'])
def dispatch():  # put application's code here
    params = request.get_json()
    # print(params)
    robot(device_name=params.get("deviceName"),
          from_dev=params.get("fromDev"),
          from_pos_para1=params.get("fromPosPara1"),
          from_pos_para2=params.get("fromPosPara2"),
          # to_dev=params.get("toDev"),
          # to_pos_para1=params.get("toPosPara1"),
          # to_pos_para2=params.get("toPosPara2"),
          )
    return 'ok'


@app.route('/save_param', methods=['POST'])
def save_param():  # put application's code here
    params = request.get_json()
    robot_num = params["robot_num"]
    device = params["device"]
    get_put = params["get_put"]
    grab_pos = params["grab_pos"]
    num_pos = params["num_pos"]
    RobotActionService.save_params(robot_num, device, get_put, grab_pos, num_pos)
    return 'ok'


@app.route('/start_singe_step', methods=['GET'])
def start_singe_step():  # put application's code here
    RobotActionService.start_singe_step()
    return 'ok'


@app.route('/clamp_action', methods=['POST'])
def clamp_action():  # put application's code here
    param = request.get_json()
    RobotActionService.clamp_action(param["status"])
    return 'ok'


@app.route('/back_origin', methods=['GET'])
def back_origin():  # put application's code here
    RobotActionService.back_origin()
    return 'ok'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6688, debug=True)
