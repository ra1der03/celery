import os
from flask import Flask, request, jsonify
from celery import Celery
from celery.result import AsyncResult
from flask.views import MethodView
from upscale import upscale

app_name = 'app'
app = Flask('app_name')
app.config['UPLOAD_FOLDER'] = 'files'
celery = Celery(
    app_name,
    backend='redis://localhost:6379/0',
    broker='redis://localhost:6379/1',
    broker_connection_retry_on_startup=True)
celery.conf.update(app.config)


class ContextTask(celery.Task):
    def __call__(self, *args, **kwargs):
        with app.app_context():
            return self.run(*args, **kwargs)


celery.Task = ContextTask


@celery.task()
def upscale_files(path_1, path_2):
    upscale(path_1, path_2)


class Upscale(MethodView):

    def get(self, task_id):
        task = AsyncResult(task_id, app=celery)
        return jsonify({'status': task.status,
                        'result': task.result})

    def post(self):
        image_path_1 = self.save_image('image_1')
        image_path_2 = r'files\\lama_600px.png'
        task = upscale_files.delay(image_path_1, image_path_2)
        return jsonify(
            {'task_id': task.id}
        )

    def save_image(self, field):
        image = request.files.get(field)
        extension = image.filename.split('.')[-1]
        name = image.filename.split('.')[0]
        path = os.path.join('files', f'{name}.{extension}')
        image.save(path)
        return path


upscale_view = Upscale.as_view('upscale')
app.add_url_rule('/upscale/<string:task_id>', view_func=upscale_view, methods=['GET'])
app.add_url_rule('/upscale', view_func=upscale_view, methods=['POST'])


if __name__ == '__main__':
    app.run()
