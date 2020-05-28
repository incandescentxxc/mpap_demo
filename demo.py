# The script is to transfer the video to another computer using ffmpeg with different network status
# Parameters needed to be finely-tuned
import os
import sys
import subprocess
import time
import csv
from threading import Timer
import _thread

"""
mode is used to select protocol
loss_rates and delays is the parameters to be tuned (two lists)
"""


def run_stream(mode, loss_rates, delays):
    serverIP = '192.168.1.29'
    clientIP = '192.168.1.19'
    sender_NIC = 'ens33'
    target_NIC = 'ens33'
    # initialize the interface
    os.system("sudo tc qdisc del dev " + sender_NIC +
              " root netem")
    try:
        _thread.start_new_thread(transmission, (mode, serverIP))
    except:
        print("Error: unable to start thread")
        # estimate 5s transmission time, and change para every one second
    for i in range(5):
        lr_timer = Timer(10, changeLR, args=(sender_NIC, loss_rates[i], i))
        delay_timer = Timer(10, changeDelays, args=(sender_NIC, delays[i], i))
        lr_timer.start()
        delay_timer.start()
        lr_timer.join()
        delay_timer.join()


def transmission(mode, serverIP):
    print("Thread 1")
    if(mode == 0):  # udp
        outputVideoName = 'udpvideo.mp4'
        # cmd_cal_remote_server = 'ssh incandescentxxc@' + target_NIC + ' ffmpeg -i video1080p.mp4 -i '+ outputVideoName
        os.system("ffmpeg -re -i video1080p.mp4 -f h264 udp://" +
                  serverIP + ":8000")
    elif(mode == 1):  # udplite
        outputVideoName = 'udplitevideo.mp4'
        # cmd_cal_remote_server = 'ssh incandescentxxc@' + target_NIC + ' ffmpeg -i video1080p.mp4 -i '+ outputVideoName
        os.system("ffmpeg -re -i video1080p.mp4 -f h264 udplite://" +
                  serverIP + ":8000")
    elif(mode == 2):  # rtp
        outputVideoName = 'rtpvideo.mp4'
        os.system("ffmpeg -re -i video1080p.mp4 -f h264 rtp://" +
                  serverIP + ":8000")
    else:  # mpap
        outputVideoName = 'mpapvideo.mp4'
    return 0


def changeLR(sender_NIC, loss_rate, index):
    print("Thread 2")
    if(index == 0):
        os.system("sudo tc qdisc add dev " + sender_NIC +
                  " root netem loss " + str(loss_rate))
    else:
        os.system("sudo tc qdisc change dev " + sender_NIC +
                  " root netem loss " + str(loss_rate))
    return 0


def changeDelays(sender_NIC, delay, index):
    print("Thread 3")
    if(index == 0):
        os.system("sudo tc qdisc add dev " + sender_NIC +
					" root netem delay " + str(delay) + "ms")
    else:
        os.system("sudo tc qdisc change dev " + sender_NIC +
					" root netem delay " + str(delay) + "ms")
    return 0


if __name__ == "__main__":
    loss_rates = [1, 5, 10, 20, 50]
    delays = [10, 10, 10, 10, 10]
    run_stream(0, loss_rates, delays)
