import requests
import os


def pulse_smart_lights(request):
    """Flash my home lights a specific color
    
    Request Params:
        :duration: int - The duration the effect will last (in seconds)
        :color: string - The color the lights will change to
        :frequency: int - The frequency of the pulses (in seconds)
    """
    request_json = request.get_json()
    base_api = os.environ.get('BASE_API')
    lifx_token = os.environ.get('LIFX_TOKEN')

    # how long to flash lights?
    duration = request_json.get('duration', 30)
    # what color?
    color = request_json.get('color', 'red')
    # frequency of flashes?
    freq = request_json.get('frequency', 0.5)
    pulse_data = {
        "color": color,
        "period": freq,
        "cycles": duration,
        "power_on": True, 
    }
    url = f"{base_api}all/effects/pulse"
    headers = {"Authorization": f"Bearer {lifx_token}"}
    try:
        r = requests.post(url, json=pulse_data, headers=headers)
        return "OK", r.status_code
    
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}, {r.status_code}")
        return f"{e}", 500

