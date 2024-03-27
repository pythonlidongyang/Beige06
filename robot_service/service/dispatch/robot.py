import json
import time

from robot_service.service.init.init_robot import init_robot


def choice_device(device):
    """设备号,第二个位置为反馈位"""
    match device:
        case "xrPs_01" | "xrPs_02" | "xrPs_03":
            return 1040, 528
        case "xrPump" | "xr96Ls_01" | "xr96Ls_02":
            return 1041, 529
        case "xrTier" | "xrIncubator_01" | "xrIncubator_04":
            return 1042, 530
        case "tcEvo" | "xrIncubator_02" | "xrIncubator_05":
            return 1043, 531
        case "Z02" | "xrIncubator_03" | "xrIncubator_06":
            return 1044, 532
        case "Z03" | "xrPs_Pipette01" | "xrPs_Pipette02":
            return 1045, 533
        case "xrPs_FromZ01":
            return 1046, 534


def choice_grab_pos(grab_pos):
    """抓取位置"""
    match grab_pos:
        case "body":
            return 1064, 552
        case "cover":
            return 1065, 553


def choice_num_pos(num_pos):
    """位置编号"""
    match num_pos:
        case 1:
            return 1070, 558
        case _:
            return 1070 + int(num_pos) - 1, 558 + int(num_pos) - 1


def choice_get_put(get_put):
    """动作类型"""
    match get_put:
        case "get":
            return 1060, 548
        case "put":
            return 1061, 549


def load_config():
    with open("robot_service/config/robot_communication_point.json", encoding='utf-8') as f:
        point_config = json.load(f)
    return point_config


# {
#     "deviceName": "Robot02",
#     "fromDev": "xrPs_03",
#     "fromPosPara1": "2",
#     "fromPosPara2": "body",
#     "toDev": "xr96Ls_02",
#     "toPosPara1": "1",
#     "toPosPara2": "body",
#     "doTask": "default"
# }
def robot(device_name: str,
          from_dev: str = None,
          from_pos_para1: str = None,
          from_pos_para2: str = None,
          to_dev: str = None,
          to_pos_para1: str = None,
          to_pos_para2: str = None,
          do_task: str = None
          ):
    """
    :param device_name:
    :param from_dev:
    :param from_pos_para1:
    :param from_pos_para2:
    :param to_dev:
    :param to_pos_para1:
    :param to_pos_para2:
    :param do_task:
    :return:
    """
    if device_name:
        robot_signal = False
        robot_id = init_robot().get(device_name)  # 选择机器人站号
        if from_dev and from_pos_para1 and from_pos_para2:  # 满足取板位条件
            task_num = [choice_device(from_dev), choice_num_pos(from_pos_para1), choice_grab_pos(from_pos_para2), choice_get_put("get"), robot_signal]
            for task in task_num:
                robot_id.write_coil(task, robot_signal)
            # robot_id.write_coil(choice_device(from_dev), robot_signal)  # 选择设备
            # robot_id.write_coil(choice_num_pos(from_pos_para1), robot_signal)  # 选择位置号
            # robot_id.write_coil(choice_grab_pos(from_pos_para2), robot_signal)  # 选择body/cover
            # robot_id.write_coil(choice_get_put("get"), robot_signal)  # 选择取板位\放板位
            robot_id.write_coil(1104, robot_signal)  # 选择取板位\放板位
        # if to_dev and to_pos_para1 and to_pos_para2:  # 满足放板位的条件
        #     robot_id.write_coil(choice_device(to_dev), robot_signal)  # 选择设备
        #     robot_id.write_coil(choice_num_pos(to_pos_para1), robot_signal)  # 选择位置号
        #     robot_id.write_coil(choice_grab_pos(to_pos_para2), robot_signal)  # 选择body/cover
        #     robot_id.write_coil(choice_get_put("put"), robot_signal)  # 选择取板位\放板位


robot_objs = init_robot()


class RobotActionService:
    def __init__(self):
        # self.robot = robot_num
        # self.device = device
        # self.get_put = get_put
        # self.grab_pos = grab_pos
        # self.num_pos = num_pos
        self.robot_obj = None
        self.sigal = True
        self.points = None
        self.callback_point = None

    def sigal_reset(self, point):
        self.robot_obj.write_coil(point, False)
        print("信号复位" + str(point))

    def save_params(self, robot_num, device, get_put, grab_pos, num_pos):

        self.robot_obj = init_robot().get(robot_num)
        """组合任务，四个点位为一个任务【设备号，取/放，夹爪位置，夹持位置】"""
        self.points = [choice_device(device)[0], choice_get_put(get_put)[0],
                       choice_grab_pos(grab_pos)[0], choice_num_pos(num_pos)[0]]
        self.callback_point = [choice_device(device)[1], choice_get_put(get_put)[1],
                               choice_grab_pos(grab_pos)[1], choice_num_pos(num_pos)[1]]
        print('机器人' + robot_num + "设备" + device + "取放" + get_put + "瓶子" + grab_pos + "位置" + num_pos)
        print(self.points)
        print(self.callback_point)
        while True:
            callback_sigal = [self.robot_obj.read_coils(i) for i in self.callback_point]
            if callback_sigal != [True, True, True, True]:
                for point in self.points:
                    self.robot_obj.write_coil(point, self.sigal)
                    time.sleep(0.5)
                print("四组点位写入成功")
            else:
                break

    def start_singe_step(self):
        """启动单步调试"""
        self.robot_obj.write_coil(load_config()["start"]["point"], self.sigal)
        while True:
            # if self.robot_obj.read_coils(load_config()["idle"]["point"]):
            if self.robot_obj.read_coils(load_config()["start_complete"]["point"]):
                self.sigal_reset(load_config()["start"]["point"])
                for i in self.points:
                    self.sigal_reset(i)
                break

    def clamp_action(self, status):
        """夹爪操作，控制夹爪打开关闭"""
        self.robot_obj.write_coil(load_config()[status]["point"], self.sigal)
        while True:
            if self.robot_obj.read_coils(load_config()["clamp_open_complete"]["point"]):
                self.sigal_reset(load_config()["clamp_open"]["point"])
                self.sigal_reset(load_config()[status]["point"])
                break
            if self.robot_obj.read_coils(load_config()["clamp_close_complete"]["point"]):
                self.sigal_reset(load_config()["clamp_close"]["point"])
                self.sigal_reset(load_config()[status]["point"])
                break

    def back_origin(self):
        """回原点"""
        self.robot_obj.write_coil(load_config()["back_origin"]["point"], self.sigal)
        while True:
            if self.robot_obj.read_coils(load_config()["zero"]["point"]):
                self.sigal_reset(load_config()["back_origin"]["point"])
                break

    def fuwei(self):
        """所有原点复位"""
        for i in range(1040, 1110):
            self.sigal_reset(i)
            time.sleep(0.1)


robot_action_service = RobotActionService()

# robot(device_name="Robot03", from_dev="xrPs_03", )
