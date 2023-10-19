#!/usr/bin/python3
import subprocess
import time
import datetime

import sys

import tkinter as tk

from tkinter import font
import tkinter.ttk as ttk

MIN_PYTHON = (3,0)

ip='192.168.48.46'

nch=4

class lvstat:
    def __init__(self,channel = 'u999'):#コンストラクタ=インスタンス化されたときに最初に呼ばれる特別なメソッド
        self.channel = channel
        self.outputVoltage = 0.0
        self.outputConfigMaxTerminalVoltage = 0.0
        self.outputMeasurementSenseVoltage = 0.0
        self.outputMeasurementTerminalVoltage = 0.0
        self.outputMeasurementCurrent = 0.0
        self.outputUserConfig = 0
        self.outputSwitch = 0


#1.すべてのmodlueの情報の一覧を取得#############################################################################################
def run_snmpwalk(name):
    result = subprocess.run('snmpwalk -v 2c -m +WIENER-CRATE-MIB -c guru ' + ip + ' '+name,shell=True, stdout = subprocess.PIPE)
    return result.stdout.decode("utf8")

lvstats = {}

#2. モジュール名をセンサ名に変更#################################################################################################
def convert_ch():
    Vch_name = {}
    path = './Vch_name.txt'
    with open(path) as f:
        for line in f:
            (i,j) = line.split(',')
            Vch_name[i] = j.rstrip()
    return Vch_name

#3. すべてのmodleのとってきた情報をlvstats{}に格納(4,5のrun_snmpwalk_float/intを用いて)#############################################
def get_info():
    #ch->modle名
    Vch_name = convert_ch()

    #1.outputVoltage
    results = run_snmpwalk_float('outputVoltage')#'ret'の値、つまり、nameで指定したすべてのchannelの情報が並んだリストをresultに入れる。
    for item in results:
        lvtmp = lvstat()#class lvstatusで定義した関数を用いる
        try:
            lvtmp.channel = Vch_name[item[0]]#item[0]はchannnel名。item[1]はnameの値
        except:
            print('e')
        lvtmp.outputVoltage = item[1]
        lvstats[Vch_name[item[0]]] =lvtmp#lvstatusという辞書の中に、[module名:name]の値を入れる。※.outputVoltageなどで区別されているため、OIDは混ざらない。

    #2.outputConfigMaxTerminalVoltage
    results = run_snmpwalk_float('outputConfigMaxTerminalVoltage')
    for item in results:
        lvstats[Vch_name[item[0]]].outputConfigMaxTerminalVoltage = item[1]

    #3.outputMeasurementSenseVoltage
    results = run_snmpwalk_float('outputMeasurementSenseVoltage')
    for item in results:
        lvstats[Vch_name[item[0]]].outputMeasurementSenseVoltage = item[1]

    #4.outputMeasurementTerminalVoltage
    results = run_snmpwalk_float('outputMeasurementTerminalVoltage')
    for item in results:
        lvstats[Vch_name[item[0]]].outputMeasurementTerminalVoltage = item[1]

    #5.outputMeasurementCurrent
    results = run_snmpwalk_float('outputMeasurementCurrent')
    for item in results:
        if Vch_name[item[0]][-2] == 'H':
            lvstats[Vch_name[item[0]]].outputMeasurementCurrent = str(float(item[1])*1000000) #uA
        else:
            lvstats[Vch_name[item[0]]].outputMeasurementCurrent = item[1]

    #6.outputUserConfig
    if Vch_name[item[0]][-2] != 'H':
        results = run_snmpwalk_int('outputUserConfig')
        for item in results:
            lvstats[Vch_name[item[0]]].outputUserConfig = item[1]

    #7.outputSwitch
    results = run_snmpwalk_int_onoff('outputSwitch')
    for item in results:
        lvstats[Vch_name[item[0]]].outputSwitch = item[1]


#4. すべてのchの情報をとってくるマクロ#########################################################################################
def run_snmpwalk_float(name):
    result = run_snmpwalk(name)
    result_strs = result.splitlines() #出力を改行で分割

    ret = []#結果を格納するリスト->channelごとのnameの情報を並べる

    # 各行ごとに処理
    for item in result_strs:#result_strsは行ごとに区切った情報(任意のチャンネルのname情報)
        line = item.split()#itemを空白で区切る
        tmp = line[0].split('.')#最初の要素を'.'で分割->WIENER-CRATE-MIB::outputVoltage.u101
        channel = tmp[-1]#channel名をひろう->u101
        var = line[-2]#値をひろう->Float: 2.500000 V->2.500000
        ret.append([channel,var])#retに追加。それは、[チャンネル名、値]で格納
    return ret

