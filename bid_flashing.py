import argparse
import pydrs
import time
from xlrd import open_workbook

params_01_element = [1, 2, 3, 4, 6, 7, 10, 11, 13, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 33, 34, 35, 36, 37]
params_04_element = [5, 8, 9, 12, 14, 15, 16, 17, 28, 29, 30, 31, 32, 38, 39, 40, 41, 42, 43, 50, 51]
params_32_element = [46, 47, 48, 49]
params_64_element = [0, 44, 45]

IP_DRS = "10.0.6.59"
PORT_DRS = 5000


def clear_bid():
    for param in params_01_element:
        drs.set_param(param, 0, 0)

    for param in params_04_element:
        for n in range(4):
            drs.set_param(param, n, 0)

    for param in params_32_element:
        for n in range(32):
            drs.set_param(param, n, 0)

    for param in params_64_element:
        for n in range(64):
            drs.set_param(param, n, 0)

    # ARM - Defaults
    drs.set_param(2, 0, 1)
    drs.set_param(4, 0, 6000000)
    drs.set_param(5, 0, 1)
    drs.set_param(5, 1, 30)
    drs.set_param(5, 2, 30)
    drs.set_param(5, 3, 30)
    drs.set_param(6, 0, 1)
    drs.set_param(10, 0, 1)



    # \/ MISSING CLEARING DSP & DSP DEFAULTS \/



    time.sleep(0.5)
    drs.save_param_bank(type_memory=1)
    time.sleep(0.5)


def read_spreadsheet(datafile = "Inventario.xls", bid = None, pstype = None):
    sheet = open_workbook(datafile).sheet_by_name("Inventario")
    keys = [sheet.cell(0, col_index).value for col_index in range(sheet.ncols)]
    items = {}
    for row_index in range(1,sheet.nrows):
        
        udc_name = sheet.cell(row_index,keys.index("UDC")).value
        udc_model =sheet.cell(row_index,keys.index("Modelo")).value
        ps_file = sheet.cell(row_index,keys.index("ps_parameters")).value
        dsp_file = sheet.cell(row_index,keys.index("dsp_parameters")).value
        bid_code = int(sheet.cell(row_index,keys.index("# BID")).value)

        if ("IA-" in udc_name):
            room_name =  udc_name[:5]
        else:
            room_name =  udc_name[:2]

        if(bid):
            if((sheet.cell(row_index,keys.index("# BID")).value == bid)):
                items[udc_name] = [udc_model, ps_file, dsp_file, room_name, bid_code]
        elif(pstype):
            if((sheet.cell(row_index,keys.index("Modelo")).value == pstype.upper())):
                items[udc_name] = [udc_model, ps_file, dsp_file, room_name, bid_code]
        
    return items


if (__name__ == '__main__'):

    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('-ps', '--power-supply', dest='ps_type', choices=['fbp', 'fbp-dclink', 'fap'])
    parser.add_argument('-bid', '--bid-id', dest='bid_id', type=int)
    args = parser.parse_args()

    drs = pydrs.EthDRS(IP_DRS, PORT_DRS)
    drs.slave_addr = 1
    psinfo = {}

    if((args.bid_id is not None) and (args.ps_type is not None)):
        print("Selecionar apenas a BID ou tipo de fonte!")
        exit()

    elif(args.ps_type is not None):
        print("PSType definido!")
        psinfo = read_spreadsheet(pstype=args.ps_type)

    elif(args.bid_id is not None):
        print("BID definida!")
        psinfo = read_spreadsheet(bid=args.bid_id)
        
        
    # psinfo[udc_name] = [udc_model, ps_file, dsp_file, room_name, bid_code]
    if psinfo:
        for ps in psinfo.keys():
            ps_param_path = 'udc-ps-parameters-db/{}/{}/{}'.format(psinfo[ps][3], psinfo[ps][0].lower(), psinfo[ps][1])
            dsp_param_path = 'udc-dsp-parameters-db/{}/{}/{}'.format(psinfo[ps][3], psinfo[ps][0].lower(), psinfo[ps][2])

            confirmation = input("Flash BID {} for UDC {}?\n( Y ) to continue or  ( N ) to skip UDC/BID\n Enter your choice (N): ".format(psinfo[ps][4], ps))
            if confirmation == "y" or confirmation == "Y":
                
                drs.unlock_udc(0xCAFE)
                time.sleep(1)

                print("Clearing BID...")
                clear_bid()

                print("Saving {} into BID...".format(psinfo[ps][1]))
                drs.set_param_bank(ps_param_path)
                time.sleep(0.5)
                drs.save_param_bank(type_memory=1)
                time.sleep(0.5)

                if (psinfo[ps][0].lower() != "fbp-dclink"):
                    print("Saving {} into BID...".format(psinfo[ps][2]))
                    drs.set_dsp_modules_bank(dsp_param_path)
                    time.sleep(0.5)
                    drs.save_dsp_modules_eeprom(type_memory=1)
                    time.sleep(0.5)
    #
    #            LEITURAS
    #            value = drs.get_param_bank()
    #            value = drs.get_dsp_modules_bank()
                #drs.reset_udc()
            else:
                print("Not updating.\n\n\n")
