import smbus2
import time
import math

bus=smbus2.SMBus(1)
bus.write_i2c_block_data(0x68,0b10001000,[0x00])
time.sleep(1)

data=bus.read_i2c_block_data(0x68,0x00,2)
raw=data[0]<<8 | data[1]

if raw >32767:
 raw-=65535
 
vol=2.048/32767
v=raw*vol
print(v,"[V]")

Rf=(v/(4.13-v))*10000.0
lnRf=Rf/10000
Temp=3380/(math.log(lnRf)+3380/298.16)-273.16
print(Temp,"[C]")
