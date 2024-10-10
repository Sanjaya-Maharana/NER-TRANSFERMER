import requests
import pandas as pd
import plotly.express as px

# Fetching the data from the API
url = 'https://app.terminal.freightos.com/api/v1/fbx/data?tickers=FBX01&version=monthly&from_date=2024-05-01&to_date=2024-12-31&is_year_over_year=True'

headers = {
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
    'authorization': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6InNhbmpheWFtYWhhcmFuYTE0NUBnbWFpbC5jb20iLCJuYW1lIjoic2FuamF5YW1haGFyYW5hMTQ1QGdtYWlsLmNvbSIsInBlcm1pc3Npb25zIjp7IkZCWCI6eyJwcmVtaXVtIjpmYWxzZSwiY3N2X2Rvd25sb2FkIjpmYWxzZSwiZ2xvYmFsIjp7ImRhaWx5Ijp7Imhpc3RvcmljYWxfZGF0YSI6MCwiaW50ZXJ2YWwiOiJtb250aCIsImRlZmF1bHRfZnJvbV9kYXRlIjpudWxsfSwid2Vla2x5Ijp7Imhpc3RvcmljYWxfZGF0YSI6ImFsbCIsImludGVydmFsIjoiYWxsIiwiZGVmYXVsdF9mcm9tX2RhdGUiOiIyMDE2LTEwLTA3In19LCJ0aWNrZXJzIjp7ImRhaWx5Ijp7Imhpc3RvcmljYWxfZGF0YSI6MCwiaW50ZXJ2YWwiOiJtb250aCIsImRlZmF1bHRfZnJvbV9kYXRlIjoiMjAyNC0wNy0wNSJ9LCJ3ZWVrbHkiOnsiaGlzdG9yaWNhbF9kYXRhIjozLCJpbnRlcnZhbCI6Im1vbnRoIiwiZGVmYXVsdF9mcm9tX2RhdGUiOiIyMDI0LTA3LTA1In19LCJkYWlseSI6ZmFsc2UsIm1hcmtldF91cGRhdGVzIjpmYWxzZSwidHJhbnNpdF90aW1lIjpmYWxzZX0sIkZBWCI6eyJwcmVtaXVtIjpmYWxzZSwiY3N2X2Rvd25sb2FkIjpmYWxzZSwiZ2xvYmFsIjp7ImRhaWx5Ijp7Imhpc3RvcmljYWxfZGF0YSI6MCwiaW50ZXJ2YWwiOiJtb250aCIsImRlZmF1bHRfZnJvbV9kYXRlIjpudWxsfSwid2Vla2x5Ijp7Imhpc3RvcmljYWxfZGF0YSI6ImFsbCIsImludGVydmFsIjoiYWxsIiwiZGVmYXVsdF9mcm9tX2RhdGUiOiIyMDIxLTAxLTAzIn19LCJ0aWNrZXJzIjp7ImRhaWx5Ijp7Imhpc3RvcmljYWxfZGF0YSI6MCwiaW50ZXJ2YWwiOiJtb250aCIsImRlZmF1bHRfZnJvbV9kYXRlIjoiMjAyNC0wNy0wNSJ9LCJ3ZWVrbHkiOnsiaGlzdG9yaWNhbF9kYXRhIjo2LCJpbnRlcnZhbCI6IndlZWsiLCJkZWZhdWx0X2Zyb21fZGF0ZSI6IjIwMjQtMDgtMjQifX0sImRhaWx5IjpmYWxzZSwibWFya2V0X3VwZGF0ZXMiOmZhbHNlLCJ0cmFuc2l0X3RpbWUiOmZhbHNlfSwiTUlSIjp7InByZW1pdW0iOmZhbHNlLCJhbGxvd2VkX3RyYWRlbGFuZXMiOjAsImxhc3RfZWRpdGluZ19kYXRlIjpudWxsLCJkZWZhdWx0X2Zyb21fZGF0ZSI6eyJhaXIiOm51bGwsIm9jZWFuIjpudWxsfSwiaGlzdG9yaWNhbF9kYXRhIjp7ImFpciI6MCwib2NlYW4iOjB9LCJpbnRlcnZhbCI6eyJhaXIiOiJtb250aCIsIm9jZWFuIjoibW9udGgifSwiZGFpbHkiOmZhbHNlLCJtYXJrZXRfdXBkYXRlcyI6ZmFsc2UsImNzdl9kb3dubG9hZCI6ZmFsc2UsInBvcnRfcGVyZm9ybWFuY2UiOmZhbHNlLCJ0cmFuc2l0X3RpbWUiOmZhbHNlfSwiQmVuY2htYXJraW5nIjp7InByZW1pdW0iOmZhbHNlLCJjc3ZfZG93bmxvYWQiOmZhbHNlLCJkYWlseSI6ZmFsc2UsIm1hcmtldF91cGRhdGVzIjpmYWxzZX0sImlzX3N1cGVyX2FkbWluIjpmYWxzZSwic2hvd19iZW5jaG1hcmsiOmZhbHNlfSwic3Vic2NyaXB0aW9uX2xldmVsIjp7fSwic3Vic2NyaXB0aW9uX2RldGFpbHMiOnt9LCJjdXN0b21lcl90eXBlIjoiQ29uc3VsdGluZyBGaXJtIiwiZmJ4X2ZheF9mbGFncyI6eyJmYnhfdGlja2Vyc19jaG9zZW4iOmZhbHNlLCJmYXhfdGlja2Vyc19jaG9zZW4iOmZhbHNlLCJkYXlzX3NpbmNlX2ZpcnN0X2xvZ2luIjowLCJzaG93X21hbmRhdG9yeV9wb3B1cCI6dHJ1ZSwibG9ja19mYnhfdGlja2VycyI6ZmFsc2UsImxvY2tfZmF4X3RpY2tlcnMiOmZhbHNlLCJmYnhfdGlja2VycyI6W10sImZheF90aWNrZXJzIjpbXSwiZmJ4X3ByZW1pdW0iOmZhbHNlLCJmYXhfcHJlbWl1bSI6ZmFsc2V9LCJleHAiOjE3Mjk1Nzc4MDQsImlzX25ld191c2VyIjpmYWxzZX0.mAvPfL0Q_gFPg3OM8Q_gdxs5EtUMiG_0iKbX2oi-V3k'
}

response = requests.get(url, headers=headers)

# Check the status code
if response.status_code == 200:
    data = response.json()
else:
    print(f"Failed to fetch data. Status code: {response.status_code}")

# Extract the relevant data from the response
data = data['indexPoints']

for row in data:
    print(row)

# Convert the data into a pandas DataFrame
df = pd.DataFrame(data)

# Convert 'month' column to datetime and ensure the data is sorted by month
df['month'] = pd.to_datetime(df['month'])
df = df.sort_values(by='month')

# Create the interactive bar chart using Plotly Express
fig = px.bar(df, x='month', y='value', title='Freightos Baltic Index (FBX) Over Time',
             labels={'value': 'FBX Value', 'month': 'Month'},
             height=600)

# Update the y-axis to display two decimal places
fig.update_traces(hovertemplate='%{x}: %{y:.2f}')

# Show the interactive plot
fig.show()


{
  "status": true,
  "data": [
"2017": [
      {
        "ticker": "FBX",
        "month": "01-01-2017",
        "value": 1334.91
      },
      {
        "ticker": "FBX",
        "month": "01-02-2017",
        "value": 1574.48
      }
    ],
    "2018": [
      {
        "ticker": "FBX",
        "month": "01-01-2018",
        "value": 1400.00
      }
    ]
  ]
}
