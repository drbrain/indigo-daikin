import urllib
import urllib2

class DaikinHVAC:
    DIRECTIONS = {
        "0": "stop",
        "1": "vertical",
        "2": "horizontal",
        "3": "both",
    }

    MODES = {
        "0": "automatic",
        "1": "automatic",
        "2": "dry",
        "3": "cool",
        "4": "heat",
        "6": "fan",
        "7": "automatic",
    }

    SPEEDS = {
        "A": "automatic",
        "B": "silent",
        "3": "1",
        "4": "2",
        "5": "3",
        "6": "4",
        "7": "5",
    }

    def __init__(self, address):
        self.address = address

    def basic_info(self):
        url = "http://%s/common/basic_info" % self.address

        fields = self.__GET(url)

        basic_info = {}

        basic_info["name"]  = urllib.parse.unquote(fields["name"])
        basic_info["power"] = fields["pow"] == "1"

        return basic_info

    def control_info(self):
        url = "http://%s/aircon/get_control_info" % self.address

        fields = self.__GET(url)

        control_info = {}

        control_info["power"]        = fields["pow"] == "1"
        control_info["mode"]         = self.MODES[fields["mode"]]
        control_info["setPoint"]     = float(fields["stemp"])
        control_info["setHumidity"]  = float(fields["shum"])
        control_info["fanSpeed"]     = self.SPEEDS[fields["f_rate"]]
        control_info["fanDirection"] = self.DIRECTIONS[fields["f_dir"]]

        control_info["setpointCool"]     = float(fields["dt3"])
        control_info["setpointHeat"]     = float(fields["dt4"])
        control_info["setpointHeatCool"] = float(fields["dt7"])

        return control_info

    def sensor_info(self):
        url = "http://%s/aircon/get_sensor_info" % self.address

        fields = self.__GET(url)

        sensor_info = {}

        if fields["hhum"] == "-":
            sensor_info["humidity"] = None
        else:
            sensor_info["humidity"] = float(fields["hhum"])

        if fields["htemp"] == "-":
            sensor_info["temperature"] = None
        else:
            sensor_info["temperature"] = float(fields["htemp"])

        if fields["otemp"] == "-":
            sensor_info["outdoorTemperature"] = None
        else:
            sensor_info["outdoorTemperature"] = float(fields["otemp"])

        return sensor_info

    def __GET(self, url):
        try:
            f = urllib2.urlopen(url)
        except urllib2.HTTPError, e:
            self.errorLog('Error fetching %s: %s' % (url, str(e)))
            return;

        fields = f.read().split(",")

        f.close()

        response = {}

        for field in fields:
            key, value = field.split("=", 2)
            response[key] = value

        return response

    def __POST(self, url, data):
        request = urllib2.Request(url, data=body)
        request.add_header('Content-Type', 'application/json')
        request.get_method = lambda: "POST"

        opener = urllib2.build_opener(urllib2.HTTPHandler)

        try:
            f = opener.open(request)
        except urllib2.HTTPError, e:
            self.errorLog('Error fetching %s: %s' % (url, str(e)))
            return;

        response = json.load(f)

        f.close()

        return response

