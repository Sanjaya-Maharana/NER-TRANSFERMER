import json
import math
import numpy as np
import pandas as pd
import traceback

from fastapi.logger import logger
from pymongo import MongoClient
from src.status import update_api_stats
from datetime import datetime, timedelta,date
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi.responses import JSONResponse
from sklearn.linear_model import LinearRegression
from src.authontication import decode_jwt_token
from fastapi import HTTPException
import aioredis

client = AsyncIOMotorClient('mongodb+srv://theoceann:UPYLXvOujwCeARDO@oceannmail-staging.tamt4.mongodb.net/')

redis = aioredis.from_url("redis://47.128.206.58:6380/0")

def custom_json_converter(obj):
    if isinstance(obj, (pd.Timestamp, datetime)):
        return obj.isoformat()
    elif isinstance(obj, date):
        return obj.isoformat()
    raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")


def normalize_date_filter(date_filter):
    if 'Formatted_Date' in date_filter:
        date_gte = datetime.fromtimestamp(date_filter['Formatted_Date']['$gte']).date()
        date_lte = datetime.fromtimestamp(date_filter['Formatted_Date']['$lte']).date()

        date_filter['Formatted_Date'] = {
            '$gte': int(datetime.combine(date_gte, datetime.min.time()).timestamp()),
            '$lte': int(datetime.combine(date_lte, datetime.min.time()).timestamp())
        }

    return date_filter

async def get_data_with_cache(cache_key):
    logger.info(f"redis key: {cache_key}")
    cached_data = await redis.get(cache_key)
    if cached_data:
        logger.info("using catch")
        return json.loads(cached_data)
    else:
        logger.info("using db")


def create_bins_and_labels(min_value, max_value, step=500001):
    min_value = 0
    max_value = math.ceil(max_value / step) * step
    bins = list(range(min_value, max_value + step, step))
    labels = [f'{bins[i]}-{bins[i + 1] - 1} MT' for i in range(len(bins) - 1)]
    return bins, labels

def predict_next_weeks(df, target_column='dwt', num_weeks=3):
    df['Date_ordinal'] = pd.to_datetime(df['Date']).apply(lambda x: x.toordinal())
    X = df['Date_ordinal'].values.reshape(-1, 1)
    y = df[target_column].values
    model = LinearRegression()
    model.fit(X, y)
    last_date = df['Date'].max()
    future_dates = [(last_date + timedelta(weeks=i)).toordinal() for i in range(1, num_weeks + 1)]
    future_dates = np.array(future_dates).reshape(-1, 1)
    predictions = model.predict(future_dates)
    rounded_predictions = np.round(predictions).astype(int)

    future_predictions = {
        str(last_date + timedelta(weeks=i)): prediction
        for i, prediction in enumerate(rounded_predictions, 1)
    }

    return future_predictions

