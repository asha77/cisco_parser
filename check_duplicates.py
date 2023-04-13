import os
import regparsers


def check_config_duplicates(list_of_files):
    # поиск дубликатов конфигураций - конфигов с одним и тем же serial number
    serial_list = []
    # заполняем массив с серийниками
    file: object

    filenum = 0

    for file in list_of_files:
        if os.path.isfile(file):
            with open(file, "r") as conffile:
                config = conffile.read()
                serial_list.append([])
                serial_list[filenum].append(filenum + 1)
                serial_list[filenum].append(file)
                serial_list[filenum].append(regparsers.obtain_serial(config))
                filenum = filenum + 1

    # ищем дупликаты в массиве с серийниками
    for num in range(0, len(serial_list)):
        for num2 in range(num + 1, len(serial_list)):
            if serial_list[num][2] == serial_list[num2][2]:
                if serial_list[num][2] == 'Not Found':
                    print("В файлах не найдены серийные номера, проблема с идентификацией устройств:")
                    print("Файл: " + serial_list[num][1] + " Serial: " + serial_list[num][2])
                    print("Файл: " + serial_list[num2][1] + " Serial: " + serial_list[num2][2])
                else:
                    print("Устраните дублирование конфигураций:")
                    print("Файл: " + serial_list[num][1] + " Serial: " + serial_list[num][2])
                    print("Файл: " + serial_list[num2][1] + " Serial: " + serial_list[num2][2])
                return(False)
    return(True)