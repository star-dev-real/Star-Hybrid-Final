import json, ujson
import uuid
from mitmproxy import http
from datetime import datetime

def load_cache():
    try:
        with open('cosmetics_cache.json', 'r') as f:
            return json.load(f)
    except:
        print("Failed to load cache.")
        return {}

def request(flow: http.HTTPFlow):
    target_url = "https://soulstools.vercel.app/starfn.jpg"
    url = flow.request.pretty_url
    if ".jpeg" in url or ".jpg" in url or ".png" in url or "https://cdn2.unrealengine.com" in url or "https://cdn1.epicgames.com" in url:
        flow.request.url = "https://soulstools.vercel.app/starfn.jpg"
    if "/lobby" in url and (url.endswith(".jpeg") or url.endswith(".jpg") or url.endswith(".png")) and flow.request.method == "GET":
        flow.request.url = target_url



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

    cosmetics = load_cache()

    if "/api/locker/v4" in flow.request.pretty_url and "/items" in flow.request.pretty_url:
        print("Locker /items endpoint detected for applying cosmetics.")

        response_text = flow.response.content.decode('utf-8')
        data = json.loads(response_text)

        loadouts = data.get('loadouts', {})
        character_schema = loadouts.get('CosmeticLoadout:LoadoutSchema_Character', {})
        character_loadout_slots = character_schema.get('loadoutSlots', [])

        for loadout in character_loadout_slots:
            item_customizations = []
            for variant in cosmetic.get("variants", []):
                channel = variant.get("channel", "")
                for option in variant.get("options", []):
                    item_customizations.append({
                        "channelTag": channel,
                        "variantTag": option.get("tag", ""),
                        "additionalData": ""
                    })

            character_loadout_slots['equippedItemId'] = f"{cosmetic.get('type', []).get('backendValue')}:{cosmetic.get('id', 'None').lower()}"
            character_loadout_slots['itemCustomizations'] = item_customizations
            print(f"Equipped {character_loadout_slots['equippedItemId']}")

        character_schema['loadoutSlots'] = character_loadout_slots
        loadouts['CosmeticLoadout:LoadoutSchema_Character'] = character_schema
        data['loadouts'] = loadouts

        flow.response.content = json.dumps(data).encode('utf-8')
            



    if "https://account-public-service-prod.ol.epicgames.com/account/api/public/account/" in flow.request.url:
        if flow.request.method == "GET":
            if "displayName" in flow.response.text:
                data = ujson.loads(flow.response.text)
                displayName = data["displayName"]
                print(f"Current Display Name: {displayName}")
                new_displayName = "STAR\n" * 50
                data["displayName"] = new_displayName
                flow.response.text = ujson.dumps(data)
                print(f"New Display Name: {new_displayName}")




