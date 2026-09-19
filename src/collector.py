import time
import shutil

#result is in bytes, a named tuple(total, used, free)
def get_disk_stats():
	return shutil.disk_usage('/') #returns the storage stats for the root directory of the OS
def get_disk_percent():
	usage = get_disk_stats()
	disk_used_percent = (usage.used / usage.total) * 100
	return disk_used_percent

def read_cpu_times():
	with open('/proc/stat', 'r') as f:
		line = f.readline()
	tokens = line.split()
	vals = [int(i) for i in tokens[1:]]
	return vals

def get_cpu_percent():
	first = read_cpu_times()
	time.sleep(1)
	second = read_cpu_times()
	
	total_delta = sum(second) - sum(first)
	idle_delta = second[3] - first[3]
	usage_pcent = ((total_delta - idle_delta) / total_delta)*100
	return usage_pcent

def read_mem_info():
	data = {}	
	with open('/proc/meminfo', 'r') as f:
		lines = f.readlines()
	for i in lines:
		i = i.strip()
		i_clean = [j for j in i.split(' ') if (j != '' and j != 'kB')]
		if(i_clean[0].rstrip(':') == 'MemTotal'):
			data['MemTotal'] = int(i_clean[1])
		elif(i_clean[0].rstrip(':') == 'MemAvailable'):
			data['MemAvailable'] = int(i_clean[1])
	return data

def get_mem_percent():
	data = read_mem_info()
	mem_percent = ((data['MemTotal'] - data['MemAvailable'])/(data['MemTotal']))*100
	return mem_percent



if __name__ == "__main__":
	print(get_disk_stats())
	print(get_disk_percent())
