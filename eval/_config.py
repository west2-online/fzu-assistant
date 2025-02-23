import json

class DotDict:
    """支持点号访问的字典"""
    def __init__(self, data):
        for key, value in data.items():
            if isinstance(value, dict):
                setattr(self, key, DotDict(value))  # 递归转换
            else:
                setattr(self, key, value)

    def __getitem__(self, key):
        return getattr(self, key)

    def __repr__(self):
        return str(self.__dict__)

class Config(DotDict):
    """加载 JSON 配置文件的类"""
    def __init__(self, config_path="config.json"):
        with open(config_path, "r", encoding="utf-8") as f:
            config_data = json.load(f)
        super().__init__(config_data)  # 继承 DotDict，实现点号访问

# 读取配置
_conf = Config("./eval/config.json")

# 访问配置
if __name__ == '__main__':
    print(_conf.ZHIPU.Model_name)
