def read_cpu_times():
	with open('/proc/stat', 'r') as f:
		line = f.readline()
	tokens = line.split()
	vals = [int(i) for i in tokens[1:]]
	return vals

def 


if __name__ == "__main__":
	print(read_cpu_times())
