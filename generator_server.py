import yaml_utils
import threading
from video_generator import VideoGenerator
from utils import *

scheduler_ip = '114.212.81.11'
scheduler_port = 8140
scheduler_path = 'schedule'

video_config_file = 'video_config.yaml'


def main():
    video_config = yaml_utils.read_yaml(video_config_file)
    videos = video_config['video']

    scheduler_address = get_merge_address(scheduler_ip, port=scheduler_port, path=scheduler_path)

    for video in videos:
        video_generator = VideoGenerator(video['url'], video['id'], 0, video['pipeline'],
                                         scheduler_address, video['resolution'], video['fps'])
        threading.Thread(target=video_generator.run).start()


if __name__ == '__main__':
    main()
