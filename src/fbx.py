import copy
import traceback
import requests
import pandas as pd
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

url = 'https://app.terminal.freightos.com/api/v1/fbx/data?tickers=FBX&version=monthly&from_date=1000-05-01&to_date=2040-12-31&is_year_over_year=True'

authorization = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6InNhbmpheWEudGhlb2NlYW5uQGdtYWlsLmNvbSIsIm5hbWUiOiJzYW5qYXlhIG1haGFyYW5hIiwicGVybWlzc2lvbnMiOnsiRkJYIjp7InByZW1pdW0iOmZhbHNlLCJjc3ZfZG93bmxvYWQiOmZhbHNlLCJnbG9iYWwiOnsiZGFpbHkiOnsiaGlzdG9yaWNhbF9kYXRhIjowLCJpbnRlcnZhbCI6Im1vbnRoIiwiZGVmYXVsdF9mcm9tX2RhdGUiOm51bGx9LCJ3ZWVrbHkiOnsiaGlzdG9yaWNhbF9kYXRhIjoiYWxsIiwiaW50ZXJ2YWwiOiJhbGwiLCJkZWZhdWx0X2Zyb21fZGF0ZSI6IjIwMTYtMTAtMDcifX0sInRpY2tlcnMiOnsiZGFpbHkiOnsiaGlzdG9yaWNhbF9kYXRhIjowLCJpbnRlcnZhbCI6Im1vbnRoIiwiZGVmYXVsdF9mcm9tX2RhdGUiOiIyMDI0LTA3LTEzIn0sIndlZWtseSI6eyJoaXN0b3JpY2FsX2RhdGEiOjMsImludGVydmFsIjoibW9udGgiLCJkZWZhdWx0X2Zyb21fZGF0ZSI6IjIwMjQtMDctMTMifX0sImRhaWx5IjpmYWxzZSwibWFya2V0X3VwZGF0ZXMiOmZhbHNlLCJ0cmFuc2l0X3RpbWUiOmZhbHNlfSwiRkFYIjp7InByZW1pdW0iOmZhbHNlLCJjc3ZfZG93bmxvYWQiOmZhbHNlLCJnbG9iYWwiOnsiZGFpbHkiOnsiaGlzdG9yaWNhbF9kYXRhIjowLCJpbnRlcnZhbCI6Im1vbnRoIiwiZGVmYXVsdF9mcm9tX2RhdGUiOm51bGx9LCJ3ZWVrbHkiOnsiaGlzdG9yaWNhbF9kYXRhIjoiYWxsIiwiaW50ZXJ2YWwiOiJhbGwiLCJkZWZhdWx0X2Zyb21fZGF0ZSI6IjIwMjEtMDEtMDMifX0sInRpY2tlcnMiOnsiZGFpbHkiOnsiaGlzdG9yaWNhbF9kYXRhIjowLCJpbnRlcnZhbCI6Im1vbnRoIiwiZGVmYXVsdF9mcm9tX2RhdGUiOiIyMDI0LTA3LTEzIn0sIndlZWtseSI6eyJoaXN0b3JpY2FsX2RhdGEiOjYsImludGVydmFsIjoid2VlayIsImRlZmF1bHRfZnJvbV9kYXRlIjoiMjAyNC0wOS0wMSJ9fSwiZGFpbHkiOmZhbHNlLCJtYXJrZXRfdXBkYXRlcyI6ZmFsc2UsInRyYW5zaXRfdGltZSI6ZmFsc2V9LCJNSVIiOnsicHJlbWl1bSI6ZmFsc2UsImFsbG93ZWRfdHJhZGVsYW5lcyI6MCwibGFzdF9lZGl0aW5nX2RhdGUiOm51bGwsImRlZmF1bHRfZnJvbV9kYXRlIjp7ImFpciI6bnVsbCwib2NlYW4iOm51bGx9LCJoaXN0b3JpY2FsX2RhdGEiOnsiYWlyIjowLCJvY2VhbiI6MH0sImludGVydmFsIjp7ImFpciI6Im1vbnRoIiwib2NlYW4iOiJtb250aCJ9LCJkYWlseSI6ZmFsc2UsIm1hcmtldF91cGRhdGVzIjpmYWxzZSwiY3N2X2Rvd25sb2FkIjpmYWxzZSwicG9ydF9wZXJmb3JtYW5jZSI6ZmFsc2UsInRyYW5zaXRfdGltZSI6ZmFsc2V9LCJCZW5jaG1hcmtpbmciOnsicHJlbWl1bSI6ZmFsc2UsImNzdl9kb3dubG9hZCI6ZmFsc2UsImRhaWx5IjpmYWxzZSwibWFya2V0X3VwZGF0ZXMiOmZhbHNlfSwiaXNfc3VwZXJfYWRtaW4iOmZhbHNlLCJzaG93X2JlbmNobWFyayI6ZmFsc2V9LCJzdWJzY3JpcHRpb25fbGV2ZWwiOnt9LCJzdWJzY3JpcHRpb25fZGV0YWlscyI6e30sImN1c3RvbWVyX3R5cGUiOiJTb2Z0d2FyZSBQcm92aWRlciIsImZieF9mYXhfZmxhZ3MiOnsiZmJ4X3RpY2tlcnNfY2hvc2VuIjpmYWxzZSwiZmF4X3RpY2tlcnNfY2hvc2VuIjpmYWxzZSwiZGF5c19zaW5jZV9maXJzdF9sb2dpbiI6Nywic2hvd19tYW5kYXRvcnlfcG9wdXAiOnRydWUsImxvY2tfZmJ4X3RpY2tlcnMiOmZhbHNlLCJsb2NrX2ZheF90aWNrZXJzIjpmYWxzZSwiZmJ4X3RpY2tlcnMiOltdLCJmYXhfdGlja2VycyI6W10sImZieF9wcmVtaXVtIjpmYWxzZSwiZmF4X3ByZW1pdW0iOmZhbHNlfSwiaXNfbmV3X3VzZXIiOmZhbHNlLCJleHAiOjE3MzAzNTU1NzV9.XX_H6soPiRG2FzunZ_moG4nG5rGY4ue6H1wknRQlAKw'

