"""
Star Hybrid V1.0.0 beta
I don't reccommend skidding
Enjoy! :)
"""

import json
import ujson
import uuid
from mitmproxy import http, options
from mitmproxy.tools.dump import DumpMaster
from datetime import datetime
import requests
import threading
import asyncio

def load_cachee():
    try:
        with open('cosmetics_cache.json', 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Failed to load local cache: {e}")
        return {}

def load_cache():
    try:
        response = requests.get('https://fortnite-api.com/v2/cosmetics/br')
        response.raise_for_status() 
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Failed to load remote cache: {e}")
        return load_cachee() 

def request(flow: http.HTTPFlow):
    target_url = "https://starstools.vercel.app/starfn.jpg"
    url = flow.request.pretty_url
    
    if (".jpeg" in url or ".jpg" in url or ".png" in url or 
        "https://cdn2.unrealengine.com" in url or 
        "https://cdn1.epicgames.com" in url):
        flow.request.url = target_url
    
    if ("/lobby" in url and 
        (url.endswith(".jpeg") or url.endswith(".jpg") or url.endswith(".png")) and 
        flow.request.method == "GET"):
        flow.request.url = target_url

    if "https://prm-dialogue-public-api-prod.ak.epicgames.com/api/v1/fortnite-br/channel/interstitials/target" in flow.request.pretty_url:
        try:
            request_text = flow.request.content.decode('utf-8')
            data = json.loads(request_text)
            
            params = data.get('parameters', {})
            params.update({
                'battlepass': True,
                'battlepassLevel': 999,
                '3018': 999,
                'levelPerPass': [999, 999, 999],
                'victoryCrownsRoyales': 999
            })
            
            data['parameters'] = params
            flow.request.content = json.dumps(data).encode('utf-8')
        except Exception as e:
            print(f"Error modifying battlepass request: {e}")

def response(flow: http.HTTPFlow):
    if not hasattr(flow, 'cosmetics'):
        flow.cosmetics = load_cache()
    
    if 'profile' in flow.request.pretty_url and flow.response and flow.response.content:
        try:
            print("Detected 'Fortnite Profile' request")
            response_text = flow.response.content.decode('utf-8')
            data = json.loads(response_text)

            profile_changes = data.get('profileChanges', [])
            if not profile_changes:
                return

            profile_change = profile_changes[0]
            profile = profile_change.get('profile', {})
            print(f"Profile: {profile.get('profileId', 'None')}")

            if profile_change.get('changeType') == 'fullProfileUpdate' and profile.get('profileId') == 'athena':
                print("Athena profile update detected")
                current_items = {item['templateId']: uuid for uuid, item in profile.get('items', {}).items()}
                
                for cosmetic in flow.cosmetics.get('data', []):
                    type_data = cosmetic.get('type', {})
                    backend_value = type_data.get('backendValue', 'UnknownType')
                    cosmetic_id = cosmetic.get('id', 'UnknownID')
                    template_id = f"{backend_value}:{cosmetic_id}"

                    if template_id not in current_items:
                        variants = [
                            {
                                "channel": variant.get('channel', 'UnknownChannel'),
                                "active": None,
                                "owned": [option.get('tag', 'UnknownTag') for option in variant.get('options', [])]
                            } for variant in cosmetic.get('variants', [])
                        ]
                        item_uuid = uuid.uuid4().hex
                        item = {
                            "templateId": template_id,
                            "attributes": {
                                "creation_time": profile.get('created', '0'),
                                "level": 1,
                                "item_seen": True,
                                "variants": variants,
                            },
                            "quantity": 1,
                        }
                        profile.setdefault('items', {})[item_uuid] = item

                data['profileChanges'][0]['profile'] = profile
                flow.response.content = json.dumps(data).encode('utf-8')
                print(f"Profile items updated: {len(profile['items'])} items.")
        except Exception as e:
            print(f"Error processing profile response: {e}")

    if "https://fngw-svc-gc-livefn.ol.epicgames.com/api/locker/v4" in flow.request.pretty_url:
        try:
            print("Cosmetic changed detected")
            response_text = flow.response.content.decode('utf-8')
            data = json.loads(response_text)

            if 'loadouts' in data and 'CosmeticLoadout:LoadoutSchema_Character' in data['loadouts']:
                char_loadout = data['loadouts']['CosmeticLoadout:LoadoutSchema_Character']
                slots = char_loadout.get('loadoutSlots', [])

                if len(slots) >= 7:
                    new_data = {
                        "loadoutSlots": [
                            {
                                "slotTemplate": "CosmeticLoadoutSlotTemplate:LoadoutSlot_Glider",
                                "equippedItemId": slots[0].get('equippedItemId'),
                                "itemCustomizations": slots[0].get('itemCustomizations', [])
                            },
                            {
                                "slotTemplate": "CosmeticLoadoutSlotTemplate:LoadoutSlot_Shoes",
                                "equippedItemId": slots[1].get('equippedItemId'),
                                "itemCustomizations": slots[1].get('itemCustomizations', [])
                            },
                            {
                                "slotTemplate": "CosmeticLoadoutSlotTemplate:LoadoutSlot_Contrails",
                                "equippedItemId": slots[2].get('equippedItemId'),
                                "itemCustomizations": slots[2].get('itemCustomizations', [])
                            },
                            {
                                "slotTemplate": "CosmeticLoadoutSlotTemplate:LoadoutSlot_Aura",
                                "equippedItemId": slots[3].get('equippedItemId'),
                                "itemCustomizations": slots[3].get('itemCustomizations', [])
                            },
                            {
                                "slotTemplate": "CosmeticLoadoutSlotTemplate:LoadoutSlot_Backpack",
                                "equippedItemId": slots[4].get('equippedItemId'),
                                "itemCustomizations": slots[4].get('itemCustomizations', [])
                            },
                            {
                                "slotTemplate": "CosmeticLoadoutSlotTemplate:LoadoutSlot_Pickaxe",
                                "equippedItemId": slots[5].get('equippedItemId'),
                                "itemCustomizations": slots[5].get('itemCustomizations', [])
                            },
                            {
                                "slotTemplate": "CosmeticLoadoutSlotTemplate:LoadoutSlot_Character",
                                "equippedItemId": slots[6].get('equippedItemId'),
                                "itemCustomizations": slots[6].get('itemCustomizations', [])
                            }
                        ],
                        "shuffleType": "DISABLED"
                    }
                    data['loadouts']['CosmeticLoadout:LoadoutSchema_Character'].update(new_data)
                    flow.response.content = json.dumps(data).encode('utf-8')
                else:
                    print("Not enough slots in the response to modify cosmetics.")
        except Exception as e:
            print(f"Error processing locker response: {e}")

    if ("https://fngw-mcp-gc-livefn.ol.epicgames.com/fortnite/api/game/v2/profile" in flow.request.pretty_url and 
        "profileId=athena" in flow.request.pretty_url):
        try:
            response_text = flow.response.content.decode('utf-8')
            data = json.loads(response_text)

            profile_changes = data.get('profileChanges', [])
            if profile_changes and isinstance(profile_changes[0], dict):
                profile = profile_changes[0].get('profile', {})
                stats = profile.get('stats', {})
                attributes = stats.get('attributes', {})

                attributes.update({
                    "habanero_unlocked": False,
                    "level": 999,
                    "mfa_reward_claimed": True,
                    "last_xp_interaction": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z"),
                    "quest_manager": {
                        "dailyLoginInterval": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z"),
                        "dailyQuestRerolls": 1
                    },
                    "book_level": 999,
                    "season_num": 36,
                    "accountLevel": 999,
                    "locker_service_cosmetic_items_migration_status": "LockerReadDualWrite"
                })

                data['profileChanges'][0]['profile']['stats']['attributes'] = attributes
                flow.response.content = json.dumps(data).encode('utf-8')
        except Exception as e:
            print(f"Error modifying athena profile: {e}")

    if ("https://account-public-service-prod.ol.epicgames.com/account/api/public/account/" in flow.request.url and 
        flow.request.method == "GET"):
        try:
            if "displayName" in flow.response.text:
                data = ujson.loads(flow.response.text)
                displayName = data["displayName"]
                print(f"Current Display Name: {displayName}")
                new_displayName = f"{displayName} (Star)" 
                data["displayName"] = new_displayName
                flow.response.text = ujson.dumps(data)
                print(f"New Display Name: {new_displayName}")
        except Exception as e:
            print(f"Error modifying display name: {e}")

class FortniteAddon:
    def request(self, flow: http.HTTPFlow):
        request(flow)
        
    def response(self, flow: http.HTTPFlow):
        response(flow)

async def run_proxy():
    opts = options.Options(
        listen_host='0.0.0.0',
        listen_port=8080,
        ssl_insecure=True
    )
    master = DumpMaster(opts)
    master.addons.add(FortniteAddon())
    print(f"Starting mitmproxy on port {opts.listen_port}")
    await master.run()

def start_proxy():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        loop.run_until_complete(run_proxy())
    except KeyboardInterrupt:
        print("Proxy shutting down...")
    finally:
        loop.close()

if __name__ == "__main__":
    proxy_thread = threading.Thread(target=start_proxy, daemon=True)
    proxy_thread.start()
    
    print("Proxy is running in the background. Press Ctrl+C to stop.")
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("Shutting down...")
