import json

def load_multi_json(text):
    decoder = json.JSONDecoder()
    idx = 0
    length = len(text)
    objects = []

    while idx < length:
        while idx < length and text[idx].isspace():
            idx += 1
        if idx >= length:
            break

        obj, new_idx = decoder.raw_decode(text, idx)
        objects.append(obj)
        idx = new_idx

    return objects
def load_data(log_file):
    print(f"Loading {log_file}...")
    with open(log_file, 'r', encoding='utf-8') as f:
        content = f.read()

    data_entries = load_multi_json(content)
    print(f"Loaded {len(data_entries)} game state entries")
    return data_entries

data_entries = load_data('gsi_log.txt')