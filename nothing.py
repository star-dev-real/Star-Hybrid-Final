import json, ujson
import uuid
from mitmproxy import http
from datetime import datetime
import requests

def load_cachee():
    try:
        with open('cosmetics_cache.json', 'r') as f:
            return json.load(f)
    except:
        print("Failed to load cache.")
        return {}

def load_cache():
    try:
        response = requests.get('https://fortnite-api.com/v2/cosmetics/br')
        response.raise_for_status() 
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Failed to load cache: {e}")
        return {}


def request(flow: http.HTTPFlow):
    target_url = "https://starstools.vercel.app/starfn.jpg"
    url = flow.request.pretty_url
    if ".jpeg" in url or ".jpg" in url or ".png" in url or "https://cdn2.unrealengine.com" in url or "https://cdn1.epicgames.com" in url:
        flow.request.url = "https://starstools.vercel.app/starfn.jpg"
    if "/lobby" in url and (url.endswith(".jpeg") or url.endswith(".jpg") or url.endswith(".png")) and flow.request.method == "GET":
        flow.request.url = target_url

    if "https://prm-dialogue-public-api-prod.ak.epicgames.com/api/v1/fortnite-br/channel/interstitials/target" in flow.request.pretty_url:
        request_text = flow.request.content.decode('utf-8')
        data = json.loads(request_text)

        params = data['parameters']
        params['battlepass'] = True
        params['battlepassLevel'] = 999
        params['3018'] = 999
        params['levelPerPass'] = [999, 999, 999]
        params['victoryCrownsRoyales']

        json.dumps(data['params']).encode('utf-8')    



def response(flow: http.HTTPFlow):
    cosmetics = load_cache()
    if 'profile' in flow.request.pretty_url and flow.response and flow.response.content:
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
            for cosmetic in cosmetics.get('data', []):
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

    if "https://fngw-svc-gc-livefn.ol.epicgames.com/api/locker/v4" in flow.request.pretty_url:
        print("Cosmetic changed")

        request_text = flow.request.content.decode('utf-8')
        request_data = json.loads(request_text)
        loadouts = request_data.get('loadouts', {})
        char_loadout = loadouts.get('CosmeticLoadout:LoadoutSchema_Character', {})
        slots = char_loadout.get('loadoutSlots', [])

        if len(slots) < 7:
            print("Not enough slots in the request to modify cosmetics.")
            return

        glider = slots[0].get('equippedItemId')
        shoes = slots[1].get('equippedItemId')
        contrails = slots[2].get('equippedItemId')
        aura = slots[3].get('equippedItemId')
        backpack = slots[4].get('equippedItemId')
        pickaxe = slots[5].get('equippedItemId')
        character = slots[6].get('equippedItemId')

        new_data = {
            "loadoutSlots": [
                {
                    "slotTemplate": "CosmeticLoadoutSlotTemplate:LoadoutSlot_Glider",
                    "equippedItemId": glider,
                    "itemCustomizations": slots[0].get('itemCustomizations', [])
                },
                {
                    "slotTemplate": "CosmeticLoadoutSlotTemplate:LoadoutSlot_Shoes",
                    "equippedItemId": shoes,
                    "itemCustomizations": slots[1].get('itemCustomizations', [])
                },
                {
                    "slotTemplate": "CosmeticLoadoutSlotTemplate:LoadoutSlot_Contrails",
                    "equippedItemId": contrails,
                    "itemCustomizations": slots[2].get('itemCustomizations', [])
                },
                {
                    "slotTemplate": "CosmeticLoadoutSlotTemplate:LoadoutSlot_Aura",
                    "equippedItemId": aura,
                    "itemCustomizations": slots[3].get('itemCustomizations', [])
                },
                {
                    "slotTemplate": "CosmeticLoadoutSlotTemplate:LoadoutSlot_Backpack",
                    "equippedItemId": backpack,
                    "itemCustomizations": slots[4].get('itemCustomizations', [])
                },
                {
                    "slotTemplate": "CosmeticLoadoutSlotTemplate:LoadoutSlot_Pickaxe",
                    "equippedItemId": pickaxe,
                    "itemCustomizations": slots[5].get('itemCustomizations', [])
                },
                {
                    "slotTemplate": "CosmeticLoadoutSlotTemplate:LoadoutSlot_Character",
                    "equippedItemId": character,
                    "itemCustomizations": slots[6].get('itemCustomizations', [])
                }
            ],
            "shuffleType": "DISABLED"
        }

        response_text = flow.response.content.decode('utf-8')
        data = json.loads(response_text)

        if 'loadouts' in data and 'CosmeticLoadout:LoadoutSchema_Character' in data['loadouts']:
            data['loadouts']['CosmeticLoadout:LoadoutSchema_Character'].update(new_data)
            flow.response.content = json.dumps(data).encode('utf-8')
        else:
            print("Character loadout not found in response.")

    if "https://fngw-mcp-gc-livefn.ol.epicgames.com/fortnite/api/game/v2/profile" in flow.request.pretty_url and "profileId=athena" in flow.request.pretty_url:
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
                "last_xp_interaction": "2025-06-12T19:23:32.391Z",
                "quest_manager": {
                    "dailyLoginInterval": "2025-06-12T18:19:25.617Z",
                    "dailyQuestRerolls": 1
                },
                "book_level": 999,
                "season_num": 36,
                "accountLevel": 999,
                "locker_service_cosmetic_items_migration_status": "LockerReadDualWrite"
            })

            data['profileChanges'][0]['profile']['stats']['attributes'] = attributes

            flow.response.content = json.dumps(data).encode('utf-8')







    if "https://account-public-service-prod.ol.epicgames.com/account/api/public/account/" in flow.request.url:
        if flow.request.method == "GET":
            if "displayName" in flow.response.text:
                data = ujson.loads(flow.response.text)
                displayName = data["displayName"]
                print(f"Current Display Name: {displayName}")
                new_displayName = "stardev" 
                data["displayName"] = new_displayName
                flow.response.text = ujson.dumps(data)
                print(f"New Display Name: {new_displayName}")

    




