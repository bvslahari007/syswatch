CPU_THRESHOLD = 80
MEM_THRESHOLD = 85
DISK_THRESHOLD = 85


def check_threshold(cpu, mem, disk):
	alerts = []
	if(cpu > CPU_THRESHOLD):
		alerts.append(f"CPU usage CRITICAL: {cpu}%. (THRESHOLD {CPU_THRESHOLD})")
	if(disk > DISK_THRESHOLD):
                alerts.append(f"DISK usage CRITICAL: {disk}%. (THRESHOLD {DISK_THRESHOLD})")
	if(mem > MEM_THRESHOLD):
                alerts.append(f"MEMORY usage CRITICAL: {mem}%. (THRESHOLD {MEM_THRESHOLD})")
	return alerts

def show_alerts(cpu, mem, disk):
	alerts = check_threshold(cpu, mem, disk)
	if len(alerts) <= 0:
		print("All resources (CPU, RAM, Disk) are nominal. No thresholds crossed")
	else:
		for i in alerts:
			print(i)
	

if __name__ == '__main__':
	#test here
	import sys
	sys.path.append('.')
	from collector import  get_cpu_percent, get_mem_percent, get_disk_percent
	
	cpu = get_cpu_percent()
	mem = get_mem_percent()
	disk = get_disk_percent()
	show_alerts(cpu, mem, disk)