headers = {
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
    'authorization': authorization,
    'cookie': '_vwo_uuid_v2=D439D082C623162D76F3D0C2014E3C8F0|052100bc058e30ef327d925439ef36dc; _vwo_uuid=D439D082C623162D76F3D0C2014E3C8F0',
    'priority': 'u=1, i',
    'referer': 'https://app.terminal.freightos.com/fbx?ticker=%5B%22FBX%22%5D&frequency=%22weekly%22',
    'sec-ch-ua': '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36'
}


def fetch_fbx_data(from_date, to_date, key, index):
    try:
        grouped_data = {}
        global url, headers
        url_child = copy.copy(url)
        if index and index != '':
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
            volatility = data.get('date_range_level_volatility', {})
            if volatility:
                if index:
                    volatility = volatility.get(index, {})
                else:
                    volatility = volatility.get('FBX', {})
            df = pd.DataFrame(fbx_data)
            try:
                df['month'] = pd.to_datetime(df['indexDate'])
            except:
                df['month'] = pd.to_datetime(df['month'])
            df['year'] = df['month'].dt.year
            if from_year:
                df = df[(df['year'] >= from_year) & (df['year'] <= current_year)]
            df['month'] = df['month'].dt.strftime('%d-%m-%Y')
            df['value'] = df['value'].round(2)
            df = df.sort_values(by='month')
            for year, group in df.groupby('year'):
                grouped_data[year] = group.drop(columns=['year']).to_dict(orient='records')
            return {"status": True, "data": grouped_data, "volatility": volatility}
        else:
            return {"status": False, "error": f"Failed to fetch data. Status code: {response.status_code}"}
    except Exception as e:
        print(traceback.print_exc())
        return {"status": False, "error": str(e)}




def fetch_fbx_filter_data(key, value, url, headers):
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
                return {"category": "pacific", "index":key, "index_value": value, "max_value": max_val_rounded,
                        "percentage_diff": percentage_diff_rounded}
    except Exception as e:
        print(f"Error fetching data for {key}: {e}")
        return None


def fetch_all_fbx_filters():
    try:
        global url, headers
        result_data = {"global": [], "pacific": []}
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
            futures = [executor.submit(fetch_fbx_filter_data, key, value, url, headers) for key, value in
                       freight_indexes.items()]
            for future in futures:
                result = future.result()
                if result:
                    if result['category'] == 'global':
                        result_data['global'].append(result)
                    else:
                        result_data['pacific'].append(result)
        return {"status": True, "data": result_data}
    except Exception as e:
        print(traceback.print_exc())
        return {"status": False, "error": str(e)}