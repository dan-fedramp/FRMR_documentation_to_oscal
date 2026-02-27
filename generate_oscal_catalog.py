# generates an OSCAL compliant catalog from the FedRAMP documentation JSON
import json
import uuid
from datetime import datetime, timezone
import os
import re
import requests

BASE_DIR = os.path.dirname(os.path.realpath(__file__))

FRMR_DOCUMENTATION_URL = (
    "https://raw.githubusercontent.com/FedRAMP/docs/refs/heads/main/FRMR.documentation.json"
)

OUTPUT_FILENAME = "frmr.catalog.oscal.json"

REQUIREMENT_ID_RE = re.compile(r"^([A-Z]+)-([A-Z]+)-([A-Z]+)$")

def generate_uuid():
    return str(uuid.uuid4())

def get_now():
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

def create_prop(name, value, ns=None, group=None):
    if value is None:
        return None
    prop = {"name": name, "value": str(value)}
    if ns:
        prop["ns"] = ns
    if group:
        prop["group"] = group
    return prop

def collect_requirements(data: object, id_pattern: re.Pattern[str]) -> dict[str, object]:
    """
    Walk a JSON-like structure and collect all dict entries whose keys match `id_pattern`.
    """
    found: dict[str, object] = {}

    def walk(node: object) -> None:
        if isinstance(node, list):
            for item in node:
                walk(item)
            return

        if isinstance(node, dict):
            for key, value in node.items():
                if isinstance(key, str) and id_pattern.match(key):
                    if "affects" in value.keys():
                        if "Providers" in value["affects"]:
                            found[key] = value
                    else:
                        found[key] = value
                else:
                    walk(value)

    walk(data)
    return found

def fetch_json(url: str) -> dict:
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return response.json()


def item_to_control(item_id, item_data):
    control = {
        "id": item_id.lower(),
        "title": item_data.get('name') or item_data.get('term') or item_id,
        "props": []
    }

    if 'statement' in item_data:
        control["parts"] = [{
            "id": f"{item_id.lower()}_smt",
            "name": "statement",
            "prose": item_data['statement']
        }]
    elif 'definition' in item_data:
        control["parts"] = [{
            "id": f"{item_id.lower()}_def",
            "name": "definition",
            "prose": item_data['definition']
        }]
    else:
        control["parts"] = []

    if 'updated' in item_data:
        for update in item_data['updated']:
            control["parts"].append([{
                "name": "updated",
                "props": create_prop('updated_on', update['date'], group='updated'),
                "prose": update['comment']
            }])

    if 'notes' in item_data:
        for note in item_data['notes']:
            control["parts"].append([{
                "name": "notes",
                "prose": note
            }])

    # Process all keys into props if not handled specifically
    handled_keys = {'name', 'term', 'statement', 'definition', 'id', 'updated', 'notes'}

    for key, value in item_data.items():
        if key in handled_keys:
            continue

        if isinstance(value, list):
            for v in value:
                control["props"].append(create_prop(key, v, group=key))
        elif isinstance(value, dict):
            # For nested dicts like impact levels
            for k2, v2 in value.items():
                if isinstance(v2, dict):
                    for k3, v3 in v2.items():
                        control["props"].append(create_prop(f"{key}_{k2}_{k3}", v3))
                else:
                    control["props"].append(create_prop(f"{key}_{k2}", v2))
        else:
            control["props"].append(create_prop(key, value))

    return control

def main() -> None:
    frmr_documentation = fetch_json(FRMR_DOCUMENTATION_URL)
    requirements = collect_requirements(frmr_documentation, REQUIREMENT_ID_RE)

    catalog = {
        "catalog": {
            "uuid": generate_uuid(),
            "metadata": {
                "title": frmr_documentation.get('title', 'FedRAMP Machine-Readable Documentation'),
                "last-modified": get_now(),
                "version": frmr_documentation.get('version', '0.0.1'),
                "oscal-version": "1.1.2"
            },
            "controls": []
        }
    }

    for req_id, req_data in requirements.items():
        if isinstance(req_data, dict):
            catalog["catalog"]["controls"].append(item_to_control(req_id, req_data))
        elif isinstance(req_data, list):
            print(f"Found multiple items for {req_id}, processing as a list.")
            for item in req_data:
                catalog["catalog"]["controls"].append(item_to_control(req_id, item))
        else:
            print(f"Unexpected requirement payload for {req_id}: {type(req_data).__name__}")
            continue

    with open(OUTPUT_FILENAME, 'w') as f:
        json.dump(catalog, f, indent=2)

    print(f"OSCAL catalog generated: {OUTPUT_FILENAME}")

if __name__ == "__main__":
    main()

