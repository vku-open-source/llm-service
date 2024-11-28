import json

def load_json(string):
    try:
        start_index = min(string.find('['), string.find('{'))
        end_index = max(string.rfind(']'), string.rfind('}')) + 1
        string = string[start_index:end_index]
        if "\{" in string:
            string = string.replace("\{", "\ {")
        res = json.loads(string)
    except Exception as e:
        print(e)
        print(string)
        res = {}
    return res
