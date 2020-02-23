#!/usr/bin/env python
# coding: utf-8

import indigo
from daikin_hvac import *

class Plugin(indigo.PluginBase):
    def __init__(self, pluginId, pluginDisplayName, pluginVersion,
                 pluginPrefs):
        indigo.PluginBase.__init__(self, pluginId, pluginDisplayName,
                                   pluginVersion, pluginPrefs)

        self.debug = pluginPrefs.get('debug', False)

        self.devices = {}

    def deviceStartComm(self, device):
        if device.id not in self.devices:
            self.devices[device.id] = device
            self.update(device)

    def deviceStopComm(self, device):
        if device.id in self.devices:
            self.devices.pop(device.id)

    def update(self, device):
        if device.deviceTypeId == "DaikinHVACUnit":
            self.updateHVAC(device)

    def updateHVAC(self, device):
        self.debugLog("Updating HVAC %s" % device.address)

        api = DaikinHVAC(device.address)

        sensor_info = api.sensor_info()

        if sensor_info["humidity"]:
            device.updateStateOnServer("humidityInput1", sensor_info["humidity"])
        if sensor_info["temperature"]:
            device.updateStateOnServer("temperatureInput1", sensor_info["temperature"])

        device.updateStateOnServer("outdoorTemperature", sensor_info["outdoorTemperature"])

        device.updateStateOnServer("outdoorTemperature", sensor_info["outdoorTemperature"])

        control_info = api.control_info()

        device.updateStateOnServer("fanDirection", control_info["fanDirection"])
        device.updateStateOnServer("fanSpeed",     control_info["fanSpeed"])

        dehumidifierOn = False
        fanMode        = indigo.kFanMode.Auto
        operationMode  = indigo.kHvacMode.Off
        setpointCool   = control_info["setpointCool"]
        setpointHeat   = control_info["setpointHeat"]

        if control_info["power"]:
            mode = control_info["mode"]

            if mode == "automatic":
                operationMode = indigo.kHvacMode.ProgramHeatCool
                setpointCool  = control_info["setpointHeatCool"]
                setpointHeat  = control_info["setpointHeatCool"]
            elif mode == "cool":
                operationMode = indigo.kHvacMode.ProgramCool
            elif mode == "heat":
                operationMode = indigo.kHvacMode.ProgramHeat
            elif mode == "dry":
                dehumidifierOn = True
            elif mode == "fan":
                fanMode       = indigo.kFanMode.AlwaysOn
                operationMode = indigo.kHvacMode.Off

        device.updateStateOnServer("hvacDehumidifierIsOn", dehumidifierOn)
        device.updateStateOnServer("hvacFanMode", fanMode)
        device.updateStateOnServer("hvacOperationMode", operationMode)
        device.updateStateOnServer("setpointCool", setpointCool)
        device.updateStateOnServer("setpointHeat", setpointHeat)

