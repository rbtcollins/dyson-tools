import requests
import yaml
import pprint
import re
import io

dict_to_list = False

def convert_array(line):
    global dict_to_list
    # if "game_items" in line:
    #     import pdb;pdb.set_trace()
    array = re.search("{.*}", line )
    if array is not None:
        (start, end) = array.span()
        subline = line[start+1:end-1]
        # is this actually a dict?
        if "=" in subline and subline.find("=") < subline.find("{"):
            subline = convert_array(line[start+1:end-1])
            return  line[:start] + "{" + subline.replace("=", ": ") + "}" + line[end:]
        subline = convert_array(line[start+1:end-1])
        # print(line)
        line = line[:start] + "[" + subline + "]" + line[end:]
        # import pdb;pdb.set_trace()
    elif (line.endswith("'game_recipes': {") or line.endswith("'game_techs': {") ) and "    " not in line:
        dict_to_list = True
        return line.replace("': {", "': [")
    elif line == "  }," and dict_to_list:
        line = "  ],"
        dict_to_list = False
    return line

def convert_key(line):
    if "=" in line:
        eq = line.find("=")
        key = line[:eq].strip()
        value=line[eq+1:].strip()
        indent = " " * (line.find(key))
        if key[0] == "[":
            key = key[1:-1]
            return f"{indent}{key}: {value}"
        line = f"{indent}'{key}': {value}"
    return line

rawdata = requests.get("https://dyson-sphere-program.fandom.com/wiki/Module:Recipe/Data?action=raw").content.decode('utf8').splitlines()

in_comment = False
indent = 0
for (i, line) in enumerate(rawdata):
    if line == "--[[":
        in_comment = True
    if in_comment:
        line = "# " + line
    if "--" in line:
        line = line.replace("--", "#")
    if line.endswith(" ]]"):
        in_comment = False
    if line == "return {":
        line = "data: {"
    line = convert_key(line)

    line = line.replace("\\'", "") # could convert to a " string so we can use quotes

    if not line.startswith("#") and not line.startswith("data"):
        line = "  " + line

    line = convert_array(line)
    
    # line = ("  " * indent) + line

    rawdata[i] = line

    # if line.endswith ("{"):
    #     indent += 2
    # elif line.endswith("}") or ("{" in line and line.endswith("},")):
    #     indent -= 2

yaml_lines = [l for l in rawdata if not l.startswith('//')]


# print(f"XXXX \u2082 XXX {0}", [l[77:78] + "\n" for l in rawdata])

open("data.yaml", "wt", encoding="utf8").writelines([l + "\n" for l in rawdata])


as_yaml = yaml.safe_load(io.StringIO('\n'.join(yaml_lines)))