#5. int型の情報を4.と同じようにとってくる。#######################################################################################
def run_snmpwalk_int(name):
    result = run_snmpwalk(name)
    result_strs = result.splitlines()

    ret = []
    for item in result_strs:
        line = item.split()
        tmp = line[0].split('.')
        channel = tmp[-1]
        var = line[-1]
        ret.append([channel,var])
    return ret

#6. int型の情報を上と同じようにとってくる。(of/off関係)#############################################################################
def run_snmpwalk_int_onoff(name):
    result = run_snmpwalk(name)
    result_strs = result.splitlines()

    ret = []
    for item in result_strs:
        line = item.split()
        tmp = line[0].split('.')
        channel = tmp[-1]
        var = line[-1]
        ret.append([channel,var])
    return ret

#7. 取得したデータから任意のmodle_nameとOIDの情報のみをとってくる(3.を用いて)##########################################################
def get_info_detail(modle_name,oid_name):
    get_info()#情報取得の関数を呼び出す。
    #1.outputVoltage
    if oid_name == 'outputVoltage':
        if str(modle_name) not in lvstats.keys():
            oid_value = 'none'
        else:
            oid_value = round(float(lvstats[modle_name].outputVoltage),3)

    #2.outputConfigMaxTerminalVoltage
    elif oid_name == 'outputConfigMaxTerminalVoltage':
        if str(modle_name) not in lvstats.keys():
            oid_value = 'none'
        else:
            oid_value = round(float(lvstats[modle_name].outputConfigMaxTerminalVoltage),3)

    #3.outputMeasurementSenseVoltage
    elif oid_name == 'outputMeasurementSenseVoltage':
        if str(modle_name) not in lvstats.keys():
            oid_value = 'none'
        else:
            oid_value = round(float(lvstats[modle_name].outputMeasurementSenseVoltage),3)

    #4.outputMeasurementTerminalVoltage
    elif oid_name == 'outputMeasurementTerminalVoltage':
        if str(modle_name) not in lvstats.keys():
            oid_value = 'none'
        else:
            oid_value = round(float(lvstats[modle_name].outputMeasurementTerminalVoltage),3)

    #5.outputMeasurementCurrent
    elif oid_name == 'outputMeasurementCurrent':
        if str(modle_name) not in lvstats.keys():
            oid_value = 'none'
        else:
            oid_value = round(float(lvstats[modle_name].outputMeasurementCurrent),3)

    #6.outputUserConfig
    elif oid_name == 'outputUserConfig':
        if str(modle_name) not in lvstats.keys():
            oid_value = 'none'
        else:
            oid_value = int(lvstats[modle_name].outputUserConfig)

    #7.outputSwitch
    elif oid_name == 'outputSwitch':
        if str(modle_name) not in lvstats.keys():
            oid_value = 'none'
        else:
            oid_value = lvstats[modle_name].outputSwitch

    else:
        print('such OID name is none')

    return oid_value

#8. GUIの表に入れる値をテキスト化する############################################################################################
def gui_value(row,sens_name,oid):
    if row == 1:
        ch_name = str(sens_name) + '_P2.5'
    elif row == 2:
        ch_name = str(sens_name) + '_P2.3'
    elif row == 3:
        ch_name = str(sens_name) + '_N2.5'
    elif row == 4:
        ch_name = str(sens_name) + '_N2.3'
    elif row == 5:
        ch_name = str(sens_name) + '_P_HV'
    elif row == 6:
        ch_name = str(sens_name) + '_N_HV'

    label_text = f"{get_info_detail(ch_name,oid)}"
    return label_text

#9. GUIの表に入れる値(switch:on/off)をテキスト化&背景色化する#############################################################################
def on_off_value(row,sens_name):
    on_off = gui_value(row,sens_name,'outputSwitch')

    if on_off == 'on(1)':
        on_off_label = 'ON'
        button_bg = 'green'
    elif on_off == 'off(0)':
        on_off_label = 'OFF'
        button_bg = 'gray80'
    else :
        on_off_label = 'none'
        button_bg = 'gray80'

    return on_off_label,button_bg

