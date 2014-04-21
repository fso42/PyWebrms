# !---------written by Felix Schueller (FSS)-----------------
# ! -INPUT:
# ! -OUTPUT:
# -DESCRIPTION: based on webrms by tim
# -TODO:
# -Last modified:  Mon Apr 21, 2014  15:22
# @author Felix Schueller
# -----------------------------------------------------------
import serial
import time
import random
import tornado.ioloop
import tornado.web
import tornado.websocket
from tornado.options import define, options, parse_command_line
import sys

class controller_data(dict):
    def __init__(self,idin):
        self['id']=idin
        self['fastest']= 0.0
        self['time']= 0.0
        self['fuel']= 100 
        self['laps']= 0
        self['prev']= 0.0

    def reset(self):
        self['fastest']= 0.0
        self['time']= 0.0
        self['fuel']= 100 
        self['laps']= 0
        self['prev']= 0.0

class setup_data():
    def __init__(self):
        self.fuelmode = 4 

def logger(driver,fuel,simulation = False):
    
    # FSS---set up last timestamp 
    last_ts = dict()
    for i in range(6):
        last_ts[i+1] = 0.0


    run = True
    while run:
        if simulation :
            # ser = open('raw_data/car1_no_fuel_min.txt')
            #ser = open('raw_data/car1_no_fuel.txt')
            # ser = open('raw_data/car2_fuel_on_over_pitlane.txt')
            ser = open('raw_data/car4_fuel_real.txt')
        else:
            ser = serial.Serial('/dev/cu.NoZAP-PL2303-000013FA', 19200, timeout=0.05)

        line_saved=0
        fuel_saved_1=0
        fuel_at_start=0

        while run:
            if not simulation:
                ser.write("\"?")
            line = ser.readline()
            if line == '':
                time.sleep(.02)
                continue
                #run = False
                #sys.exit()


            if line!=line_saved:

                ascii_string = line
                first_bit = ascii_string[1:2]
                
                # 1234567891011121314
                # :TTTTTTVVS M B B A P$
                # T = Tank Autos 1-6
                # V immer 0
                # S = 0 = rennen 
                # M = Tankmodus 0: aus, 1: normal, 2: real
                #   mit Pitlane +4
                if first_bit == ":":
                    # fuel mode
                    hex_string=ascii_string[11:12].encode('hex')[1:2]
                    # -4 removes pitlane info
                    decimal = int(hex_string,16) - 4
                    if decimal > 0 : #means fuel is used
                        # loop over all fuel bits
                        for i in range(6):
                            hex_string=ascii_string[i+2:i+3].encode('hex')[1:2]
                            decimal = int(hex_string,16)
                            
                            # if change is detected, set new fuel, 
                            if int(fuel[i+1]*15.0/100.0) != decimal:
                                print "fuel change car ",i+1,":",fuel[i+1], "->", decimal * 100./15.0
                                fuel[i+1] = decimal * 100.0/15.0
                
                if first_bit!=":":
                    # Info mode
                    ascii_string = ascii_string[4:10]

                    hex_string=ascii_string[1:2].encode("hex")[1:2]+ascii_string[0:1].encode("hex")[1:2]
                    hex_string+=ascii_string[3:4].encode("hex")[1:2]+ascii_string[2:3].encode("hex")[1:2]
                    hex_string+=ascii_string[5:6].encode("hex")[1:2]+ascii_string[4:5].encode("hex")[1:2]

                    decimal=int(hex_string, 16)
                    cc = int(first_bit)
                    
                    t_in_s =  (decimal - last_ts[cc])/1000.0
                    last_ts[cc]=decimal
                    
                    if simulation:
                        if t_in_s > 10 :
                            t_in_s = 3 

                    driver[cc].append(t_in_s)

                    print "Car:", cc, '; t:', t_in_s, ', laps:', len(driver[cc]) - 1
                    if simulation:
                        time.sleep(t_in_s)

                    datafile = open("./data/car."+str(cc)+".rnd", "a")
                    datafile.write(str(t_in_s)+ '\n')
                    datafile.close()
                line_saved=line
                time.sleep(.02)

    ser.close()


if __name__ == '__main__':
    # FSS---set up 6 driver 
    driver = dict()
    fuel = dict()
    for i in range(6):
        driver[i+1]= list() 
        driver[i+1].append(0.0)
        fuel[i+1] = 100.0

    logger(driver,fuel,True)

