import random

import yaml_utils
import threading
from video_generator import VideoGenerator


def main():
    video_config = yaml_utils.read_yaml('video_config.yaml')
    videos = video_config['video']
    process = []
    for video in videos:
        task_pipeline = [{'service_name': 'car_detection',
                          'execute_address': video['execute'],
                          'execute_data': {}}]
        video_generator = VideoGenerator(video['url'], video['id'], 0, task_pipeline,
                                         'http://114.212.81.11:8140', video['resolution'], video['fps'])
        process.append(threading.Thread(target=video_generator.run))


if __name__ == '__main__':
    main()