#9. GUIの表に入れる値(sensewire:on/off)をテキスト化&背景色化する###########################################################################
def userconfig_value(row,sens_name):
    on_off = gui_value(row,sens_name,'outputUserConfig')

    if on_off == '2':
        on_off_label = 'ON'
        button_bg = 'green'
    elif on_off == '8':
        on_off_label = 'OFF'
        button_bg = 'gray80'
    else :
        on_off_label = 'none'
        button_bg = 'gray80'

    return on_off_label,button_bg

#10. テキストをupdateする#############################################################################################################
def update_text(label,row,sens_name,oid):
    current_text = gui_value(row,sens_name,oid)
    label.config(text=current_text)
    root.after(30000, lambda: update_text(label,row,sens_name,oid))

#11. switchをupdateする###########################################################################################################
def update_on_off_button(button,row,sens_name):
    current_txt, current_bg = on_off_value(row,sens_name)
    button.config(text=current_txt ,bg=current_bg)
    root.after(30000, lambda: update_on_off_button(button,row,sens_name))

#12. sensewireをupdateする#########################################################################################################
def update_userconfig_button(button,row,sens_name):
    current_txt, current_bg = userconfig_value(row,sens_name)
    button.config(text=current_txt ,bg=current_bg)
    root.after(30000, lambda: update_userconfig_button(button,row,sens_name))

#13. modle名とセンサ名をひっくり返す###################################################################################################
def get_keys_by_value(dct, value):
    keys = []
    for key, val in dct.items():
        if val == value:
            keys.append(key)
    return ', '.join(keys)

#14. 設定電圧変更####################################################################################################################
def snmp_set(check, voltage, oid, ch_name):
    Vch_name = convert_ch()
    ch = get_keys_by_value(Vch_name, ch_name)
    if check:
        output = subprocess.run('snmpset -v 2c -m +WIENER-CRATE-MIB -c guru' +' '+ ip + ' '+oid+'.'+ch+' F '+voltage,shell=True, stdout = subprocess.PIPE)
        print(ch_name)
        print(ch)
        print(output)
    else:
        print('check the box!')

#15. 設定スイッチon(switch & sensewire)#############################################################################################
def snmp_set_on(check, oid, ch_name):
    Vch_name = convert_ch()
    ch = get_keys_by_value(Vch_name, ch_name)
    if check:
        if oid == 'outputSwitch':
            output = subprocess.run('snmpset -v 2c -m +WIENER-CRATE-MIB -c guru' +' '+ ip + ' outputSwitch.'+ch+' i 1',shell=True, stdout = subprocess.PIPE)
        else:
            output = subprocess.run('snmpset -v 2c -m +WIENER-CRATE-MIB -c guru' +' '+ ip + ' outputUserConfig.'+ch+' i 2',shell=True, stdout = subprocess.PIPE)
        print(ch_name)
        print(ch)
        print(output)
    else:
        print('check the box!')

#16. 設定スイッチoff(switch & sensewire)############################################################################################
def snmp_set_off(check, oid, ch_name):
    Vch_name = convert_ch()
    ch = get_keys_by_value(Vch_name, ch_name)
    if check:
        if oid == 'outputSwitch':
            output = subprocess.run('snmpset -v 2c -m +WIENER-CRATE-MIB -c guru' +' '+ ip + ' outputSwitch.'+ch+' i 0',shell=True, stdout = subprocess.PIPE)
        else:
            output = subprocess.run('snmpset -v 2c -m +WIENER-CRATE-MIB -c guru' +' '+ ip + ' outputUserConfig.'+ch+' i 8',shell=True, stdout = subprocess.PIPE)
        print(ch_name)
        print(ch)
        print(output)
    else:
        print('check the box!')

#17. "onにしました"ウィンドウ############################################################################################################
def result_on_window(check):
    def enter_click():
        res_wd.destroy()

    res_wd = tk.Toplevel(root)
    res_wd.title("comfirm")
    res_wd.geometry("300x100")
    if check:
        la = tk.Label(res_wd, text='ONに変更しました')
    else:
        la = tk.Label(res_wd, text='チェックボックスにチェックしてください')
    la.pack(anchor='center',expand=1)

    bt = ttk.Button(res_wd, text='OK', command=enter_click)
    bt.pack()

