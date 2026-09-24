import sys, os, time
from collector import get_cpu_percent, get_mem_percent, get_disk_percent
from storage import init_db, save_metrics
from alerts import show_alerts

def main():
    init_db()

    while True:
        cpu = get_cpu_percent()
        mem = get_mem_percent()
        disk = get_disk_percent()

        save_metrics(cpu, mem, disk)
        show_alerts(cpu, mem, disk)

        time.sleep(5)

if __name__ == '__main__':
    main()