import requests
from time import strftime, localtime
from datetime import datetime
import locale
locale.setlocale(locale.LC_TIME, 'it_IT.UTF-8')

# ---------------- GEO ----------------
def geocoding(city):
    api_k = '*******************************************'
    url = 'http://api.openweathermap.org/geo/1.0/direct?'

    city = city.strip() + ',IT'
    url_fin = url + 'q=' + city + '&limit=1&appid=' + api_k

    data = requests.get(url_fin).json()

    if not data:
        return None

    return {"lat": str(data[0]["lat"]), "lon": str(data[0]["lon"])}

# ---------------- WEATHER ----------------
class OW_daily():
    def __init__(self, lat, lon):
        self.lat = lat
        self.lon = lon

    def OW_request(self):
        api_k = '*********************************************'
        url = 'http://api.openweathermap.org/data/3.0/onecall?'
        unit = 'metric'
        lan = 'it'

        url_fin = url + 'lat=' + self.lat + '&lon=' + self.lon + '&appid=' + api_k + '&units=' + unit + '&lang=' + lan
        return requests.get(url_fin).json()

# ---------------- ICON + PARSER (ORIGINALE) ----------------
class Icon():
    def __init__(self, data):
        self.data = data

    def diz_extrac_h(self, i):
        h = self.data['hourly'][i]
        return {
            "temp": int(h['temp']),
            "dt": strftime('%d/%m/%Y - %H:%M', localtime(h['dt'])),
            "desc": h['weather'][0]['description'],
            "main": h['weather'][0]['main'],
            "id": h['weather'][0]['id']
        }

    def diz_extrac_d(self, i):
        forec = {}

        daily = self.data.get('daily', [])

        if i >= len(daily):
            return forec

        day = daily[i]

        forec['dt'] = strftime('%A - %d/%m/%Y', localtime(day.get('dt', 0)))

        temp = day.get('temp', {})
        forec['max'] = int(temp.get('max', 0))
        forec['min'] = int(temp.get('min', 0))

        forec['wind_deg'] = day.get('wind_deg')
        forec['wind_speed'] = day.get('wind_speed')

        forec['moonrise'] = strftime('%H:%M:%S', localtime(day.get('moonrise', 0)))
        forec['moonset'] = strftime('%H:%M:%S', localtime(day.get('moonset', 0)))
        forec['moon_phase'] = day.get('moon_phase')

        forec['sunrise'] = strftime('%H:%M:%S', localtime(day.get('sunrise', 0)))
        forec['sunset'] = strftime('%H:%M:%S', localtime(day.get('sunset', 0)))

        forec['uvi'] = day.get('uvi')

        weather = day.get('weather', [{}])[0]
        forec['description'] = weather.get('description')
        forec['id'] = weather.get('id')
        forec['main'] = weather.get('main')

        forec['rain'] = day.get('rain', 0)

        return forec

    def icon_h(self, lst):
        forecast_ico = {
            'Clear': "☀",
            'Clouds': {'801': "🌤", '802': "⛅", '803': "🌥", '804': "☁"},
            'Rain': "🌧",
            'Drizzle': "🌦",
            'Thunderstorm': "⛈",
            'Snow': "❄"
        }
        result = []
        for item in lst:
            main = item['main']
            if main != "Clouds":
                result.append(forecast_ico.get(main, "❓"))
            else:
                result.append(forecast_ico['Clouds'].get(str(item['id']), "☁"))
        return result

    def icon_d(self, lst_forec_d):
        forecast_ico = {
            'Clear': "☀",
            'Clouds': {'801': "🌤", '802': "⛅", '803': "🌥", '804': "☁"},
            'Drizzle': "🌦",
            'Rain': "🌧",
            'Thunderstorm': "⛈",
            'Snow': "❄"
        }

        result = []

        for day in lst_forec_d:
            main = day.get('main')
            wid = str(day.get('id'))

            if main != "Clouds":
                result.append(forecast_ico.get(main, "❓"))
            else:
                result.append(forecast_ico['Clouds'].get(wid, "☁"))

        return result

    def lunar_phase(self, lst_forec_d):
        phase_map = [
            (0.00, "🌑"),
            (0.12, "🌒"),
            (0.25, "🌓"),
            (0.37, "🌔"),
            (0.50, "🌕"),
            (0.60, "🌖"),
            (0.75, "🌗"),
            (0.87, "🌘"),
            (1.00, "🌑")
        ]

        result = []

        for day in lst_forec_d:
            m_p = day.get("moon_phase", 0)

            # trova icona più vicina
            closest = min(phase_map, key=lambda x: abs(x[0] - m_p))
            result.append(closest[1])

        return result

    def wind_direction(self, deg):
        if deg is None:
            return "N/D"

        if deg == 0 or deg == 360:
            return "⬆️ Tramontana"
        elif 0 < deg < 45:
            return "↗️ Grecale"
        elif 45 <= deg < 90:
            return "➡️ Levante"
        elif 90 <= deg < 135:
            return "↘️ Scirocco"
        elif 135 <= deg < 180:
            return "⬇️ Ostro"
        elif 180 <= deg < 225:
            return "↙️ Libeccio"
        elif 225 <= deg < 270:
            return "⬅️ Ponente"
        elif 270 <= deg < 315:
            return "↖️ Maestrale"
        elif 315 <= deg <= 360:
            return "⬆️ Tramontana"
        return None


# ---------------- TEXT ----------------
class TextMeBot():
    def textme_bot_h(self, i, forec, ico):
        f = forec[i]
        return (
            f"Oraria | {f['dt']} "
            f"🌡 Temp: {f['temp']}°C "
            f"{ico[i]} {f['desc']}"
        )

txt_bot = TextMeBot()

# ---------------- ENTRY ----------------
def get_ico(lat, lon):
    return Icon(OW_daily(lat, lon).OW_request())
