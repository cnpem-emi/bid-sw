from asyncio import subprocess
import pydrs
import re
import subprocess
from xlrd import open_workbook

bid= int(input("Insira o numero da BID ou o nome do UDC "))

datafile = "Inventario.xls"
sheet = open_workbook(datafile).sheet_by_name("Inventario")

# Procurar a bid na sheet

keys = [sheet.cell(0, col_index).value for col_index in range(sheet.ncols)]

for row_index in range(1,sheet.nrows):
    if((sheet.cell(row_index,keys.index("# BID")).value == bid)):
        device_name = sheet.cell(row_index,keys.index("UDC")).value
        device_model =sheet.cell(row_index,keys.index("Modelo")).value
        ps_path = sheet.cell(row_index,keys.index("ps_parameters")).value
        dsp_path = sheet.cell(row_index,keys.index("dsp_parameters")).value
        room_name =  device_name[:5]
        print("PS path: "+ps_path)
        print("DSP path: "+dsp_path)
        print("Device name: "+device_name)
        print("Device model: "+device_model)
        print("Device room: "+room_name)

def find_dsp_file():
    if (dsp_path):
        path = 'udc-dsp-parameters-db/'+room_name+'/fbp/'+dsp_path
        file = open(path)
        line = file.readlines()
        return path

def find_ps_file():
    if(ps_path):
        path = 'udc-ps-parameters-db/'+room_name+'/fbp/'+ps_path
        file = open(path)
        line = file.readlines()
        return path

if(device_model != "FBP"):
    print("Modelo selecionado incorreto: " + device_model)

elif(device_model == "FBP"):
    print(find_ps_file())
    #drs =  pydrs.pydrs.EthDRS('10.0.6.59',5000)
    #drs.set_slave_add(4))
