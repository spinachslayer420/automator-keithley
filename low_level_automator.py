import pyvisa as vi
import pyvisa_sim
import numpy as np
import time

instr_di = {}
rm = vi.resourceManager()

def list_instruments(unused=False):
    if(unused):
        print('all addresses: ' + str(rm.list_resources()))
    print('in use: ')
    print(i + ' ' + instr_di[i] for i in instr_di.keys())

def add_instrument(addr,name,baud=9600):
    try:
        instr_di[name] += rm.add_instrument(addr)
        instr_di[name].baud_rate = baud
        print(instr_di[name].query('*IDN?'))
    except:
        print('Instrument does not exist.')
        return False

def send_instructions(instrument,inst='',file=None):
    if(file):
        try:
            fh = open(file,'r')
        except:
            return 'File could not be opened.'
        instrument.write(fh.read())
    else:
        instrument.write(inst)

#simple sweep system
def sweep_send(instrument,data_range,wait,inst_l = ['reset()','set_integration_time(smua,0.001)','set_integration_time(smub,0.001)'],preload_lines=3):
    #col 0,1,2,3 are smua v/i then smub v/i, additional params like t_int and delay and stop v can be set further down
    for u in range(preload_lines):
        send_instructions(instrument,inst_l[u])
    for u in range(np.shape(data_range)[1]):
        for w in inst_l[preload_lines:]:
            t_inst=(w.replace('$smua.v',str(data_range[0,u]))).replace('$smua.i',str(data_range[1,u]))
            t_inst=(w.replace('$smub.v',str(data_range[2,u]))).replace('$smub.i',str(data_range[3,u]))
            send_instructions(instrument,t_inst)
        time.sleep(wait)

'''
EXAMPLES OF TSP COMMANDS
Standard IV Curve for Photodiode
reset()
smua.source.output = smua.OUTPUT_ON
smub.source.output = smub.OUTPUT_ON
drange = np.arange(st,stop,(st-stop)/steps)
smua.source.levelv = 0.0
for u in drange:
    smua.measure.v(smua.nvbuffer1)
    smua.measure.i(smua.nvbuffer1)
    smub.source.levelv(u)
    smub.measure.v(smub.nvbuffer1)
    smub.measure.i(smub.nvbuffer1)
    delay(wait_t)
data_a = read_buffer(smua.nvbuffer1)

one can also use the high level commands, can be used with sweep_send to loop multiple measurements:
voltage_sweep_dual_smu(smu1=smua,smu2=smub,
    smu1.sweeplist=np.zeros(10000),smu2.sweeplist=np.arange($smub.v,$smua.v),t_int=$t_int,delay,pulsed=False)

COMMUNICATING WITH SIGNAL GENERATOR AND OSC

Unlike the TSP capable mechanism, you need to send SCPI commands to the signal generator and oscilloscope.
EX (typical TREL parameters)
instrument.write('C2:BSWV WVTP,SQUARE,FRQ,2941.17647,AMP,1.5,OFST,1.5')
instrument.write('C1:BSWV WVTP,PULSE,FRQ,2941.17647,AMP,1.5,OFST,1.5')
instrument.write('C1:OUTP ON')
instrument.write('C2:OUTP ON')
time.sleep(60) #acquisition time to completion on nanolog

'''