import sqlite3
import os, sys
import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, '..', 'data', 'syswatch.db')

def init_db(db_path=DB_PATH):
	conn = sqlite3.connect(db_path)
	cur = conn.cursor()
	cur.execute('''
		CREATE TABLE IF NOT EXISTS metrics(
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		timestamp TEXT,
		cpu_percent REAL,
		mem_percent REAL,
		disk_percent REAL
		)
	''')
	conn.commit()
	conn.close()


def save_metrics(cpu, mem, disk, db_path=DB_PATH):
	conn = sqlite3.connect(db_path)
	cur = conn.cursor()
	timestamp = datetime.datetime.now().isoformat()

	cur.execute('''
	INSERT INTO metrics (timestamp, cpu_percent, mem_percent, disk_percent)
	VALUES  (?, ?, ?, ?)
	
''', (timestamp, cpu, mem, disk)) #don't use f"" strings, it's not recommended
	conn.commit()
	conn.close()

def get_recent_metrics(limit=10, db_path=DB_PATH):
	conn = sqlite3.connect(db_path)
	cur = conn.cursor()
	cur.execute('''
		SELECT * 
		FROM metrics
		ORDER BY id DESC limit ?
	''', (limit, ))
	rows = cur.fetchall()
	conn.close()
	return rows 

if __name__ == '__main__':
	import sys
	#sys.path.append(.)
	from collector import get_cpu_percent, get_mem_percent, get_disk_percent
	init_db()
	cpu = get_cpu_percent()
	mem = get_mem_percent()
	disk = get_disk_percent()
	save_metrics(cpu, mem, disk)
	print(get_recent_metrics())