#18. "offにしました"ウィンドウ############################################################################################################
def result_off_window(check):
    def enter_click():
        res_wd.destroy()

    res_wd = tk.Toplevel(root)
    res_wd.title("comfirm")
    res_wd.geometry("300x100")
    if check:
        la = tk.Label(res_wd, text='OFFに変更しました')
    else:
        la = tk.Label(res_wd, text='チェックボックスにチェックしてください')
    la.pack(anchor='center',expand=1)

    bt = ttk.Button(res_wd, text='OK', command=enter_click)
    bt.pack()

#19. on/off変更ウィンドウ############################################################################################################
def on_off_window(row,sens_name,oid):
    def on_click():
        check = var.get()
        result_on_window(check)
        snmp_set_on(check, oid, ch_name)
        on_off_wd.destroy()

    def off_click():
        check = var.get()
        result_off_window(check)
        snmp_set_off(check, oid, ch_name)
        on_off_wd.destroy()

    # 新規ウィンドウを表示
    on_off_wd = tk.Toplevel(root)
    on_off_wd.title("Fix window")
    on_off_wd.geometry("300x100")

    var = tk.BooleanVar()
    chk = tk.Checkbutton(on_off_wd, text='設定を変更しますか？', variable=var)
    chk.pack(side=tk.TOP)

    if row == 1:
        ch_name = str(sens_name) + '_P2.5'
    elif row == 2:
        ch_name = str(sens_name) + '_P2.3'
    elif row == 3:
        ch_name = str(sens_name) + '_N2.5'
    elif row == 4:
        ch_name = str(sens_name) + '_N2.3'
    elif row == 5:
        ch_name = str(sens_name) + '_P_HV'
    elif row == 6:
        ch_name = str(sens_name) + '_N_HV'
    text_name = ch_name+' '+oid
    la = tk.Label(on_off_wd, text=text_name)
    la.pack()

    bt_on = tk.Button(on_off_wd, text='ON', command=on_click, bg='green')
    bt_on.pack()
    bt_off = tk.Button(on_off_wd, text='OFF', command=off_click, bg='gray80')
    bt_off.pack()

    on_off_wd.mainloop()

#20. "設定電圧変更しました"ウィンドウ#############################################################################################################
def result_window(voltage, check):
    def enter_click():
        res_wd.destroy()

    res_wd = tk.Toplevel(root)
    res_wd.title("comfirm")
    res_wd.geometry("300x100")
    if check:
        la = tk.Label(res_wd, text=f'{voltage}Vに変更しました')
    else:
        la = tk.Label(res_wd, text='チェックボックスにチェックしてください')
    la.pack(anchor='center',expand=1)

    bt = ttk.Button(res_wd, text='OK', command=enter_click)
    bt.pack()

#21. 設定電圧変更ウィンドウ#############################################################################################################
def fix_window(row,sens_name,oid):
    def enter_button_click():
        voltage = txt.get()
        check = var.get()
        result_window(voltage, check)
        snmp_set(check, voltage, oid, ch_name)
        fix_wd.destroy()

    # 新規ウィンドウを表示
    fix_wd = tk.Toplevel(root)
    fix_wd.title("Fix window")
    fix_wd.geometry("300x100")

    var = tk.BooleanVar()
    chk = tk.Checkbutton(fix_wd, text='設定を変更しますか？', variable=var)
    chk.pack(side=tk.TOP)

    if row == 1:
        ch_name = str(sens_name) + '_P2.5'
    elif row == 2:
        ch_name = str(sens_name) + '_P2.3'
    elif row == 3:
        ch_name = str(sens_name) + '_N2.5'
    elif row == 4:
        ch_name = str(sens_name) + '_N2.3'
    elif row == 5:
        ch_name = str(sens_name) + '_P_HV'
    elif row == 6:
        ch_name = str(sens_name) + '_N_HV'
    text_name = ch_name+' '+oid
    la = tk.Label(fix_wd, text=text_name)
    la.pack()

    txt = tk.Entry(fix_wd, width=20)
    txt.pack()

    bt = ttk.Button(fix_wd, text='ENTER', command=enter_button_click)
    bt.pack()

    fix_wd.mainloop()

