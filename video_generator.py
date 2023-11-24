import json

from generator import Generator
import cv2
import os
import time
import base64
import requests

from utils import *


class VideoGenerator(Generator):
    def __init__(self, data_source: str, generator_id: int, priority: int,
                 task_pipeline: list, schedule_address: str, resolution: str, fps: int):
        super().__init__(data_source, generator_id, priority, task_pipeline)

        self.data_source = data_source
        self.data_source_capture = cv2.VideoCapture(data_source)
        print(f'source:{data_source}')
        self.schedule_address = schedule_address
        self.raw_meta_data = {'resolution_raw': resolution, 'fps_raw': fps}

    # TODO： how to process video source in real-time.
    #        currently some frames from video source
    #        will be discarded in the process of frame compress.
    def run(self):
        cur_id = 0
        cnt = 0

        # TODO: complete details of requests to scheduler
        # response = requests.get(self.schedule_address)
        # tuned_parameters = response.json()

        # frame_resolution = tuned_parameters['resolution']
        # frame_fourcc = tuned_parameters['encoding']
        # frames_per_task = tuned_parameters['frames_per_task']
        # skipping_frame_interval = tuned_parameters['skipping_frame_interval']

        frame_resolution = '720p'
        frame_fourcc = 'h264'
        frames_per_task = 8
        skipping_frame_interval = 1

        temp_frame_buffer = []
        while True:
            ret, frame = self.data_source_capture.read()

            while not ret:
                print(f'no video signal of source {self.generator_id}')
                time.sleep(1)
                self.data_source_capture = cv2.VideoCapture(self.data_source)
                ret, frame = self.data_source_capture.read()
            print(f'get a frame from source {self.generator_id}')
            frame = cv2.resize(frame, text2resolution(frame_resolution))
            cnt += 1
            if cnt % skipping_frame_interval != 0:
                continue
            temp_frame_buffer.append(frame)
            if len(temp_frame_buffer) < frames_per_task:
                continue
            else:
                # compress all the frames in the buffer into a short video, send it as a task, and empty the buffer
                compressed_video_pth = self.compress_frames(temp_frame_buffer, frame_fourcc)

                # TODO: post task to local controller
                """
                data structure
                
                1.source_id
                2.task_id
                3.priority 
                4.metadata:{resolution_raw, fps_raw, resolution, frame_number,
                            skip_interval, encoding}
                
                5.pipeline_flow:[service1, service2,..., end]
                    service:{service_name, execute_address, execute_data}
                    execute_data:{service_time, transmit_time, acc}
                6.cur_flow_index
                7.scenario_data:{obj_num, obj_size, stable}
                8.content_data (middle_result/result)
                9.tmp_data:{} (middle_record)
                
                """

                data = {}
                data['source_id'] = self.generator_id
                data['task_id'] = cur_id
                data['priority'] = self.priority
                data['metadata'] = {}
                data['pipeline_flow'] = self.task_pipeline
                data['tmp_data'] = {}
                data['cur_flow_index'] = 0
                data['content_data'] = None
                data['scenario_data'] = {}
                data['content_type'] = 'file'

                data['tmp_data'], _ = record_time(data['tmp_data'], f'transmit_time_{data["cur_flow_index"]}')

                requests.post(data['pipeline_flow'][data['cur_flow_index']]['execute_address'],
                              data={'data': json.dumps(data)},
                              files={'file': (f'tmp_{self.generator_id}.mp4',
                                              open(compressed_video_pth, 'rb'),
                                              'video/mp4')})
                cur_id += 1
                temp_frame_buffer = []
                os.remove(compressed_video_pth)

    # TODO: optimize frames compress efficiency
    def compress_frames(self, frames, fourcc):
        fourcc = cv2.VideoWriter_fourcc(*fourcc)
        height, width, _ = frames[0].shape
        buffer_path = f'temp_{self.generator_id}.mp4'
        out = cv2.VideoWriter(buffer_path, fourcc, 30, (width, height))
        for frame in frames:
            out.write(frame)
        out.release()

        return buffer_path

