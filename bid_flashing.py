#!/usr/bin/python3
import argparse
import pydrs
import time
from xlrd import open_workbook


IP_DRS = "10.0.6.59"
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

        if "fbp" not in udc_model.lower():
            udc_model = udc_model[:3]

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
    parser.add_argument('-memory', '--type-memory', dest='type_mem', type=int, choices=[1, 2], default=1)
    args = parser.parse_args()

    memoryType = {1: "BID", 2:"on-board"}

    drs = pydrs.EthDRS(IP_DRS, PORT_DRS)
    drs.slave_addr = 1
    psinfo = {}

    if((args.bid_id is not None) and (args.ps_type is not None)):
        print("Selecionar apenas a BID ou tipo de fonte!")
        exit()

    elif(args.ps_type is not None):
        psinfo = read_spreadsheet(pstype=args.ps_type)

    elif(args.bid_id is not None):
        psinfo = read_spreadsheet(bid=args.bid_id)
        
        
    # psinfo[udc_name] = [udc_model, ps_file, dsp_file, room_name, bid_code]
    if psinfo:
        for ps in psinfo.keys():
            ps_param_path = 'udc-ps-parameters-db/{}/{}/{}'.format(psinfo[ps][3], psinfo[ps][0].lower(), psinfo[ps][1])
            dsp_param_path = 'udc-dsp-parameters-db/{}/{}/{}'.format(psinfo[ps][3], psinfo[ps][0].lower(), psinfo[ps][2])

            confirmation = input("Flash BID {} for UDC {}?\n( Y ) to continue or  ( N ) to skip UDC/BID\n Enter your choice (N): ".format(psinfo[ps][4], ps))
            if confirmation == "y" or confirmation == "Y":
                
                #print("Clearing BID...")
                #drs.clear_bid(password=0xCAFE)
                drs.unlock_udc(0xCAFE)


                print("Saving {} into {} memory...".format(psinfo[ps][1], memoryType[args.type_mem]))
                bid_ps_bank = drs.set_param_bank(ps_param_path)
                time.sleep(0.5)
                drs.save_param_bank(type_memory=args.type_mem)
                time.sleep(0.5)

                if (psinfo[ps][0].lower() != "fbp-dclink"):
                    print("Saving {} into {} memory...".format(psinfo[ps][2], memoryType[args.type_mem]))
                    bid_dsp_bank = drs.set_dsp_modules_bank(dsp_param_path)
                    time.sleep(0.5)
                    drs.save_dsp_modules_eeprom(type_memory=args.type_mem)
                    time.sleep(0.5)

    #            LEITURAS
                drs.load_param_bank(type_memory=args.type_mem)
                read_ps_bank = drs.get_param_bank(print_modules=False)
              
                for param_name in bid_ps_bank.keys():
                    for i in range(len(bid_ps_bank[param_name])):
                        if(bid_ps_bank[param_name][i][1] != read_ps_bank[param_name][i][1]):
                            print("{}[{}] = {} and {} : params differs.\nRetry flashing this BID!".format(param_name, i, bid_ps_bank[param_name][i][0], read_ps_bank[param_name][i][0]))

                if (psinfo[ps][0].lower() != "fbp-dclink"):
                    drs.load_dsp_modules_eeprom(type_memory=args.type_mem)
                    read_dsp_bank = drs.get_dsp_modules_bank(print_modules=False)
                    for param_name in bid_dsp_bank.keys():
                        if(bid_dsp_bank[param_name] != read_dsp_bank[param_name]):
                            print("{}\n{}\n{}\nparams differs.\nRetry flashing this BID!".format(param_name, bid_dsp_bank[param_name]['coeffs'][0], read_dsp_bank[param_name]['coeffs'][0]))

            else:
                print("Not updating.\n\n\n")
