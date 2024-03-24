import configparser

from robot_service.service.init.base_socket_service import ModbusClient


class Config(object):
    def __init__(self, filename, encoding):
        # 声明配置类对象
        self.config = configparser.ConfigParser()
        # 读取配置文件
        self.config.read(filename, encoding)

    def get_value(self, section, option):
        """获取 value"""
        value = self.config.get(section, option)
        return value

    def get_list(self):
        """获取机械臂列表"""
        value = self.config.sections()
        return value


def init_robot():
    config = Config('robot_service/config/config.ini', 'UTF-8')
    service_dict = {}
    print(config.get_list())
    for i in config.get_list():
        robot_s = ModbusClient(config.get_value(i, 'ip'), slave=1)
        robot_s.connect()
        service_dict.update({i: robot_s})
    print(service_dict)
    return service_dict
