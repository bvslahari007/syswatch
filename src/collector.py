import time
import shutil
import psutil

#FOR PROCESSES
def list_processes():
	l = []
	procs = list(psutil.process_iter(['pid', 'name']))
	for i in procs:
		i.cpu_percent()
	time.sleep(2)
	for i in procs:
		data = {}
		data['pid'] = i.info['pid']
		data['name'] = i.info['name']
		data['cpu'] = i.cpu_percent()
		data['mem'] = i.memory_percent()
		l.append(data)
	return l

def get_top_consumers(n=5):
	data = list_processes()
	sorted_data = sorted(data, key=lambda x: x['cpu'], reverse=True)
	return sorted_data[:n]

#FOR DISK
#result is in bytes, a named tuple(total, used, free)
def get_disk_stats():
	return shutil.disk_usage('/') #returns the storage stats for the root directory of the OS
def get_disk_percent():
	usage = get_disk_stats()
	disk_used_percent = (usage.used / usage.total) * 100
	return disk_used_percent

#FOR CPU
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

#FOR MEMORY
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
    for p in get_top_consumers():
        print(p)
