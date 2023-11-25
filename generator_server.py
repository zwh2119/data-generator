import random

import yaml_utils
import threading
from video_generator import VideoGenerator


def main():
    video_config = yaml_utils.read_yaml('video_config.yaml')
    videos = video_config['video']
    for video in videos:
        task_pipeline = [{'service_name': 'car_detection',
                          'execute_address': video['execute'],
                          'execute_data': {}},
                         {'service_name': 'end',
                          'execute_address': 'http://114.212.81.11:5713/distribute',
                          'execute_data': {}}]
        video_generator = VideoGenerator(video['url'], video['id'], 0, task_pipeline,
                                         'http://114.212.81.11:8140', video['resolution'], video['fps'])
        threading.Thread(target=video_generator.run).start()


if __name__ == '__main__':
    main()
