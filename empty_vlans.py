from netmiko import ConnectHandler
import os

# Параметры подключения для устройства, на котором будем просматривать VLAN

DEVICE_IP = '172.31.0.3'

DEVICES_PARAMS = {
    'device_type'           : 'huawei',
    'ip'                    :  DEVICE_IP,
    'username'              : 'username',
    'password'              : 'password',
    'global_delay_factor'   : 2, 
    'read_timeout_override' : 90  }

#
# Составление списка проверяемых VLAN
#

def vlan_id_list():

    # Вывод фрагмента общей конфигурации коммутатора касательно отдельно VLAN

    connect = ConnectHandler(**DEVICES_PARAMS)
    connect.find_prompt()
    vlan_list = connect.send_command(f'display current-configuration configuration vlan')
    connect.disconnect()

    # Запись фрагмента в файл

    with open("vlan_cfg", "w") as f:
        f.writelines(vlan_list)

    # Чтение того же файла, поиск блока настройки VLAN - оставляем только VLAN ID и записываем в новый файл

    with open("vlan_cfg") as src, open("vlan_list", "w") as dst:
        for ln in src:
            if ln.startswith("vlan"):
                vlan_id ="".join(filter(str.isdecimal, ln))
                dst.write(str(vlan_id) + "\n")

#
# Формирование списка VLAN и общего количества MAC-адресов в каждом
#

def empty_vlan():

    connect = ConnectHandler(**DEVICES_PARAMS)
    connect.find_prompt()

    # Выводим MAC-таблицу для каждого VLAN и записываем в соответсвующий файл

    with open("vlan_list") as src, open("total_mac", "w") as dst:
        for ID in src:
            mac_table = connect.send_command(f"display mac-address vlan {ID}")
            dst.write(mac_table + "\n")

    connect.disconnect()

    # В выводе предыдущей команды находим строку "Total items:" и записываем её полностью в новый файл

    with open("total_mac") as src, open("total_brief", "w") as dst:    
        for ln in src:        
            if ln.startswith("Total items:"):      
                dst.write(ln)

    # Считываем два файла и пишем соединённый результат в итоговый новый файл

    with open("vlan_list") as src1, open("total_brief") as src2, open("result", "w") as dst:
        for line1, line2 in zip(src1, src2):
            dst.write("VLAN " + line1.strip() + "   " + line2)

    os.remove("vlan_list")
    os.remove("vlan_cfg")
    os.remove("total_mac")
    os.remove("total_brief")

vlan_id_list()
empty_vlan()