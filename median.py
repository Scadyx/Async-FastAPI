from statistics import median
import requests
from fastapi import  FastAPI
import uvicorn
from collections import Counter
import asyncio
from concurrent.futures import ThreadPoolExecutor

app = FastAPI()

async def parser():
    responses = requests.get('http://127.0.0.1:8000/users')
    return responses.json()

class Worker:

    def __init__(self, data):
        self._data = data

    def medians(self,data):
        result = []
        for user in data.values():
            if user['age'] is not None:
                result.append(user['age'])
        print(result)
        return {'median': median(result)}

    def age_range(self,data):
        minmax = []
        for user in data.values():
            if user['age'] is not None:
                if user['age'] >= 20 and user['age'] <= 30:
                    minmax.append(user)
        return minmax

    def unique_names(self,data):
        names = []
        for user in data.values():
            if user['name'] is not None:
                names.append(user['name'])
        res = Counter(names)
        return res

    async def run_thread_pool(self, method, args):
        loop = asyncio.get_running_loop()

        with ThreadPoolExecutor() as pool:
            return await loop.run_in_executor(pool, method, args)

@app.get('/median')
async def run_median():
    data = await parser()
    worker= Worker(data)
    return await worker.run_thread_pool(worker.medians, data)

@app.get('/age_range')
async def run_age_range():
    data = await parser()
    worker = Worker(data)
    return await worker.run_thread_pool(worker.age_range, data)

@app.get('/unique_names_histogram')
async def run_unique_names_histogram():
    data = await parser()
    worker = Worker(data)
    return await worker.run_thread_pool(worker.unique_names, data)


if __name__ == '__main__':
    uvicorn.run(app, host="127.0.0.1", port=8001)

