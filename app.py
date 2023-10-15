from flask import Flask, jsonify, request, abort
from kasa import SmartPlug, SmartDevice
from kasa.discover import Discover
import json
app = Flask(__name__)


async def get_device(ip_or_alias) -> SmartDevice:
    '''Get the first smart device with the given ip or alias'''
    devices = await Discover.discover()
    def check(id):
        return id == ip_or_alias or devices[id].alias == ip_or_alias
    matching = filter(check, devices)
    if matching:
        host = next(matching)
        device = devices[host]
        return device
    
async def get_info(device: SmartDevice):
    '''Get device info'''
    await device.update()
    info = {**device.state_information, 'state': 'on' if device.is_on else 'off'}
    return info

@app.route("/kasa/toggle/<alias>", methods=["POST"])
async def kasa_toggle(alias: str):
    '''Toggle kasa smart device'''
    device = await get_device(alias)
    if device:
        await device.update()
        if device.is_on:
            await device.turn_off()
        if device.is_off:
            await device.turn_on()
        return jsonify(await get_info(device))
    else:
        abort(f'Device with ip or alias {alias} was not found', 400)

@app.route("/kasa/<alias>", methods=["GET","POST"])
async def kasa_state(alias: str):
    '''Set the kasa smart device state'''
    device = await get_device(alias)
    if device:
        if request.method == "GET":
            return jsonify(await get_info(device))
        else:
            abort(f'Unsupported method: {request.method}', 400)
    else:
         abort(f'Device with ip or alias {alias} was not found', 400)
    

@app.route("/")
def hello_world():
    # TODO Update to get main menu
    return "<p>Hello, World!</p>"