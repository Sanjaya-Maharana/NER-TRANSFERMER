import json
from datetime import datetime, timedelta
from pathlib import Path

def get_ist_time():
    utc_time = datetime.utcnow()
    ist_time = utc_time + timedelta(hours=5, minutes=30)
    return ist_time.strftime('%Y-%m-%d %H:%M:%S')


stats_file_path = Path('api_status.json')

if not stats_file_path.exists():
    initial_data = {
        'timestamp': {'timestamp': get_ist_time()},
        'tonnage': {'count': 0, 'last_called': None},
        'cargo': {'count': 0, 'last_called': None}
    }
    with open(stats_file_path, 'w') as f:
        json.dump(initial_data, f, indent=4)


# Function to update API stats
def update_api_stats(api_name):
    with open(stats_file_path, 'r+') as f:
        data = json.load(f)
        if api_name not in data:
            data[api_name] = {'count': 0, 'last_called': None}
        data[api_name]['count'] += 1
        data[api_name]['last_called'] = get_ist_time()
        f.seek(0)
        json.dump(data, f, indent=4)
        f.truncate()