import json
import unidecode

with open('country_phones.json') as f:
    phones = json.load(f)

with open('country_codes.json') as f:
    codes = json.load(f)

not_found = []

for code in codes:
    found = False
    asciified = unidecode.unidecode(code['nome']).upper()
    pt_name = code['nome']
    parsed = asciified \
        .replace("(", "") \
        .replace(")", "") \
        .replace(" ", "_") \
        .replace("-", "_") \
        .replace(".", "_") \
        .replace("_ ", " ") \
        .replace("__", "_")

    two_digit_code = code['sigla2']
    three_digit_code = code['sigla3']

    for p in phones:
        if two_digit_code == p['code'] and p["dial_code"] is not None:
            en_name = p['name']
            dial_code = p['dial_code'].replace(" ", "")

            lang = {
                "langs": {
                    "pt-br": str(pt_name),
                    "en-us": en_name,
                },
                "phone": {
                    "two_digits": two_digit_code,
                    "three_digits": three_digit_code,
                    "prefix": dial_code
                }
            }

            print(parsed + " = " + json.dumps(lang, ensure_ascii=False,
                                              sort_keys=True, indent=4
                                              ) + "\n")
            found = True

    if not found:

        lang = {
            "langs": {
                "pt-br": str(pt_name),
                "en-us": "None",
            },
            "phone": {
                "two_digits": two_digit_code,
                "three_digits": three_digit_code,
                "prefix": "None"
            }
        }
        not_found.append(parsed)

        print(parsed + " = " + json.dumps(lang, ensure_ascii=False,
                                          sort_keys=True, indent=4
                                          ) + "\n")

with open("not_found.txt", "w") as f:
    f.write(json.dumps(not_found))
