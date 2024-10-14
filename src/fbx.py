import copy
import traceback
import requests
import pandas as pd
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
url = 'https://app.terminal.freightos.com/api/v1/fbx/data?tickers=FBX&version=monthly&from_date=1000-05-01&to_date=2040-12-31&is_year_over_year=True'

headers = {
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
    'authorization': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6InNhbmpheWFtYWhhcmFuYTE0NUBnbWFpbC5jb20iLCJuYW1lIjoic2FuamF5YW1haGFyYW5hMTQ1QGdtYWlsLmNvbSIsInBlcm1pc3Npb25zIjp7IkZCWCI6eyJwcmVtaXVtIjpmYWxzZSwiY3N2X2Rvd25sb2FkIjpmYWxzZSwiZ2xvYmFsIjp7ImRhaWx5Ijp7Imhpc3RvcmljYWxfZGF0YSI6MCwiaW50ZXJ2YWwiOiJtb250aCIsImRlZmF1bHRfZnJvbV9kYXRlIjpudWxsfSwid2Vla2x5Ijp7Imhpc3RvcmljYWxfZGF0YSI6ImFsbCIsImludGVydmFsIjoiYWxsIiwiZGVmYXVsdF9mcm9tX2RhdGUiOiIyMDE2LTEwLTA3In19LCJ0aWNrZXJzIjp7ImRhaWx5Ijp7Imhpc3RvcmljYWxfZGF0YSI6MCwiaW50ZXJ2YWwiOiJtb250aCIsImRlZmF1bHRfZnJvbV9kYXRlIjoiMjAyNC0wNy0wNSJ9LCJ3ZWVrbHkiOnsiaGlzdG9yaWNhbF9kYXRhIjozLCJpbnRlcnZhbCI6Im1vbnRoIiwiZGVmYXVsdF9mcm9tX2RhdGUiOiIyMDI0LTA3LTA1In19LCJkYWlseSI6ZmFsc2UsIm1hcmtldF91cGRhdGVzIjpmYWxzZSwidHJhbnNpdF90aW1lIjpmYWxzZX0sIkZBWCI6eyJwcmVtaXVtIjpmYWxzZSwiY3N2X2Rvd25sb2FkIjpmYWxzZSwiZ2xvYmFsIjp7ImRhaWx5Ijp7Imhpc3RvcmljYWxfZGF0YSI6MCwiaW50ZXJ2YWwiOiJtb250aCIsImRlZmF1bHRfZnJvbV9kYXRlIjpudWxsfSwid2Vla2x5Ijp7Imhpc3RvcmljYWxfZGF0YSI6ImFsbCIsImludGVydmFsIjoiYWxsIiwiZGVmYXVsdF9mcm9tX2RhdGUiOiIyMDIxLTAxLTAzIn19LCJ0aWNrZXJzIjp7ImRhaWx5Ijp7Imhpc3RvcmljYWxfZGF0YSI6MCwiaW50ZXJ2YWwiOiJtb250aCIsImRlZmF1bHRfZnJvbV9kYXRlIjoiMjAyNC0wNy0wNSJ9LCJ3ZWVrbHkiOnsiaGlzdG9yaWNhbF9kYXRhIjo2LCJpbnRlcnZhbCI6IndlZWsiLCJkZWZhdWx0X2Zyb21fZGF0ZSI6IjIwMjQtMDgtMjQifX0sImRhaWx5IjpmYWxzZSwibWFya2V0X3VwZGF0ZXMiOmZhbHNlLCJ0cmFuc2l0X3RpbWUiOmZhbHNlfSwiTUlSIjp7InByZW1pdW0iOmZhbHNlLCJhbGxvd2VkX3RyYWRlbGFuZXMiOjAsImxhc3RfZWRpdGluZ19kYXRlIjpudWxsLCJkZWZhdWx0X2Zyb21fZGF0ZSI6eyJhaXIiOm51bGwsIm9jZWFuIjpudWxsfSwiaGlzdG9yaWNhbF9kYXRhIjp7ImFpciI6MCwib2NlYW4iOjB9LCJpbnRlcnZhbCI6eyJhaXIiOiJtb250aCIsIm9jZWFuIjoibW9udGgifSwiZGFpbHkiOmZhbHNlLCJtYXJrZXRfdXBkYXRlcyI6ZmFsc2UsImNzdl9kb3dubG9hZCI6ZmFsc2UsInBvcnRfcGVyZm9ybWFuY2UiOmZhbHNlLCJ0cmFuc2l0X3RpbWUiOmZhbHNlfSwiQmVuY2htYXJraW5nIjp7InByZW1pdW0iOmZhbHNlLCJjc3ZfZG93bmxvYWQiOmZhbHNlLCJkYWlseSI6ZmFsc2UsIm1hcmtldF91cGRhdGVzIjpmYWxzZX0sImlzX3N1cGVyX2FkbWluIjpmYWxzZSwic2hvd19iZW5jaG1hcmsiOmZhbHNlfSwic3Vic2NyaXB0aW9uX2xldmVsIjp7fSwic3Vic2NyaXB0aW9uX2RldGFpbHMiOnt9LCJjdXN0b21lcl90eXBlIjoiQ29uc3VsdGluZyBGaXJtIiwiZmJ4X2ZheF9mbGFncyI6eyJmYnhfdGlja2Vyc19jaG9zZW4iOmZhbHNlLCJmYXhfdGlja2Vyc19jaG9zZW4iOmZhbHNlLCJkYXlzX3NpbmNlX2ZpcnN0X2xvZ2luIjowLCJzaG93X21hbmRhdG9yeV9wb3B1cCI6dHJ1ZSwibG9ja19mYnhfdGlja2VycyI6ZmFsc2UsImxvY2tfZmF4X3RpY2tlcnMiOmZhbHNlLCJmYnhfdGlja2VycyI6W10sImZheF90aWNrZXJzIjpbXSwiZmJ4X3ByZW1pdW0iOmZhbHNlLCJmYXhfcHJlbWl1bSI6ZmFsc2V9LCJleHAiOjE3Mjk1Nzc4MDQsImlzX25ld191c2VyIjpmYWxzZX0.mAvPfL0Q_gFPg3OM8Q_gdxs5EtUMiG_0iKbX2oi-V3k'
}


