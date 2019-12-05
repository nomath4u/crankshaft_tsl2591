#!/usr/bin/python3 -u

import smbus
import os
import subprocess
from time import sleep
from python_tsl2591 import tsl2591

def get_var(varname):
    try:
        CMD = 'echo $(source /boot/crankshaft/crankshaft_env.sh; echo $%s)' % varname
        p = subprocess.Popen(CMD, stdout=subprocess.PIPE, shell=True, executable='/bin/bash')
        return int(p.stdout.readlines()[0].strip())
    except:
        CMD = 'echo $(source /opt/crankshaft/crankshaft_default_env.sh; echo $%s)' % varname
        p = subprocess.Popen(CMD, stdout=subprocess.PIPE, shell=True, executable='/bin/bash')
        return int(p.stdout.readlines()[0].strip())

# ---------------------------------
BUS = 1
TSL2591_ADDR = 0x29

daynight_gpio = get_var('DAYNIGHT_PIN')
# ---------------------------------

lastvalue = 0
tsl = tsl2591(i2c_bus=BUS, sensor_address=TSL2591_ADDR) # Initialize the connector

while True:
    full, ir = tsl.get_full_luminosity()
    lux = tsl.calculate_lux(full,ir)
    Luxrounded = round(lux,1)
    print(Luxrounded)
    if lastvalue != Luxrounded:
        #print ("Lux = {}\n".format(Luxrounded))
        os.system("echo {} > /tmp/tsl2561".format(Luxrounded))
        lastvalue = Luxrounded
        #Set display brigthness
        if Luxrounded <= get_var('LUX_LEVEL_1'):
            os.system("crankshaft brightness set " + str(get_var('DISP_BRIGHTNESS_1')) + " &")
            step = 1
        elif Luxrounded > get_var('LUX_LEVEL_1') and Luxrounded < get_var('LUX_LEVEL_2'):
            os.system("crankshaft brightness set " + str(get_var('DISP_BRIGHTNESS_2')) + " &")
            step = 2
        elif Luxrounded >= get_var('LUX_LEVEL_2') and Luxrounded < get_var('LUX_LEVEL_3'):
            os.system("crankshaft brightness set " + str(get_var('DISP_BRIGHTNESS_3')) + " &")
            step = 3
        elif Luxrounded >= get_var('LUX_LEVEL_3') and Luxrounded < get_var('LUX_LEVEL_4'):
            os.system("crankshaft brightness set " + str(get_var('DISP_BRIGHTNESS_4')) + " &")
            step = 4
        elif Luxrounded >= get_var('LUX_LEVEL_5'):
            os.system("crankshaft brightness set " + str(get_var('DISP_BRIGHTNESS_5')) + " &")
            step = 5

        if daynight_gpio == 0:
            if step <= get_var('TSL2561_DAYNIGHT_ON_STEP'):
                print("Lux = {} | ".format(Luxrounded) + "Level " + str(step) + " -> trigger night")
                os.system("touch /tmp/night_mode_enabled >/dev/null 2>&1")
            else:
                if  step > get_var('TSL2561_DAYNIGHT_ON_STEP'):
                    print("Lux = {} | ".format(Luxrounded) + "Level " + str(step) + " -> trigger day")
                    os.system("sudo rm /tmp/night_mode_enabled >/dev/null 2>&1")

    sleep (get_var('TSL2561_CHECK_INTERVAL'))
