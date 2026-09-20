def scan_log(filepath, keys=['ERROR', 'WARNING', 'CRITICAL', 'FAIL'], last_n=100):
    flagged = {}
    with open(filepath, 'r') as f:
        lines = f.readlines()
    
    lines = lines[-last_n:]
    
    for i in lines:
        if(any(keyword in i for keyword in keys)):
            tokens = i.split()
            process = tokens[2]
            message = ' '.join(tokens[4:])
            
            if message in flagged:
                flagged[message]['count'] += 1
                flagged[message]['sources'].add(process)
            else:
                flagged[message] = {'count': 1, 'sources': {process}}
    
    return flagged

if __name__ == "__main__":
    results = scan_log('/var/log/syslog')
    for message, info in results.items():
        print(f"[{info['count']}x] {message}")
        print(f"    Sources: {info['sources']}")
