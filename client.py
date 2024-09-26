import requests
import time
import datetime
start = datetime.datetime.now()
resp = requests.post('http://127.0.0.1:5000/upscale', files={
    'image_1': open('lama_300px.png', 'rb')
})
resp_data = resp.json()
task_id = resp_data.get('task_id')
print(task_id)

while True:
    resp = requests.get(f'http://127.0.0.1:5000/upscale/{task_id}')
    if resp.json()['status'] != 'PENDING':
        break
    print(resp.json())
    time.sleep(7)
end = datetime.datetime.now()
print(end - start, '\n', resp.json())
