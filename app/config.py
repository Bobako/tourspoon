##
# @file 
#
# @brief Файл чтения конфигурации.
#
# @section desctiption_config Description
# В данном файле производится чтение конфигурационных данных из файла config.ini. Отсюда объект config можеть быть импортирован и использован в любом другом файле.

import configparser

## Путь к файлу конфигурации. Использует формат ini.
INI_FILE_PATH = "config.ini"

config = configparser.ConfigParser()

config.read(INI_FILE_PATH)
