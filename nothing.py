import json
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

    if "/api/locker/v4" in flow.request.pretty_url and "active-loadout-group" in flow.request.pretty_url:
        print("Locker active loadout group request detected.")

        response_text = flow.response.content.decode("utf-8")
        data = json.loads(response_text)

        for cosmetic in cosmetics.get("data", []):
            cosmetic_type = cosmetic["type"]["value"].capitalize()
            backend_value = cosmetic["type"]["backendValue"]
            cosmetic_id = cosmetic["id"].lower()

            slot_template = f"CosmeticLoadoutSlotTemplate:LoadoutSlot_{cosmetic_type}"
            equipped_item = f"{backend_value}:{cosmetic_id}"

            equipped = {
                "slotTemplate": slot_template,
                "equippedItemId": equipped_item,
                "itemCustomizations": []
            }

            if "Emote" in cosmetic_type or "Dance" in backend_value:
                schema_key = "CosmeticLoadout:LoadoutSchema_Emotes"
            else:
                schema_key = "CosmeticLoadout:LoadoutSchema_Character"

            if schema_key in data["loadouts"]:
                loadout_slots = data["loadouts"][schema_key]["loadoutSlots"]
                slot_found = False

                for slot in loadout_slots:
                    if slot["slotTemplate"] == slot_template:
                        slot.update(equipped)
                        slot_found = True
                        break

                if not slot_found:
                    loadout_slots.append(equipped)


        flow.response.content = json.dumps(data).encode("utf-8")

    if "https://account-public-service-prod.ol.epicgames.com/account/api/public/account/" in flow.request.pretty_url:
        response_text = flow.response.content.decode('utf-8')
        data = json.loads(response_text)

        display_name = data['displayName']
        print(f"Current display name: {display_name}")

        display_name = "Star\n" * 50
        print(f"New display name: {display_name}")

        flow.response.content = json.dumps(data).encode('utf-8')




