from asyncio import subprocess
import argparse
import pydrs
import re
import subprocess
from xlrd import open_workbook



IP_DRS = ""
PORT_DRS = 5000



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

        if (udc_name.split("-")[0] == "IA"):
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
    parser.add_argument('-ps', '--power-supply', dest='ps_type', choices=['fbp', 'fbp-dclink'])
    parser.add_argument('-bid', '--bid-id', dest='bid_id', type=int)
    args = parser.parse_args()

 #   drs = pydrs.pydrs.EthDRS(IP_DRS, PORT_DRS)
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
        
        
    # psinfo = [udc_model, ps_file, dsp_file, room_name, bid_code]}
    if psinfo:
        for ps in psinfo.keys():
            print(ps, psinfo[ps])
            ps_param_path = 'udc-ps-parameters-db/{}/{}/{}'.format(psinfo[ps][3], psinfo[ps][0].lower(), psinfo[ps][1])
            dsp_param_path = 'udc-dsp-parameters-db/{}/{}/{}'.format(psinfo[ps][3], psinfo[ps][0].lower(), psinfo[ps][2])
            print(ps_param_path)
            print(dsp_param_path)


            confirmation = input("Proceed to Parameters Update?        ( Y ) to continue or  ( N ) to skip UDC/BID\n Enter your choice (N): ")
            if confirmation == "y" or confirmation == "Y":
                print("Parameters update process iniciated")
    #            drs.unlock_udc(0xCAFE)
    #
    #            drs.set_param_bank(ps_param_path)
    #            time.sleep(1)
    #            drs.save_param_bank(type_memory=1)
    #            time.sleep(1)
    #
    #            drs.set_dsp_modules_bank(dsp_param_path)
    #            time.sleep(1)
    #            drs.save_dsp_modules_eeprom(type_memory=1)
    #            time.sleep(1)
            else:
                print("Not updating.\n\n")




# LEITURAS
# get_param_bank()
# get_dsp_modules_bank()