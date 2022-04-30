from collections import defaultdict
import yaml
import pprint

docf = open("data.yaml", "rt", encoding="utf8")

doc = yaml.safe_load(docf)

# import pdb;pdb.set_trace()
# pprint.pprint(doc["data"].keys()) #["game_facilities"])

# import pdb;pdb.set_trace()
# pprint.pprint([v for v in  doc["data"]["game_items"].values() if v["name"] == "Casimir Crystal"])



buildings = [v for v in doc["data"]["game_recipes"]
    if v["type"] == "ASSEMBLE" and v["name"] not in [
        "Antimatter Fuel Rod",
        "Hydrogen Fuel Rod",
        "Deuteron Fuel Rod",
        "Proliferator Mk.I",
        "Proliferator Mk.II",
        "Proliferator Mk.III",
        "Small Carrier Rocket",
        ] and doc["data"]["game_items"][v["outputs"][0]]["type"] not in ["COMPONENT", "MATERIAL"]
        ]

def get_inputs(building):
    inputs = []
    for (pos, value) in enumerate(building["inputs"]):
        if (pos %2) == 0:
            inputs.append(value)
    return inputs

def get_input(input):
    return doc["data"]["game_items"][input]

def get_building_inputs(building):
    return [input for input in get_inputs(building) if get_input(input)["name"] in building_to_recipe]

building_to_recipe = {}
item_to_building = defaultdict(list)
inputs = set()
for building in buildings:
    building_to_recipe[building["name"]] = building
    for input in get_inputs(building):
        item_to_building[input].append(building["name"])
        #  = doc["data"]["game_items"][value]
        inputs.add(input)
    
print("====================")
pprint.pprint(item_to_building)
pprint.pprint(len(item_to_building))
print("====================")
def observe_depth(depths, name, depth):
    if name not in depths or depths[name] < depth:
        depths[name] = depth
def transitive_deps(depths, building):
    if building["name"] in depths:
        return depths[building["name"]]
    max_depth = 0
    for input in get_building_inputs(building):
        input_item = get_input(input)
        depth = transitive_deps(depths, building_to_recipe[input_item["name"]])
        max_depth = max(depth, max_depth)
    observe_depth(depths, building["name"], max_depth+1)
    return max_depth + 1
        
depths = dict() # building name -> distance from only raw materials
for (name, building) in building_to_recipe.items():
    transitive_deps(depths, building)

topo_sort = [(v, height) for (height, v) in sorted([(height, name) for (name, height) in depths.items()])]
topo_dict = dict(topo_sort)
topo_sorted = [v for (v, h) in topo_sort]
pprint.pprint(topo_sort)
print("====================")

# clustering
clusters = defaultdict(list)
# depth 1 start as single clusters
for (name, depth) in topo_sort:
    if depth == 1:
        clusters[name]
        continue
    # Find the matching cluster(s) to join with
    building = building_to_recipe[name]
    deps = get_building_inputs(building)
    if len(deps) > 1:
        raise Exception("multiple building inputs")
    for dep in deps:
        dep_building = building_to_recipe[get_input(dep)["name"]]
        while True:
            if dep_building["name"] in clusters:
                clusters[dep_building["name"]].append(name)
                break
            dep_building = building_to_recipe[get_input(get_building_inputs(dep_building)[0])["name"]]

# now, 
pprint.pprint(clusters)

print("====================")


# a production line is up to 6 belts and what they produce, ordered
# {inputs: set, recipes:[]}

lines = []

order = [[k] + v for (n,k,v) in sorted(((len(v), k, v) for (k,v) in clusters.items()), reverse=True)]

pprint.pprint(order)
print("====================")

clusters = []
for cluster in order:
    inputs = set()
    for recipe_name in cluster:
        recipe = building_to_recipe[recipe_name]
        building_inputs = get_building_inputs(recipe)
        inputs.update([get_input(input)["name"] for input in get_inputs(recipe) if input not in building_inputs])
    clusters.append((len(inputs), inputs, cluster))


for (_, inputs, cluster) in sorted(clusters, reverse=True):
    scheduled = False
    for line in lines:
        missing_inputs = inputs - line["inputs"]
        if len(line["inputs"]) + len(missing_inputs) < 7:
            line["recipes"].extend(cluster)
            line["inputs"].update(missing_inputs)
            scheduled = True
            break
        else:
            continue
    
    if not scheduled:
        lines.append({"inputs": inputs, "recipes": cluster})
        # print(recipe_name, inputs)
        # import pdb;pdb.set_trace()
    # for line in lines



pprint.pprint(lines)
print(len(lines), " lines")
print(len([(get_input(item)["name"], get_input(item)["type"]) for item in item_to_building.keys() if get_input(item)["type"] not in {"LOGISTICS", "PRODUCTION"}]), " inputs")

print("====================")
