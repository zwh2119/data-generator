import yaml_utils
import threading
from video_generator import VideoGenerator

scheduler_address = 'http://114.212.81.11:8140/schedule'


def main():
    video_config = yaml_utils.read_yaml('video_config.yaml')
    videos = video_config['video']

    for video in videos:
        video_generator = VideoGenerator(video['url'], video['id'], 0, video['pipeline'],
                                         scheduler_address, video['resolution'], video['fps'])
        threading.Thread(target=video_generator.run).start()


if __name__ == '__main__':
    main()