#22. GUI1sensorの表作り##############################################################################################################
def create_frame(root, rows, columns, sens_name):#"rows"(行)x"columns"(列)の表を作るframe
    frame = tk.Frame(root)#rootに"frame"という"frame"を用意
    labels = []#"labels"と"buttons"という配列を用意
    buttons = []

    for row in range(rows):#rowでloop
        row_labels = []#"row_labels"と"row_buttons"という配列を用意
        row_buttons = []

        for col in range(columns):
            if row >= 1 and col == 0:#「センサ」= row(行)が2行目以降、1列目はマージ
                merged_frame = tk.Frame(frame, borderwidth=1, relief="solid")#merged_frameというframeを設定
                merged_frame.grid(row=1, column=0, rowspan=rows-1, sticky="nsew")#2行１列目,"rowspan"複数行にまたがるフレームの複数行のこと
                merged_frame.grid_columnconfigure(0, weight=1)#高さ調節
                merged_frame.grid_rowconfigure(0, weight=1)#幅調節

                # Create labels inside the merged frame
                label_text = f"{sens_name}"#sensor名入れる
                label = tk.Label(merged_frame, text=label_text)#"label"を"merged_frame"に配置
                label.grid(sticky="nsew")#???----------------------------------------------------------------------------------------------------?

                # Save the label in the row_labels list
                row_labels.append(label)#

            elif row >= 1 and row <=4 and col == 1:#「センサ」= row(行)が2行目以降、1列目はマージ
                merged_frame = tk.Frame(frame, borderwidth=1, relief="solid")#merged_frameというframeを設定
                merged_frame.grid(row=1, column=1, rowspan=4, sticky="nsew")#2行１列目,"rowspan"複数行にまたがるフレームの複数行のこと
                merged_frame.grid_columnconfigure(0, weight=1)#高さ調節
                merged_frame.grid_rowconfigure(0, weight=1)#幅調節

                # Create labels inside the merged frame
                label_text = "LV"#LV
                label = tk.Label(merged_frame, text=label_text)#"label"を"merged_frame"に配置
                label.grid(sticky="nsew")#???----------------------------------------------------------------------------------------------------?

                # Save the label in the row_labels list
                row_labels.append(label)#

            elif row >= 5 and col == 1:#「センサ」= row(行)が6行目以降、2列目はマージ
                merged_frame = tk.Frame(frame, borderwidth=1, relief="solid")#merged_frameというframeを設定
                merged_frame.grid(row=5, column=1, rowspan=2, sticky="nsew")#2行１列目,"rowspan"複数行にまたがるフレームの複数行のこと
                merged_frame.grid_columnconfigure(0, weight=1)#高さ調節
                merged_frame.grid_rowconfigure(0, weight=1)#幅調節

                # Create labels inside the merged frame
                label_text = "HV"#HV
                label = tk.Label(merged_frame, text=label_text)#"label"を"merged_frame"に配置
                label.grid(sticky="nsew")#???----------------------------------------------------------------------------------------------------?

                # Save the label in the row_labels list
                row_labels.append(label)#?????????????????????????????????????????????????????????????????????????????????????????????????????????????????

