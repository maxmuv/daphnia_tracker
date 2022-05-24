import json
import sys

if __name__ == "__main__":
	if (len(sys.argv) != 3):
		print("usage: python3 markup.py /path/to/orig/json path/to/mod/json")
		exit()
	json_file = sys.argv[1]
	written_file = sys.argv[2]
	with open(json_file, "r") as read_file:
		data = json.load(read_file)

		print(data)
		metadata = data["_via_img_metadata"]
		ks= data["_via_image_id_list"]
		i = 0
		for k in ks:
			fn = metadata[k]["filename"]
			if (fn != k):
				metadata[fn] = metadata[k]
				metadata.pop(k)
				ks[i] = fn
			i+=1
		with open(written_file, "w") as written_file:
			json.dump(data, written_file,  indent=4) 
