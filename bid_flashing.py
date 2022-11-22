#!/usr/bin/python3
import argparse
import pydrs
import time
from xlrd import open_workbook


IP_DRS = "10.0.6.59"
PORT_DRS = 5000

FLOAT_MAX_ERROR = 1e-4 # Usually is 1.1920929e-08



def check_param_bank(csv_file, max_error, memory=1):
    drs.load_param_bank(type_memory=args.type_mem)
    read_ps_bank = drs.get_param_bank()
    csv_ps_bank = drs.read_csv_param_bank(ps_param_path)

    error_values = {}
              
    for param_name in csv_ps_bank.keys():
        if param_name == "PS_Name":
            if(csv_ps_bank[param_name] != read_ps_bank[param_name][0]):
                print("{} = {} and {} : param differs!".format(
                    param_name, 
                    csv_ps_bank[param_name], 
                    read_ps_bank[param_name],
                    )
                )
        else:
            for i in range(len(csv_ps_bank[param_name])):
                if(csv_ps_bank[param_name][i] != read_ps_bank[param_name][i]):
                    if(abs(csv_ps_bank[param_name][i] - read_ps_bank[param_name][i]) > FLOAT_MAX_ERROR):
                        print("{}[{}] = {} (CSV) and {} (DRS): params differ!".format(
                            param_name, 
                            i, 
                            csv_ps_bank[param_name][i], 
                            read_ps_bank[param_name][i],
                            )
                        )
                        error_values[param_name] = {"csv":csv_ps_bank[param_name], "read":read_ps_bank[param_name]}
    return error_values

def check_dsp_module_bank(csv_file, max_error, memory=1):
    drs.load_dsp_modules_eeprom(type_memory=memory)
    read_dsp_bank = drs.get_dsp_modules_bank()
    csv_dsp_bank = drs.read_csv_dsp_modules_bank(csv_file)

    error_values = {}

    for param_name in csv_dsp_bank.keys():
            for ninstance in range(pydrs.consts.num_dsp_modules[pydrs.consts.dsp_classes_names.index(param_name)]):
                if(csv_dsp_bank[param_name]['coeffs'][ninstance] != read_dsp_bank[param_name]['coeffs'][ninstance]):
                    for ncoeff in range(pydrs.consts.num_coeffs_dsp_modules[pydrs.consts.dsp_classes_names.index(param_name)]):
                        if(abs(csv_dsp_bank[param_name]['coeffs'][ninstance][ncoeff] - read_dsp_bank[param_name]['coeffs'][ninstance][ncoeff]) > max_error):
                            print("{}[{},{}] = {} (CSV) and {} (DRS): params differ!".format(
                                param_name, 
                                ninstance,
                                ncoeff,
                                csv_dsp_bank[param_name]['coeffs'][ninstance][ncoeff], 
                                read_dsp_bank[param_name]['coeffs'][ninstance][ncoeff],
                                )
                            )
                            error_values[param_name] = {"csv":csv_dsp_bank[param_name], "read":read_dsp_bank[param_name]}
    return error_values



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




    if((args.bid_id is not None) and (args.ps_type is not None)):
        print("Selecionar apenas a BID ou tipo de fonte!")
        exit()

    elif(args.ps_type is not None):
        psinfo = read_spreadsheet(pstype=args.ps_type)

    elif(args.bid_id is not None):
        psinfo = read_spreadsheet(bid=args.bid_id)
        
    
    drs = pydrs.EthDRS(IP_DRS, PORT_DRS)

    for addr in range(31)[1:]:
        drs.slave_addr = addr
        try:
            drs.get_ps_name()
            print("Address {} found!".format(addr))
            break
        except:
            pass


    print("UDC ARM VERSION:  ", drs.read_udc_arm_version())
    print("UDC DSP VERSION:  ", drs.read_udc_c28_version())
        
    # psinfo[udc_name] = [udc_model, ps_file, dsp_file, room_name, bid_code]
    if psinfo:
        for ps in psinfo.keys():
            ps_param_path = 'udc-ps-parameters-db/{}/{}/{}'.format(psinfo[ps][3], psinfo[ps][0].lower().replace("-","_"), psinfo[ps][1])
            dsp_param_path = 'udc-dsp-parameters-db/{}/{}/{}'.format(psinfo[ps][3], psinfo[ps][0].lower(), psinfo[ps][2])

            confirmation = input("Flash BID {} for UDC {}? (y/N): ".format(psinfo[ps][4], ps))
            if confirmation == "y" or confirmation == "Y":
                
                print("Clearing BID...")
                drs.clear_bid(password=0xCAFE)
                # ------------------------------
                # UNLOCK UDC
                # ------------------------------
                print("Unlocking UDC...")
                drs.unlock_udc(0xCAFE)


                # ------------------------------
                # FLASHING EEPROM
                # ------------------------------
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

                # ------------------------------
                # RESET UDC FOR PARAMETER LOADING
                # ------------------------------
                print("Resetting UDC and wait for startup...")
                drs.reset_udc()
                time.sleep(5)
                
                drs.slave_addr = int(bid_ps_bank['RS485_Address'][0][0])

                while(True):
                    try:
                        drs.get_ps_name()
                        print("Address after reboot {} found!".format(drs.slave_addr))
                        break
                    except:
                        print("Waiting addr {}".format(drs.slave_addr))

       


                drs.unlock_udc(0xCAFE)

                # ------------------------------
                # READINGS - PS PARAMETERS
                # ------------------------------
                
                print("\n")
                print("Loading {} into memory, reading PS parameters and comparing them to {} file".format(
                    memoryType[args.type_mem],
                    psinfo[ps][1]
                ))
                if(check_param_bank(ps_param_path, FLOAT_MAX_ERROR, memory=args.type_mem)):
                    print("OOOOOOOOOPS !")
                else:
                    print("PS PARAMETERS: DONE!")
                
                # ------------------------------
                # READINGS - DSP PARAMETERS
                # ------------------------------
                if (psinfo[ps][0].lower() != "fbp-dclink"):
                    print("Loading {} into memory, reading DSP parameters and comparing them to {} file".format(
                    memoryType[args.type_mem],
                    psinfo[ps][2]
                ))
                    if(check_dsp_module_bank(dsp_param_path, FLOAT_MAX_ERROR, memory=args.type_mem)):
                        print("OOOOOOOOOPS !")
                    else:
                        print("DSP PARAMETERS: DONE!")

            else:
                print("Not updating.\n\n")

            
