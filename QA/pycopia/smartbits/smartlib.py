#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
# vim:ts=4:sw=4:softtabstop=4:smarttab:expandtab

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#    http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
This is a high-level object interface the the Smartbits test system. It
also imports all of the low-level API calls. These low-level wrapper
classes are automatically generated by SWIG. You must first install the
smartbitsmodule in order for this to work. The SWIG program wraps the the
smartlib C API and this smartbits package makes it available to the Python
programmer. This module also defines some utility functions.

"""

from pycopia.smartbits.SMARTBITS import *
from pycopia.smartbits.smartbits_struct import *
from pycopia.smartbits.smartbits_func import *

SmartlibError = smartbits_funcc.SmartlibError

class SmartbitsError(SmartlibError):
    pass

# you can subclass smartlib structures and add methods!
class HTCount(HTCountStructure):
    pass


# some helpful functions follow, borrowed from Smartlib sample C code.
def linkToSmartBits(ipaddr=None, port=16385):
    # ETGetLinkStatus will be positive if we're linked
    try:
        st = ETGetLinkStatus()
    except SmartlibError, err:
        if not ipaddr:
            ipaddr = raw_input ("Enter IP address of SmartBits chassis ==> ")
        try:
            NSSocketLink(ipaddr,port,RESERVE_NONE)
        except SmartlibError, err:
            print_error_desc(err)
            raise SmartbitsError, err[0]


def resetCard(hub, slot, port):
    """
    HTResetPort resets card to power on defaults
    """
    HTResetPort(RESET_FULL, hub, slot, port)

def setFill(hub, slot, port, fill_len):
    """
    setFill(hub, slot, port, fill_len)
    Sets the backgound fill pattern.  The first 6 bytes are set to 0xFF
    to create a broadcast packet.  The rest of the packet is filled with 0xAA.
    """
    fillData = "\xFF" * 6 + "\xAA" * fill_len
    HTFillPattern( len(fillData), fillData, hub, slot, port)


def setVFD1(h1, s1, p1):
    """
    Sets up VFD1 to overwrite the source MAC area of the packet
    VFD 1 and 2 work like counters, will overwrite 1 to 6 bytes
    and can be set static, increment or decrement.
    Since we have set the fill to have FF FF FF FF FF FF in the first
    six bytes and this VFD has an offset of 48 bits it will overwrite the
    next six bytes with 66 55 44 33 22 11

    """
    vfdstruct = HTVFDStructure()
    # MAC will increment with each successive packet
    vfdstruct.Configuration = HVFD_INCR
    # will overwrite 6 bytes
    vfdstruct.Range = 6
    # 48 bits (6 bytes) after preamble - SOURCE MAC
    vfdstruct.Offset = 48
    # order is 0 = LSB - will produce a MAC address 66 55 44 33 22 11
# XXX current interface uses pointers
    vfdData = ptrcreate("int",0,6)
    ptrset(vfdData, 0x11, 0)
    ptrset(vfdData, 0x22, 1)
    ptrset(vfdData, 0x33, 2)
    ptrset(vfdData, 0x44, 3)
    ptrset(vfdData, 0x55, 4)
    ptrset(vfdData, 0x66, 5)
    # Associate the data with the VFD structure
    vfdstruct.Data = vfdData
    # will increment 5 times then repeat LSB of Source MAC will
    # follow 11 12 13 14 15 11 12 pattern
    vfdstruct.DataCount = 5
    # send to config card
    HTVFD( HVFD_1, vfdstruct, h1, s1, p1)
    ptrfree(vfdData)



def setTrigger(h1, s1, p1):
    """
setTrigger
    Sets a trigger to match the base source MAC address.  Since we have a
    cycle count of five on the VFD1 we are triggering on, our trigger will fire
    every fifth packet.
    """
    MyTrigger = HTTriggerStructure()
    #  start 48 bits after preamble (SOURCE MAC)
    MyTrigger.Offset = 48
    #  trigger pattern is 6 bytes long
    MyTrigger.Range = 6
    #  data to match is 66 55 44 33 22 11
# XXX future interface, use typemaps to allow python list assignment to
# memeber arrays.
    MyTrigger.Pattern = [0x11, 0x22, 0x33, 0x44, 0x55, 0x66]
    #  send config to card
    HTTrigger( HTTRIGGER_1, HTTRIGGER_ON, MyTrigger, h1, s1, p1)



def clearCounters(h1, s1, p1):
    """
