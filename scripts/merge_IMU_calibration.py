#!/usr/bin/python

#   Copyright (c) 2016 AIT, ETH Zurich. All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in
#    the documentation and/or other materials provided with the
#    distribution.
# 3. Neither the name AIT nor the names of its contributors may be
#    used to endorse or promote products derived from this software
#    without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS
# OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED
# AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
# File: merge_IMU_calibration.py
# Created on: 09.03.16
# Author: Nicolas de Palezieux

from __future__ import print_function, division
import yaml
import sys
import rospkg
import os

__author__ = 'nicolas'

if __name__ == "__main__":
    # select device
    if len(sys.argv) < 2:
        print('No device serial nr provided at the command line.')
        rospack = rospkg.RosPack()
        duo_path = rospack.get_path('duo3d_ros')

        devices = os.listdir(os.path.join(duo_path, 'calib'))

        devices = [device for device in devices if os.path.isdir(os.path.join(duo_path, 'calib', device))]

        if len(devices) == 1:
            print('Found one device: {}. Using that one.'.format(devices[0]))
            device_serial_nr = devices[0]

        else:

            print('Found the following devices:')

            for i, device in enumerate(devices):
                print('{}: {}'.format(i+1, device))

            selection = int(raw_input('Select the device you want by providing the appropriate number: '))

            if selection < 1 or selection > len(devices):
                raise Exception('The provided number {} is not in the valid range [{}:{}]'.format(selection, 1, len(devices)))

            device_serial_nr = devices[selection-1]

    else:
        device_serial_nr = sys.argv[1]

    if not os.path.isfile(os.path.join(duo_path, 'calib', device_serial_nr, 'last_bias_estimate.yaml')):
        raise Exception('There is no last_bias_estimate.yaml for the selected device')

    # select lens
    lenses = os.listdir(os.path.join(duo_path, 'calib', device_serial_nr))
    lenses = [lens for lens in lenses if os.path.isdir(os.path.join(duo_path, 'calib', device_serial_nr, lens))]

    if len(lenses) == 1:
        print('Found one lens: {}. Using that one.'.format(lenses[0]))
        lens = lenses[0]
    else:
        print('Found several lenses:')
        for i, lens in enumerate(lenses):
            print('{}: {}'.format(i+1, lens))
        selection = int(raw_input('Select the lens you want by providing the appropriate number: '))
        if selection < 1 or selection > len(lenses):
            raise Exception('The provided number {} is not in the valid range [{}:{}]'.format(selection, 1, len(lenses)))
        lens = lenses[selection-1]

    # select resolution
    resolutions = os.listdir(os.path.join(duo_path, 'calib', device_serial_nr, lens))
    resolutions = [resolution for resolution in resolutions if os.path.isdir(os.path.join(duo_path, 'calib', device_serial_nr, lens, resolution))]

    if len(resolutions) == 1:
        print('Found one resolution: {}. Using that one.'.format(resolutions[0]))
        resolution = resolutions[0]
    else:
        print('Found several resolutions:')
        for i, resolution in enumerate(resolutions):
            print('{}: {}'.format(i+1, resolution))
        selection = int(raw_input('Select the resolution you want by providing the appropriate number: '))
        if selection < 1 or selection > len(resolutions):
            raise Exception('The provided number {} is not in the valid range [{}:{}]'.format(selection, 1, len(resolutions)))
        resolution = resolutions[selection-1]

    # load the yaml files
    with open(os.path.join(duo_path, 'calib', device_serial_nr, 'last_bias_estimate.yaml'), 'r') as infile:
        last_bias_estimate = yaml.load(infile)

    with open(os.path.join(duo_path, 'calib', device_serial_nr, lens, resolution, 'cameraParams.yaml'), 'r') as infile:
        cameraParams = yaml.load(infile)

    print('For each axis of the accelerometer and gyroscope you can decide to use the new estimate (answer y), keep the old one (answer n) or manually provide your own (answer m).')

    print('Accelerometer biases:')
    print('Old       \tNew')
    print('{0: 6.6f}\t{1: 6.6f}'.format(cameraParams['acc_bias'][0][0], last_bias_estimate['acc_bias'][0]))
    print('{0: 6.6f}\t{1: 6.6f}'.format(cameraParams['acc_bias'][1][0], last_bias_estimate['acc_bias'][1]))
    print('{0: 6.6f}\t{1: 6.6f}'.format(cameraParams['acc_bias'][2][0], last_bias_estimate['acc_bias'][2]))

    axes = 'XYZ'
    for i in range(3):
        selection = raw_input('Do you want to use the new accelerometer {} axis estimate? [Y/n/m]: '.format(axes[i]))
        if not selection or selection == 'y' or selection == 'Y':
            cameraParams['acc_bias'][i][0] = last_bias_estimate['acc_bias'][i]
        elif selection == 'o':
            cameraParams['acc_bias'][i][0] = float(raw_input('Enter a bias value for the accelerometer {} axis: '.format(axes[i])))

    print('Gyroscope biases:')
    print('Old       \tNew')
    print('{0: 6.6f}\t{1: 6.6f}'.format(cameraParams['gyro_bias'][0][0], last_bias_estimate['gyro_bias'][0]))
    print('{0: 6.6f}\t{1: 6.6f}'.format(cameraParams['gyro_bias'][1][0], last_bias_estimate['gyro_bias'][1]))
    print('{0: 6.6f}\t{1: 6.6f}'.format(cameraParams['gyro_bias'][2][0], last_bias_estimate['gyro_bias'][2]))

    axes = 'XYZ'
    for i in range(3):
        selection = raw_input('Do you want to use the new gyroscope {} axis estimate? [Y/n/m]: '.format(axes[i]))
        if not selection or selection == 'y' or selection == 'Y':
            cameraParams['gyro_bias'][i][0] = last_bias_estimate['gyro_bias'][i]
        elif selection == 'o':
            cameraParams['gyro_bias'][i][0] = float(raw_input('Enter a bias value for the gyroscope {} axis: '.format(axes[i])))

    with open(os.path.join(duo_path, 'calib', device_serial_nr, lens, resolution, 'cameraParams.yaml'), 'w') as outfile:
        outfile.write(yaml.dump(cameraParams, default_flow_style=None))
