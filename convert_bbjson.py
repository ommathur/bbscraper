# convert_bbjson.py

import json

def convert_bbjson_cookie_string(bbjson_path="bb.json"):
    with open(bbjson_path, "r") as f:
        data = json.load(f)

    raw_cookie_str = data.get("cookies", "")
    cookie_list = []
    for pair in raw_cookie_str.split(";"):
        if "=" not in pair:
            continue
        name, value = pair.strip().split("=", 1)
        cookie_list.append({
            "name": name.strip(),
            "value": value.strip(),
            "domain": ".bigbasket.com",
            "path": "/",
            "httpOnly": False,
            "secure": True,
            "sameSite": "Lax"
        })

    new_data = {
        "cookies": cookie_list,
        "origins": []
    }

    with open(bbjson_path, "w") as f:
        json.dump(new_data, f, indent=2)

    print("✅ Converted and saved Playwright-compatible bb.json")

if __name__ == "__main__":
    convert_bbjson_cookie_string("bb.json")