clearCounters
    zero out the counters on the target Hub Slot Port
    """
    HTClearPort( h1, s1, p1)


def sendPackets(h1, s1, p1):
    """
sendPackets
    HTRun will control transmission state of the card - with HTRUN mode it
    will start transmitting, with HTSTOP it will stop transmitting.
    A one second delay ensures the card has started transmitting, a while
    loop checks to ensure the card has stopped transmitting before exiting.
    The final 1 second wait allows time for the packets to get to the receive card.
    """
    # Start transmission - card will transmit at whatever mode it is set to
    HTRun( HTRUN, h1, s1, p1)
    cs = HTCountStructure()
    # Library 3.09 and higher includes delay function
    NSDelay(1)
    # Now wait until transmission stops
    HTGetCounters( cs, h1, s1, p1)
    while cs.TmtPktRate != 0:
        HTGetCounters( cs, h1, s1, p1)
        NSDelay(1)


def promptForEnter():
    """
promptForEnter
    Press Enter to continue procedure
    waits until user presses ENTER
    """
    raw_input("Press ENTER to continue.")


def showCounters(h1, s1, p1):
    """
showCounters
    Display counts on target card.  HTClearPort will clear couts
    Card counter alwasy run.  There is no Start command for counters.
    Each element has a corresponding Rate (ie TmtPktRate RcvPktRate etc.
    Thses counts will display the packets per second counts while the card
    is transmitting.
    """
    cs = HTCount()
    HTGetCounters( cs, h1, s1, p1)
    print "========================================="
    print "Counter Data Card", (s1 + 1)
    print "========================================="
    print " Transmitted Pkts  " , cs.TmtPkt
    print " Received Pkts     " , cs.RcvPkt
    print " Collisions        " , cs.Collision
    print " Received Triggers " , cs.RcvPkt
    print " CRC Errors        " , cs.CRC
    print " Alignment Errors  " , cs.Align
    print " Oversize Pkts     " , cs.Oversize
    print " Undersize Pkts    " , cs.Undersize
    print "========================================="

    promptForEnter()


def unlink():
    ETUnLink()

####################################################################
# module self test. This is a translation from the 1stTest.c sample
# program.
if __name__ == "__main__":
    import sys

    hub1 = 0
    slot1 = 0
    port1 = 0
    hub2 = 0
    slot2 = 1
    port2 = 0
    numPackets = 100000

    if len(sys.argv) > 1:
        ipaddr = sys.argv[1]
    else:
        ipaddr = raw_input("Enter IP address of SmartBits chassis ==> ")
    try:
        ETSocketLink(ipaddr, 16385)
    except Exception, err:
        print "Error linking to chassis:", err
        sys.exit()
    print "successfully linked"

# reset cards
    HTResetPort(RESET_FULL, hub1, slot1, port1)
    HTResetPort(RESET_FULL, hub2, slot2, port2)

# clear counters
    HTClearPort(hub1, slot1, port1)
    HTClearPort(hub2, slot2, port2)

# set transmission parameters, single burst of numPackets packets
    HTTransmitMode(SINGLE_BURST_MODE,hub1,slot1,port1)
    HTBurstCount(numPackets,hub1,slot1,port1)

# start transmitting from the first card
    HTRun(HTRUN,hub1,slot1,port1)

# you could need a delay here before reading counter data
    raw_input("Press ENTER key to get counts.")

# get the transmit counts from card1 then the receive counts from card2
    cs = HTCountStructure()
    HTGetCounters(cs, hub1, slot1, port1)
    txPackets = cs.TmtPkt
    HTGetCounters(cs, hub2, slot2, port2)
    rxPackets = cs.RcvPkt
    if txPackets == rxPackets:
       print "Test Passed! %d packets transmitted and %d packets received." % (txPackets, rxPackets)
    else:
       print "Test Failed! %d packets transmitted and %d packets received." % (txPackets, rxPackets)

    ETUnLink()

