#!/usr/bin/python3

######## Chaos synchronization experiment ################
# Ruslans Babajans, Arturs Aboltins
# Institute of Radioelectronics
# Riga Technical University
# 2020
# The following program is for driving two Analod Discovery-2 (AD2) devices. The purpose is to record chaotic signals
# of two chaos oscillators at the start of synchronization.
# Program:
#	1)Generate info noise on AD2-A;
# 	2)Generate synchro noise on AD2-B;
#	3)Turn on power voltage for synchro circuit (AD2-A);
#	4)Recor and save samples:
#		AD2-A - info signal_master, info signal_slave;
#		AD2-B - info noise (later to be summed in MATLAB)
# Note - program connects to specific AD2 devices by using their serial numbers stored as variables.

from dwfconstants import *
import time
import sys
import matplotlib.pyplot as plt
import numpy as np
import csv

# Parameters of the experiment
SNR = [20, 15, 10, 5, 0]  # Signal-2-noise ratios (SNR) for the experiment in dB
# Amplitude_info_noise = [0.078, 0.150, 0.274, 0.493, 0.877]  # Amplitude of the noise signal for required SNR
Amplitude_info_noise = [1.5, 2.5, 3.5, 4.5, 5.5]  # Amplitude of the noise signal for required SNR
# Amplitude_synchro_noise = [0.000, 0.016, 0.050, 0.087, 0.180]  # Amplitude of the noise signal for required SNR
Amplitude_synchro_noise = [5.000, 4.000, 3.000, 2.000, 1.000]  # Amplitude of the noise signal for required SNR

# Serial numbers of the used devices
AD2_A = 'b\'SN:210321A962FA\''  # Change if device with different serial number is used
AD2_B = 'b\'SN:210321ABE78C\''  # Change if device with different serial number is used

# Device handlers and variables
hdwf_A = c_int()  # AD2-A handler
hdwf_B = c_int()  # AD2-B handler
sts_A = c_byte()  # Variable for oscilloscope acquisition on AD2-A
sts_B = c_byte()  # Variable for oscilloscope acquisition on AD2-B
W1 = c_int(0)  # Arbitrary waveform generator (AWG) Channel 1 (W1)
W2 = c_int(1)  # Arbitrary waveform generator (AWG) Channel 2 (W2)
device_id_A = c_int()  # The ID of a discovered AD2-A device
device_id_B = c_int()  # The ID of a discovered AD2-B device
cDevice = c_int()  # Stores the number of discovered AD2 devices

# Declare string variables
devicename = create_string_buffer(64)  # Character array to store the name of enumerated devices
serialnum = create_string_buffer(16)  # Character array to store the serial number of enumerated devices

# Custom waveform generator variables
hzFreq = 610.351563  # Parameter taken from the signal import window for the noise signals
cSamples_gen = 2 * 16384  # Number of samples for AWG

hzFreq_info = 106667/cSamples_gen #110e3/cSamples_gen  # Parameter taken from the signal import window for the info signals (3.356933593750000 Hz)

# Acquisition variables
fAcq = 2e6  # Sample frequency for analog input channels in Hz
tAcq = 0.30  # Signal acquisition time in sec. Aimed at 1000 bits with 300 us bit length
hzAcq = c_double(fAcq)
nSamples = int(tAcq * fAcq)  # Number of samples for signal acquisition
rgdSamples_chaos_info_signal_master = (c_double * nSamples)()  # Create a buffer array of c_doubles with size nSamples
rgdSamples_chaos_noise_signal_master = (c_double * nSamples)()  # Create a buffer array of c_doubles with size nSamples
rgdSamples_chaos_info_signal_slave = (c_double * nSamples)()  # Create a buffer array of c_doubles with size nSamples

# Scope acquisition variables
cAvailable_A = c_int()
cLost_A = c_int()
cCorrupted_A = c_int()

cAvailable_B = c_int()
cLost_B = c_int()
cCorrupted_B = c_int()

fLost_A = 0
fCorrupted_A = 0
cSamples_A = 0

fLost_B = 0
fCorrupted_B = 0
cSamples_B = 0
#####################################################################################
    # Import noise signal .csv files and convert them to c_double
with open('RC1_synchro_noise_samples.csv', newline='') as File:
    txtlist = [j for sub in csv.reader(File) for j in sub]
    fa = list(map(float, txtlist))
    genSamples_synchro_noise = (c_double * len(fa))(*fa)

with open('RC1_info_noise_samples.csv', newline='') as File:
    txtlist = [j for sub in csv.reader(File) for j in sub]
    fa = list(map(float, txtlist))
    genSamples_info_noise = (c_double * len(fa))(*fa)

