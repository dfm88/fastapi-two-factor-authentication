from enum import Enum


class DeviceTypeEnum(str, Enum):
    EMAIL: str = 'email'
    CODE_GENERATOR: str = 'code_generator'

    def __str__(self):
        return self.value
