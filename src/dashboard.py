from flask import Flask, render_template
import sys

sys.path.append('.') #look for files present in this directory
from collector import get_cpu_percent, get_mem_percent, get_disk_percent, get_top_consumers
from alerts import check_threshold

app = Flask(__name__) #creates the actual web app object

@app.route('/') #decorator
def home():
	procs = get_top_consumers()
	cpu = get_cpu_percent()
	mem = get_mem_percent()
	disk = get_disk_percent()
	a = check_threshold(cpu, mem, disk)
	return render_template('index.html', cpu=cpu, mem=mem, disk=disk, procs=procs, ale=a)

if __name__ == '__main__':
	app.run(debug=True)