#################ここからOID情報を入れなくては!!!!!!!!!!!!!!!#####################################################################################
            elif row >= 1 and col == 3:#"on/off"のあるフレーム"sub_frame"の作成
                subframe = tk.Frame(frame, borderwidth=1, relief="solid")
                subframe.grid(row=row, column=col, sticky="nsew")
                subframe.grid_columnconfigure(0, weight=1)
                subframe.grid_columnconfigure(1, weight=1)
                subframe.grid_rowconfigure(0, weight=1)

                # Create button inside the right subframe
                button_text,button_bg = on_off_value(row,sens_name)
                #style = ttk.Style()
                #style.configure('TButton', background=button_bg)
                if row == 1:
                    button = tk.Button(subframe, text=button_text, command=lambda: on_off_window(1,sens_name,'outputSwitch'), bg=button_bg)
                elif row == 2:
                    button = tk.Button(subframe, text=button_text, command=lambda: on_off_window(2,sens_name,'outputSwitch'), bg=button_bg)
                elif row == 3:
                    button = tk.Button(subframe, text=button_text, command=lambda: on_off_window(3,sens_name,'outputSwitch'), bg=button_bg)
                elif row == 4:
                    button = tk.Button(subframe, text=button_text, command=lambda: on_off_window(4,sens_name,'outputSwitch'), bg=button_bg)
                elif row == 5:
                    button = tk.Button(subframe, text=button_text, command=lambda: on_off_window(5,sens_name,'outputSwitch'), bg=button_bg)
                elif row == 6:
                    button = tk.Button(subframe, text=button_text, command=lambda: on_off_window(6,sens_name,'outputSwitch'), bg=button_bg)

                #button = tk.Button(bg= button_bg)
                button.grid(row=0, column=1, sticky=tk.EW)
                row_buttons.append(button)

            # 4=OutputVoltage & 5=outputConfigMaxTerminalVoltage
            elif row >= 1 and (col == 4 or col == 5):#"fixbotton"のあるフレーム"sub_frame"の作成
                # 2nd row onwards, 3rd column (two frames side by side)
                subframe = tk.Frame(frame, borderwidth=1, relief="solid")
                subframe.grid(row=row, column=col, sticky="nsew")
                subframe.grid_columnconfigure(0, weight=1)
                subframe.grid_columnconfigure(1, weight=1)
                subframe.grid_rowconfigure(0, weight=1)

                button_text = "fix"
                # Create label inside the left subframe
                if col == 4:
                    oid_4 = 'outputVoltage'
                    label_text = gui_value(row,sens_name,oid_4)

                    # Create button inside the right subframe
                    if row == 1:
                        button = ttk.Button(subframe, text=button_text, command=lambda: fix_window(1,sens_name,oid_4))
                    elif row == 2:
                        button = ttk.Button(subframe, text=button_text, command=lambda: fix_window(2,sens_name,oid_4))
                    elif row == 3:
                        button = ttk.Button(subframe, text=button_text, command=lambda: fix_window(3,sens_name,oid_4))
                    elif row == 4:
                        button = ttk.Button(subframe, text=button_text, command=lambda: fix_window(4,sens_name,oid_4))
                    elif row == 5:
                        button = ttk.Button(subframe, text=button_text, command=lambda: fix_window(5,sens_name,oid_4))
                    elif row == 6:
                        button = ttk.Button(subframe, text=button_text, command=lambda: fix_window(6,sens_name,oid_4))
                else:
                    oid_5 = 'outputConfigMaxTerminalVoltage'
                    label_text = gui_value(row,sens_name,oid_5)

                    # Create button inside the right subframe
                    if row == 1:
                        button = ttk.Button(subframe, text=button_text, command=lambda: fix_window(1,sens_name,oid_5))
                    elif row == 2:
                        button = ttk.Button(subframe, text=button_text, command=lambda: fix_window(2,sens_name,oid_5))
                    elif row == 3:
                        button = ttk.Button(subframe, text=button_text, command=lambda: fix_window(3,sens_name,oid_5))
                    elif row == 4:
                        button = ttk.Button(subframe, text=button_text, command=lambda: fix_window(4,sens_name,oid_5))
                    elif row == 5:
                        button = ttk.Button(subframe, text=button_text, command=lambda: fix_window(5,sens_name,oid_5))
                    elif row == 6:
                        button = ttk.Button(subframe, text=button_text, command=lambda: fix_window(6,sens_name,oid_5))

                label = tk.Label(subframe, text=label_text, bg= 'white')#現在の電圧表示
                label.grid(row=0, column=0, sticky="nsew")
                row_labels.append(label)

                button.grid(row=0, column=1, sticky="nsew")
                #row_buttons.append(button)

            #9=OutputUserConfig
            elif row >= 1 and row <=4 and col == 9:#"sense_wire_mode"のあるフレーム"sub_frame"の作成
                # 2nd row onwards, 3rd column (two frames side by side)
                subframe = tk.Frame(frame, borderwidth=1, relief="solid")
                subframe.grid(row=row, column=col, sticky="nsew")
                subframe.grid_columnconfigure(0, weight=1)
                subframe.grid_columnconfigure(1, weight=1)
                subframe.grid_rowconfigure(0, weight=1)

                # Create button inside the right subframe
                button_text_sw,button_bg_sw = userconfig_value(row,sens_name)
                #style = ttk.Style()
                #style.configure('TButton', background=button_bg_sw)
                if row == 1:
                        button = tk.Button(subframe, text=button_text_sw, command=lambda: on_off_window(1,sens_name,'outputUserConfig'), bg=button_bg_sw)
                elif row == 2:
                    button = tk.Button(subframe, text=button_text_sw, command=lambda: on_off_window(2,sens_name,'outputUserConfig'), bg=button_bg_sw)
                elif row == 3:
                    button = tk.Button(subframe, text=button_text_sw, command=lambda: on_off_window(3,sens_name,'outputUserConfig'), bg=button_bg_sw)
                elif row == 4:
                    button = tk.Button(subframe, text=button_text_sw, command=lambda: on_off_window(4,sens_name,'outputUserConfig'), bg=button_bg_sw)
                elif row == 5:
                    button = tk.Button(subframe, text=button_text_sw, command=lambda: on_off_window(5,sens_name,'outputUserConfig'), bg=button_bg_sw)
                elif row == 6:
                    button = tk.Button(subframe, text=button_text_sw, command=lambda: on_off_window(6,sens_name,'outputUserConfig'), bg=button_bg_sw)

                #button = tk.Button(bg= button_bg)
                button.grid(row=0, column=1, sticky=tk.EW)
                row_buttons.append(button)

            else:
                # Other frames
                subframe = tk.Frame(frame, borderwidth=1, relief="solid")
                subframe.grid(row=row, column=col, sticky="nsew")
                subframe.grid_columnconfigure(0, weight=1)
                subframe.grid_rowconfigure(0, weight=1)

                # Create label inside the frame
                if row == 0:
                    bg_color = 'gray80'
                    if col == 0:
                        label_text = "Sensor"
                    elif col == 1:
                        label_text = "LV/HV"
                    elif col == 2:
                        label_text = "Name"
                    elif col == 3:
                        label_text = "Power"
                    elif col == 4:
                        label_text = "OutV [V]"
                    elif col == 5:
                        label_text = "MaxV [V]"
                    elif col == 6:
                        label_text = "MeasV [V]"
                    elif col == 7:
                        label_text = "MeasTV [V]"
                    elif col == 8:
                        label_text = "MeasC [A/uA]"
                    else:
                        label_text = "SW mode"

                elif col == 2:
                    bg_color = 'gray80'
                    if row == 1:
                        label_text = "P 2.5V"
                    elif row == 2:
                        label_text = "P 2.3V"
                    elif row == 3:
                        label_text = "N 2.5V"
                    elif row == 4:
                        label_text = "N 2.3V"
                    elif row == 5:
                        label_text = "P(-)"
                    else:
                        label_text = "N(+)"
                else:
                    bg_color = 'white'
                    if col == 6:
                        oid_6789 = 'outputMeasurementSenseVoltage'
                    elif col == 7:
                        oid_6789 = 'outputMeasurementTerminalVoltage'
                    elif col == 8:
                        oid_6789 = 'outputMeasurementCurrent'
                    else:
                        oid_6789 = 'outputUserConfig'

                    label_text = gui_value(row,sens_name,oid_6789)
                label = tk.Label(subframe, text=label_text, bg=bg_color)
                label.grid(sticky="nsew")
                row_labels.append(label)

        labels.append(row_labels)
        buttons.append(row_buttons)
    return frame, labels, buttons

