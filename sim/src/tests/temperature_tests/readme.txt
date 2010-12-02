001_two_methanes_9A_apart_vdw_5.mmp

-Two CH4 molecules , 9.08 Angstrom apart (distance between Carbon centers) 
- Their vdw distance is 5.4 A
- Simulate this file for ~ 4 picoseconds at 0 K
- see the temperature reading


002_two_methanes_10A_apart_vdw_6.mmp

-Two Ch4 molecules ,10.06 Angstrom apart (distance between Carbon centers) 
- Their vdw distance is 6.38 A
- Simulate this file for ~ 4 picoseconds at 0 K
- see the temperature reading

003_thermostat_test.mmp  (003 1 to 5)
003-1:
- 2 thermostats attached to the same chunk
- First one will set temperature to 10K during a simulation run and the other at 500 K 
- Thermostat#2 is disabled 
- It is expected that the temperature plot will show temperatures around 10 K 
- Run this simulation at 1000 K 
003-2 to 003-5: 
- Other thermostat tests with various temperatures