def fetch_fbx_data(from_date, to_date, key, index):
    try:
        global url, headers
        url_child = copy.copy(url)
        if index:
            url_child = url_child.replace('FBX', index)
        current_year = datetime.now().year
        from_year = None
        if key.lower() != 'all':
            try:
                years = int(key.replace('y', ''))
                from_year = current_year - years
            except ValueError:
                pass
        if from_date:
            url_child = url_child.replace('1000-05-01', from_date)
        if to_date:
            url_child = url_child.replace('2040-12-31', to_date)
        print(url_child)
        response = requests.get(url_child, headers=headers)
        if response.status_code == 200:
            data = response.json()
            fbx_data = data.get('indexPoints', [])
            df = pd.DataFrame(fbx_data)
            df['month'] = pd.to_datetime(df['month'])
            df['year'] = df['month'].dt.year
            if from_year:
                df = df[(df['year'] >= from_year) & (df['year'] <= current_year)]
            df['month'] = df['month'].dt.strftime('%d-%m-%Y')
            df['value'] = df['value'].round(2)
            df = df.sort_values(by='month')
            grouped_data = {}
            for year, group in df.groupby('year'):
                grouped_data[year] = group.drop(columns=['year']).to_dict(orient='records')
            return {"status": True, "data": grouped_data}
        else:
            return {"status": False, "error": f"Failed to fetch data. Status code: {response.status_code}"}
    except Exception as e:
        print(traceback.print_exc())
        return {"status": False, "error": str(e)}





def fetch_fbx_data(key, value, url, headers):
    try:
        url_child = url.replace('FBX', key)
        response = requests.get(url_child, headers=headers)
        if response.status_code == 200:
            data = response.json()
            fbx_data = data.get('indexPoints', [])
            max_value = fbx_data[-1]
            min_value = fbx_data[-2]
            max_val = max_value['value']
            min_val = min_value['value']
            max_val_rounded = round(max_val, 2)
            percentage_diff = ((max_val - min_val) / min_val) * 100
            percentage_diff_rounded = round(percentage_diff, 2)
            if key == "FBX":
                return {"category": "global", "index":key, "index_value": value, "max_value": max_val_rounded,
                        "percentage_diff": percentage_diff_rounded}
            else:
                return {"category": "spacific", "index":key, "index_value": value, "max_value": max_val_rounded,
                        "percentage_diff": percentage_diff_rounded}
    except Exception as e:
        print(f"Error fetching data for {key}: {e}")
        return None


def fetch_all_fbx_filters():
    try:
        global url, headers
        result_data = {"global": [], "spacific": []}
        freight_indexes = {
            "FBX": "Global Container Freight Index",
            "FBX01": "China/East Asia - North America West Coast",
            "FBX02": "North America West Coast - China/East Asia",
            "FBX03": "China/East Asia - North America East Coast",
            "FBX04": "North America East Coast - China/East Asia",
            "FBX11": "China/East Asia - North Europe",
            "FBX12": "North Europe - China/East Asia",
            "FBX13": "China/East Asia - Mediterranean",
            "FBX14": "Mediterranean - China/East Asia",
            "FBX21": "North America East Coast - North Europe",
            "FBX22": "North Europe - North America East Coast",
            "FBX24": "Europe - South America East Coast",
            "FBX26": "Europe - South America West Coast"
        }
        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(fetch_fbx_data, key, value, url, headers) for key, value in
                       freight_indexes.items()]
            for future in futures:
                result = future.result()
                if result:
                    if result['category'] == 'global':
                        result_data['global'].append(result)
                    else:
                        result_data['spacific'].append(result)
        return {"status": True, "data": result_data}
    except Exception as e:
        print(traceback.print_exc())
        return {"status": False, "error": str(e)}