#23. 実際にGUIを作るマクロ#############################################################################################################
def create_gui():
    n_sens = 0
    frame_grid = []
    d_sens = {0:"prot", 1:"GBT/RP", 2:106, 3:104, 4:108, 5:102, 6:109, 7:101, 8:206, 9:207}
    oid = {4:'outputVoltage', 5:'outputConfigMaxTerminalVoltage', 6:'outputMeasurementSenseVoltage',7:'outputMeasurementTerminalVoltage',8:'outputMeasurementCurrent',9:'outputUserConfig'}
    for i in range(1):#行row
        row_frames = []
        for j in range(2):#列columm
            frame, labels, buttons = create_frame(root, 7, 10, d_sens[n_sens])
            frame.grid(row=i, column=j, padx=5, pady=5)
            for row in range(7):
                if row != 0:
                    for col in range(10):
                        oid_col = col-1
                        if col >= 4 and col <=8:
                            label = labels[row][oid_col]
                            update_text(label,row,d_sens[n_sens],oid[col])
                        elif col ==3:
                            button = buttons[row][0]
                            update_on_off_button(button,row,d_sens[n_sens])
                        elif col == 9:
                            button = buttons[row][-1]
                            update_userconfig_button(button,row,d_sens[n_sens])
            row_frames.append(frame)
            n_sens+=1
        frame_grid.append(row_frames)


if __name__ == "__main__":
    root = tk.Tk()
    root.title("STS_Voltage_Manager")
    root.resizable(False, False)
    root.geometry("1270x350")
    create_gui()
    root.mainloop()
