import json
 
# Data to be written
dictionary = {
    "C": [40, 255, 0, 255],
    
}
 
# Serializing json
json_object = json.dumps(dictionary, indent=4)
 
# Writing to sample.json
with open("sample.json", "w") as outfile:
    outfile.write(json_object)