def convert_numpy_to_python(data):
    if isinstance(data, dict):
        return {key: convert_numpy_to_python(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [convert_numpy_to_python(item) for item in data]
    elif isinstance(data, np.generic):
        return data.item()
    else:
        return data

async def plot_data_fun(request_data):
    try:
        token = getattr(request_data, 'token', None)
        if token:
            decoded_token = decode_jwt_token(token)
            company = decoded_token.get("company_name", None)
            if company:
                db_name = company.lower()
            else:
                db_name = 'theoceann'
        else:
            db_name = getattr(request_data, 'client', 'theoceann')

        update_api_stats(db_name)
        database = client[db_name]

        end_date = datetime.now()
        start_date = end_date - timedelta(weeks=6)
        from_unix = int(start_date.timestamp())
        to_unix = int(end_date.timestamp())

        # Date filter for MongoDB
        date_filter = {
            'Formatted_Date': {
                '$gte': from_unix,
                '$lte': to_unix
            }
        }

        if request_data.type == 'tonnage':
            collection = database['tonnage']
            if request_data.vessel_name:
                date_filter['vessel_name'] = request_data.vessel_name.lower()
            if request_data.vessel_type:
                date_filter['vessel_type'] = request_data.vessel_type
            if request_data.sub_vessel_type:
                date_filter['sub_vessel_type'] = request_data.sub_vessel_type
            if request_data.new_open_port:
                date_filter['new_open_port'] = request_data.new_open_port
            if request_data.new_open_date:
                from_date, to_date = request_data.new_open_date.split('/')
                from_dt = datetime.strptime(from_date, "%Y-%m-%d")
                to_dt = datetime.strptime(to_date, "%Y-%m-%d")
                date_filter['new_open_date'] = {
                    '$gte': int(from_dt.timestamp()),
                    '$lte': int(to_dt.timestamp())
                }

            date_filter['dwt'] = {"$lt": 10000000}
            normalized_filter = normalize_date_filter(date_filter)
            cache_key = f"tonnage:{db_name}:{hash(str(normalized_filter))}"
            data = await get_data_with_cache(cache_key)
            if data:
                return data
            tonnage_data = await collection.find(
                date_filter,
                {'_id': 0, 'vessel_name': 1, 'vessel_type': 1, 'Formatted_Date': 1, 'dwt': 1, 'new_open_port': 1}
            ).limit(50000).to_list(50000)

            if not tonnage_data:
                return JSONResponse(status_code=200, content={"data": {}, "status": False, "message": "No data found"})

            df = pd.DataFrame(tonnage_data)

            if 'Formatted_Date' in df.columns:
                df['Formatted_Date'] = pd.to_datetime(df['Formatted_Date'], unit='s', errors='coerce').fillna(pd.NaT)
            else:
                return JSONResponse(status_code=200, content={"data": {}, "status": True, "message": "Data not found"})

            df['dwt'] = pd.to_numeric(df['dwt'], errors='coerce').fillna(0)
            df['Date'] = df['Formatted_Date'].dt.date
            df['Week'] = pd.to_datetime(df['Formatted_Date']).dt.to_period('W').apply(lambda r: r.start_time)
            min_dwt = df['dwt'].min()
            max_dwt = df['dwt'].max()
            bins, labels = create_bins_and_labels(min_dwt, max_dwt, step=2000001)

            df['dwt_bins'] = pd.cut(df['dwt'], bins=bins, labels=labels)
            grouped_data = {}
            for week, group in df.groupby('Week'):
                week_group = {}
                for label in labels:
                    vessels_in_bin = group[group['dwt_bins'] == label].to_dict(orient='records')
                    week_group[label] = vessels_in_bin
                grouped_data[str(week.date())] = week_group

            predictions = predict_next_weeks(df, target_column='dwt')

            grouped_data = convert_numpy_to_python(grouped_data)
            predictions = convert_numpy_to_python(predictions)
            data = {"data": grouped_data, "predictions": predictions, "status": True, "type": "tonnage"}
            await redis.set(cache_key, json.dumps(data, default=custom_json_converter), ex=3600)
            return data

        elif request_data.type == 'cargo':
            collection = database['cargo']
            if request_data.cargo_name:
                date_filter['cargo'] = request_data.cargo_name
            if request_data.cargo_type:
                date_filter['cargo_type'] = request_data.cargo_type
            if request_data.load_port:
                date_filter['load_port.port'] = request_data.load_port

            date_filter['cargo_size'] = {"$lt": 10000000}
            normalized_filter = normalize_date_filter(date_filter)
            cache_key = f"cargo:{db_name}:{hash(str(normalized_filter))}"
            data = await get_data_with_cache(cache_key)
            if data:
                return data
            cargo_data = await collection.find(date_filter, {
                '_id': 0, 'cargo': 1, 'cargo_type': 1, 'Formatted_Date': 1, 'cargo_size': 1, 'load_port': 1
            }).limit(50000).to_list(50000)

            if not cargo_data:
                return JSONResponse(status_code=200, content={"data": {}, "status": False, "message": "No data found"})

            df = pd.DataFrame(cargo_data)

            if 'Formatted_Date' in df.columns:
                df['Formatted_Date'] = pd.to_datetime(df['Formatted_Date'], unit='s', errors='coerce').fillna(pd.NaT)
            else:
                return JSONResponse(status_code=200, content={"data": {}, "status": True, "message": "Data not found"})
            df['cargo_size'] = pd.to_numeric(df['cargo_size'], errors='coerce').fillna(0)
            df['Date'] = df['Formatted_Date'].dt.date
            df['Week'] = pd.to_datetime(df['Formatted_Date']).dt.to_period('W').apply(lambda r: r.start_time)

            min_cargo_size = df['cargo_size'].min()
            max_cargo_size = df['cargo_size'].max()
            bins, labels = create_bins_and_labels(min_cargo_size, max_cargo_size, step=2000001)
            df['cargo_bins'] = pd.cut(df['cargo_size'], bins=bins, labels=labels)
            grouped_data = {}
            for week, group in df.groupby('Week'):
                week_group = {}
                for label in labels:
                    cargos_in_bin = group[group['cargo_bins'] == label].to_dict(orient='records')
                    week_group[label] = cargos_in_bin
                grouped_data[str(week.date())] = week_group
            predictions = predict_next_weeks(df, target_column='cargo_size')
            grouped_data = convert_numpy_to_python(grouped_data)
            predictions = convert_numpy_to_python(predictions)
            data = {"data": grouped_data, "predictions": predictions, "status": True, "type": "cargo"}
            await redis.set(cache_key, json.dumps(data, default=custom_json_converter), ex=3600)
            return data

        else:
            raise HTTPException(status_code=400, detail="Invalid request type")

    except Exception as e:
        logger.info(traceback.print_exc())
        return JSONResponse(content={"error": str(e), "status": False})



def filter_ports(port_list):
    return [port for port in port_list if isinstance(port, str) and port.strip() and port.lower() != 'n/a']


def handle_data(request_data):
    client = MongoClient('mongodb+srv://theoceann:UPYLXvOujwCeARDO@oceannmail-staging.tamt4.mongodb.net/')

    try:
        token = getattr(request_data, 'token', None)
        if token:
            decoded_token = decode_jwt_token(token)
            company = decoded_token.get("company_name", None)
            if company:
                db_name = company.lower()
            else:
                db_name = 'theoceann'
        else:
            db_name = getattr(request_data, 'client', 'theoceann')

        update_api_stats(db_name)
        db = client[db_name]
        end_date = datetime.now()
        start_date = end_date - timedelta(weeks=8)
        from_unix = int(start_date.timestamp())
        to_unix = int(end_date.timestamp())

        if request_data.type == 'tonnage':
            collection = db['tonnage']
            vessel_name_list = filter_ports(collection.distinct('vessel_name'))[:200]
            vessel_type_list = filter_ports(collection.distinct('vessel_type'))
            sub_vessel_type_list = filter_ports(collection.distinct('sub_vessel_type'))
            port_list = filter_ports(collection.distinct('new_open_port'))[:200]

            date_filter = {
                'Formatted_Date': {'$gte': from_unix, '$lte': to_unix},
                'dwt': {"$lt": 10000000}
            }
            tonnage_data = list(collection.find(date_filter, {
                '_id': 0, 'vessel_name': 1, 'vessel_type': 1, 'dwt': 1, 'new_open_date': 1
            }).limit(50000))

            return {
                'status': True,
                'type': 'tonnage',
                'vessel_names': vessel_name_list,
                'vessel_types': vessel_type_list,
                'sub_vessel_types': sub_vessel_type_list,
                'ports': port_list,
                'filtered_tonnage': tonnage_data
            }

        elif request_data.type == 'cargo':
            collection = db['cargo']
            cargo_list = filter_ports(collection.distinct('cargo'))
            cargo_type_list = filter_ports(collection.distinct('cargo_type'))
            port_list = filter_ports(collection.distinct('load_port.port'))
            date_filter = {
                'Formatted_Date': {'$gte': from_unix, '$lte': to_unix},
                'dwt': {"$lt": 10000000}
            }
            cargo_data = list(collection.find(date_filter, {
                '_id': 0, 'cargo': 1, 'cargo_type': 1, 'Formatted_Date': 1, 'cargo_size': 1, 'load_port': 1
            }).limit(50000))
            return {
                'status': True,
                'type': 'cargo',
                'cargo': cargo_list,
                'cargo_types': cargo_type_list,
                'ports': port_list,
                'filtered_cargo': cargo_data
            }

        else:
            raise HTTPException(status_code=400, detail="Invalid data type.")

    except Exception as e:
        logger.error(traceback.print_exc())
        logger.error(e)
        return {
            'status': False,
            'type': 'None',
            'error': str(e)
        }


