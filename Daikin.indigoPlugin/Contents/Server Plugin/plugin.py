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

    def actionControlThermostat(self, action, device):
        if action.thermostatAction in [
                indigo.kThermostatAction.RequestEquipmentState,
                indigo.kThermostatAction.RequestHumidities,
                indigo.kThermostatAction.RequestMode,
                indigo.kThermostatAction.RequestSetpoints,
                indigo.kThermostatAction.RequestStatusAll,
                indigo.kThermostatAction.RequestTemperatures,
           ]:
            self.updateHVAC(device)
        else:
            self.debugLog("Unhandled thermostat control action %s" % action)

    def convertTemperature(self, device, celcius):
        if device.ownerProps["temperature"] == "celcius":
            return celcius
        else:
            return round(1.8 * celcius + 32, 0)

    def deviceStartComm(self, device):
        if device.id not in self.devices:
            self.devices[device.id] = device
            self.update(device)

    def deviceStopComm(self, device):
        if device.id in self.devices:
            self.devices.pop(device.id)

    def runConcurrentThread(self):
        while True:
            if len(self.devices) > 0:
                self.updateAll()

            self.sleep(60)

    def update(self, device):
        if device.deviceTypeId == "DaikinHVACUnit":
            self.updateHVAC(device)

    def updateAll(self):
        for _, device in self.devices.iteritems():
            self.updateHVAC(device)

    def updateHVAC(self, device):
        self.debugLog("Updating HVAC %s" % device.address)

        api = DaikinHVAC(device.address)

        sensor_info = api.sensor_info()

        if sensor_info["humidity"]:
            device.updateStateOnServer("humidityInput1", sensor_info["humidity"])

        if sensor_info["temperature"]:
            device.updateStateOnServer("temperatureInput1", self.convertTemperature(device, sensor_info["temperature"]))

        device.updateStateOnServer("outdoorTemperature", self.convertTemperature(device, sensor_info["outdoorTemperature"]))

        control_info = api.control_info()

        device.updateStateOnServer("fanDirection", control_info["fanDirection"])
        device.updateStateOnServer("fanSpeed",     control_info["fanSpeed"])

        dehumidifierOn = False
        fanMode        = indigo.kFanMode.Auto
        operationMode  = indigo.kHvacMode.Off
        setpointCool   = self.convertTemperature(device, control_info["setpointCool"])
        setpointHeat   = self.convertTemperature(device, control_info["setpointHeat"])

        if control_info["power"]:
            mode = control_info["mode"]

            if mode == "automatic":
                operationMode = indigo.kHvacMode.ProgramHeatCool
                setpointCool  = self.convertTemperature(device, control_info["setpointHeatCool"])
                setpointHeat  = self.convertTemperature(device, control_info["setpointHeatCool"])
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