with open('RC1_info_dignal_999_SNR_1.csv', newline='') as File:
    txtlist = [j for sub in csv.reader(File) for j in sub]
    fa = list(map(float, txtlist))
    genSamples_info_signal = (c_double * len(fa))(*fa)
#####################################################################################
# Load dwf library (contain functions to interact with AD2)
if sys.platform.startswith("win"):
    dwf = cdll.dwf
elif sys.platform.startswith("darwin"):
    dwf = cdll.LoadLibrary("/Library/Frameworks/dwf.framework/dwf")
else:
    dwf = cdll.LoadLibrary("libdwf.so")

version = create_string_buffer(16)
dwf.FDwfGetVersion(version)
print("DWF Version: " + str(version.value))
dwf.FDwfParamSet(DwfParamOnClose, c_int(1))  # 0 = run, 1 = stop, 2 = shutdown
#####################################################################################
# Enumerate and print device information
dwf.FDwfEnum(c_int(3), byref(cDevice))  # Enumerate AD2 devices
print("Number of Devices: " + str(cDevice.value))

for iDev in range(0, cDevice.value):
    dwf.FDwfEnumDeviceName(c_int(iDev), devicename)
    dwf.FDwfEnumSN(c_int(iDev), serialnum)
    print("------------------------------")
    print("Device " + str(iDev) + " : ")
    print("\tName:\'" + str(devicename.value) + "' " + str(serialnum.value))
print("------------------------------")
#####################################################################################
# Distinguish which device is AD2_A and AD2_B. Get handlers for both devices.
for iDev in range(0, cDevice.value):
    dwf.FDwfEnumSN(c_int(iDev), serialnum)
    deviceserialnum_string = str(serialnum.value)

    if deviceserialnum_string == AD2_A:
        device_id_A = iDev
        print("------------------------------")
        print("Opening AD2_A : " + deviceserialnum_string + ". Device ID: " + str(device_id_A))
        dwf.FDwfDeviceOpen(c_int(device_id_A), byref(hdwf_A))

    if deviceserialnum_string == AD2_B:
        device_id_B = iDev
        print("------------------------------")
        print("Opening AD2_B : " + deviceserialnum_string + ". Device ID: " + str(device_id_B))
        dwf.FDwfDeviceOpen(c_int(device_id_B), byref(hdwf_B))
print("------------------------------")

if hdwf_A.value == 0:
    print("Failed to open device AD2-A")
    szerr = create_string_buffer(512)
    dwf.FDwfGetLastErrorMsg(szerr)
    print(str(szerr.value))
else:
    print("Connected to AD2-A")
    print("------------------------------")
if hdwf_B.value == 0:
    print("Failed to open device AD2-B")
    szerr = create_string_buffer(512)
    dwf.FDwfGetLastErrorMsg(szerr)
    print(str(szerr.value))
else:
    print("Connected to AD2-B")
    print("------------------------------")
#####################################################################################
# Run the measurements part for every SNR level
for a in range(len(SNR)):
    if hdwf_A.value != 0 and hdwf_B.value != 0:
        print("======================================")
        print("ITERRATION: " + str(a+1) + ", SNR= " + str(SNR[a]) + " dB")
        print("======================================")
        #####################################################################################
        # Set up acquisition
        dwf.FDwfAnalogInChannelEnableSet(hdwf_A, c_int(0), c_bool(True))
        dwf.FDwfAnalogInChannelRangeSet(hdwf_A, c_int(0), c_double(8)) # Set to 2 V for RC1
        dwf.FDwfAnalogInAcquisitionModeSet(hdwf_A, acqmodeRecord)
        dwf.FDwfAnalogInFrequencySet(hdwf_A, hzAcq)
        dwf.FDwfAnalogInRecordLengthSet(hdwf_A, c_double(tAcq))  # Set record length

        dwf.FDwfAnalogInChannelEnableSet(hdwf_B, c_int(0), c_bool(True))
        dwf.FDwfAnalogInChannelRangeSet(hdwf_B, c_int(0), c_double(8)) # Set to 2 V for RC1
        dwf.FDwfAnalogInAcquisitionModeSet(hdwf_B, acqmodeRecord)
        dwf.FDwfAnalogInFrequencySet(hdwf_B, hzAcq)
        dwf.FDwfAnalogInRecordLengthSet(hdwf_B, c_double(tAcq))  # Set record length
        #####################################################################################
        # Generate info noise on AD2-A
        print("Generating info noise...")
        print("------------------------------")
        dwf.FDwfAnalogOutNodeEnableSet(hdwf_A, W1, AnalogOutNodeCarrier, c_bool(True))
        dwf.FDwfAnalogOutNodeFunctionSet(hdwf_A, W1, AnalogOutNodeCarrier, funcCustom)
        dwf.FDwfAnalogOutNodeDataSet(hdwf_A, W1, AnalogOutNodeCarrier, genSamples_info_noise, c_int(cSamples_gen))
        dwf.FDwfAnalogOutNodeFrequencySet(hdwf_A, W1, AnalogOutNodeCarrier, c_double(hzFreq))
        dwf.FDwfAnalogOutNodeAmplitudeSet(hdwf_A, W1, AnalogOutNodeCarrier, c_double(Amplitude_info_noise[a]))

        dwf.FDwfAnalogOutConfigure(hdwf_A, W1, c_bool(True))
        print("Info noise generated and running.")
        print("------------------------------")
        #####################################################################################
        # Generate synchro noise on AD2-B
        print("Generating synchro noise...")
        print("------------------------------")
        dwf.FDwfAnalogOutNodeEnableSet(hdwf_B, W1, AnalogOutNodeCarrier, c_bool(True))
        dwf.FDwfAnalogOutNodeFunctionSet(hdwf_B, W1, AnalogOutNodeCarrier, funcCustom)
        dwf.FDwfAnalogOutNodeDataSet(hdwf_B, W1, AnalogOutNodeCarrier, genSamples_synchro_noise,
                                     c_int(cSamples_gen))
        dwf.FDwfAnalogOutNodeFrequencySet(hdwf_B, W1, AnalogOutNodeCarrier, c_double(hzFreq))
        dwf.FDwfAnalogOutNodeAmplitudeSet(hdwf_B, W1, AnalogOutNodeCarrier, c_double(Amplitude_synchro_noise[a]))
        dwf.FDwfAnalogOutConfigure(hdwf_B, W1, c_bool(True))
        print("Synchro noise generated and running.")
        print("------------------------------")
        #####################################################################################
        # Apply voltage to synchronization circuit by AD2-A
        print("Turning the synchronization circuit ON...")
        print("------------------------------")
        dwf.FDwfAnalogIOChannelNodeSet(hdwf_A, c_int(0), c_int(0), c_double(True))  # Enable positive supply
        dwf.FDwfAnalogIOChannelNodeSet(hdwf_A, c_int(0), c_int(1), c_double(5.0))  # Set voltage to 5 V
        dwf.FDwfAnalogIOChannelNodeSet(hdwf_A, c_int(1), c_int(0), c_double(True))  # Enable negative supply
        dwf.FDwfAnalogIOChannelNodeSet(hdwf_A, c_int(1), c_int(1), c_double(-5.0))  # Set voltage to -5 V
        dwf.FDwfAnalogIOEnableSet(hdwf_A, c_int(True))  # Master enable
        print("Synchronization circuit is ON.")
        print("------------------------------")
        #####################################################################################
        # Generate info SIGNAL on AD2-A
        print("Running info signal...")
        print("------------------------------")
        # dwf.FDwfAnalogOutNodeEnableSet(hdwf_A, W2, AnalogOutNodeCarrier, c_bool(True))
        dwf.FDwfAnalogOutNodeFunctionSet(hdwf_A, W2, AnalogOutNodeCarrier, funcCustom)
        dwf.FDwfAnalogOutNodeDataSet(hdwf_A, W2, AnalogOutNodeCarrier, genSamples_info_signal,
                                     c_int(cSamples_gen))
        dwf.FDwfAnalogOutNodeFrequencySet(hdwf_A, W2, AnalogOutNodeCarrier, c_double(hzFreq_info))
        # FDwfAnalogOutNodeOffsetSet(hdwf_A, W2, AnalogOutNodeCarrier, c_double(0)
        dwf.FDwfAnalogOutNodeAmplitudeSet(hdwf_A, W2, AnalogOutNodeCarrier, c_double(5))
        # dwf.FDwfAnalogOutNodeAmplitudeSet(hdwf_A, W2, AnalogOutNodeCarrier, c_double(0))






        dwf.FDwfAnalogOutNodeEnableSet(hdwf_A, W2, AnalogOutNodeCarrier, c_bool(True))
        dwf.FDwfAnalogOutConfigure(hdwf_A, W2, c_bool(True))
        #####################################################################################
        # Acquire scope data
        # wait at least 2 seconds for the offset to stabilize
        # time.sleep(2)
        print("Starting oscilloscope acquisition...")
        print("------------------------------")

        # fLost_A = 0
        # fCorrupted_A = 0
        # cSamples_A = 0
        #
        # fLost_B = 0
        # fCorrupted_B = 0
        # cSamples_B = 0

        dwf.FDwfAnalogInConfigure(hdwf_A, c_int(0), c_int(1))
        dwf.FDwfAnalogInConfigure(hdwf_B, c_int(0), c_int(1))

        while cSamples_A < nSamples and cSamples_B < nSamples:

            dwf.FDwfAnalogInStatus(hdwf_A, c_int(1), byref(sts_A))
            if cSamples_A == 0 and (sts_A == DwfStateConfig or sts_A == DwfStatePrefill or sts_A == DwfStateArmed):
                # Acquisition not yet started.
                continue

            dwf.FDwfAnalogInStatus(hdwf_B, c_int(1), byref(sts_B))
            if cSamples_B == 0 and (sts_B == DwfStateConfig or sts_B == DwfStatePrefill or sts_B == DwfStateArmed):
                # Acquisition not yet started.
                continue

            dwf.FDwfAnalogInStatusRecord(hdwf_A, byref(cAvailable_A), byref(cLost_A), byref(cCorrupted_A))
            dwf.FDwfAnalogInStatusRecord(hdwf_B, byref(cAvailable_B), byref(cLost_B), byref(cCorrupted_B))
            cSamples_A += cLost_A.value
            cSamples_B += cLost_B.value

            if cLost_A.value:
                fLost_A = 1

            if cLost_B.value:
                fLost_B = 1

            if cCorrupted_A.value:
                fCorrupted_A = 1

            if cCorrupted_B.value:
                fCorrupted_B = 1

            if cAvailable_A.value == 0:
                continue

            if cAvailable_B.value == 0:
                continue

            if cSamples_A + cAvailable_A.value > nSamples:
                cAvailable_A = c_int(nSamples - cSamples_A)

            if cSamples_B + cAvailable_B.value > nSamples:
                cAvailable_B = c_int(nSamples - cSamples_B)

            dwf.FDwfAnalogInStatusData(hdwf_A, c_int(0),
                                       byref(rgdSamples_chaos_info_signal_master, sizeof(c_double) * cSamples_A),
                                       cAvailable_A)  # get AD2-A channel 1 data
            dwf.FDwfAnalogInStatusData(hdwf_A, c_int(1),
                                       byref(rgdSamples_chaos_info_signal_slave, sizeof(c_double) * cSamples_A),
                                       cAvailable_A)  # get AD2-A channel 2 data
            dwf.FDwfAnalogInStatusData(hdwf_B, c_int(0),
                                       byref(rgdSamples_chaos_noise_signal_master, sizeof(c_double) * cSamples_B),
                                       cAvailable_B)  # get AD2-B channel 1 data

            cSamples_A += cAvailable_A.value
            cSamples_B += cAvailable_B.value

        print("Data acquisition is done.")
        print("------------------------------")
        #####################################################################################
        # Saving to file
        print("Saving data to .csv files...")
        print("------------------------------")

        f = open("Chaos_info_signal_master_" + str(SNR[a]) + "_SNR.csv", "w")  # From AD2-A
        for v in rgdSamples_chaos_info_signal_master:
            f.write("%s\n" % v)
        f.close()

        f = open("Chaos_noise_signal_master_" + str(SNR[a]) + "_SNR.csv", "w") # From AD2-B
        for v in rgdSamples_chaos_noise_signal_master:
            f.write("%s\n" % v)
        f.close()

        f = open("Chaos_info_signal_slave_" + str(SNR[a]) + "_SNR.csv", "w") # From AD2-A
        for v in rgdSamples_chaos_info_signal_slave:
            f.write("%s\n" % v)
        f.close()

        print("Measurement results saved to .csv files.")
        print("------------------------------")

        fLost_A = 0
        fCorrupted_A = 0
        cSamples_A = 0

        fLost_B = 0
        fCorrupted_B = 0
        cSamples_B = 0
        #####################################################################################
        # Turn off synchronization circuit
        print("Turning the synchronization circuit OFF...")
        print("------------------------------")
        # time.sleep(5)
        dwf.FDwfAnalogIOEnableSet(hdwf_A, c_int(False))
        dwf.FDwfAnalogOutNodeAmplitudeSet(hdwf_A, W2, AnalogOutNodeCarrier, c_double(3))
        # dwf.FDwfAnalogOutConfigure(hdwf_A, W1, c_bool(False))
        # dwf.FDwfAnalogOutConfigure(hdwf_B, W1, c_bool(False))
        print("Synchronization circuit is OFF.")
        print("------------------------------")
        time.sleep(5)  # Wait 5 sec.
#####################################################################################
# Close devices
dwf.FDwfDeviceCloseAll()
time.sleep(2)  # Wait 2 sec.
print("======================================")
print("Measurements are done!")
print("======================================")
#####################################################################################
# Plot data
plot1 = plt.figure(1)
plt.plot(np.fromiter(rgdSamples_chaos_info_signal_master, dtype=float))
plot2 = plt.figure(2)
plt.plot(np.fromiter(rgdSamples_chaos_noise_signal_master, dtype=float))
plot3 = plt.figure(3)
plt.plot(np.fromiter(rgdSamples_chaos_info_signal_slave, dtype=float))
plt.show()
