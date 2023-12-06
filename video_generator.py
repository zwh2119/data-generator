import json

from generator import Generator
import cv2
import os
import requests

from utils import *

buffer_size = 8
encoding = 'mp4v'
controller_port = 9002


class VideoGenerator(Generator):
    def __init__(self, data_source: str, generator_id: int, priority: int,
                 task_pipeline: list, schedule_address: str, resolution: str, fps: int):
        super().__init__(data_source, generator_id, priority, task_pipeline)

        self.data_source = data_source
        self.data_source_capture = cv2.VideoCapture(data_source)
        self.schedule_address = schedule_address
        self.raw_meta_data = {'resolution_raw': resolution, 'fps_raw': fps}

        self.local_ip = get_host_ip()

        for task in self.task_pipeline:
            if task['service_name'] == 'end':
                break
            task['execute_address'] = get_merge_address(self.local_ip, port=controller_port, path='submit_task')
            task['execute_data'] = {}

    # TODO： how to process video source in real-time.
    #        currently some frames from video source
    #        will be discarded in the process of frame compress.
    def run(self):
        cur_id = 0
        cnt = 0

        fps_raw = self.raw_meta_data['fps_raw']
        resolution_raw = self.raw_meta_data['resolution_raw']

        # default parameters
        frame_resolution = self.raw_meta_data['resolution_raw']
        frame_fourcc = encoding
        frames_per_task = buffer_size
        fps = self.raw_meta_data['fps_raw']
        priority = self.priority
        pipeline = self.task_pipeline

        response = requests.get(self.schedule_address, json={'source_id': self.generator_id,
                                                             'resolution_raw': resolution_raw,
                                                             'fps_raw': fps_raw,
                                                             'pipeline': pipeline})
        tuned_parameters = response.json()['plan']

        frame_resolution = tuned_parameters['resolution']
        fps = tuned_parameters['fps']
        priority = tuned_parameters['priority']
        pipeline = tuned_parameters['pipeline']

        fps = min(fps, fps_raw)
        fps_mode, skip_frame_interval, remain_frame_interval = self.get_fps_adjust_mode(fps_raw, fps)

        temp_frame_buffer = []
        while True:
            ret, frame = self.data_source_capture.read()

            # retry when no video signal
            while not ret:
                print(f'no video signal of source {self.generator_id}')
                time.sleep(1)
                self.data_source_capture = cv2.VideoCapture(self.data_source)
                ret, frame = self.data_source_capture.read()

            print(f'get a frame from source {self.generator_id}')
            resolution_raw = resolution2text((self.data_source_capture.get(cv2.CAP_PROP_FRAME_WIDTH),
                                              self.data_source_capture.get(cv2.CAP_PROP_FRAME_HEIGHT)))
            fps_raw = self.data_source_capture.get(cv2.CAP_PROP_FPS)

            # adjust resolution
            frame = cv2.resize(frame, text2resolution(frame_resolution))

            # adjust fps
            cnt += 1
            if fps_mode == 'skip' and cnt % skip_frame_interval == 0:
                continue

            if fps_mode == 'remain' and cnt % remain_frame_interval != 0:
                continue

            # put frame in buffer
            temp_frame_buffer.append(frame)
            if len(temp_frame_buffer) < frames_per_task:
                continue
            else:
                # compress frames in the buffer into a short video
                compressed_video_pth = self.compress_frames(temp_frame_buffer, frame_fourcc)

                """
                data structure
                
                1.source_id
                2.task_id
                3.priority 
                4.meta_data:{resolution_raw, fps_raw, resolution, frame_number,
                            skip_interval, encoding}
                
                5.pipeline_flow:[service1, service2,..., end]
                    service:{service_name, execute_address, execute_data}
                    execute_data:{service_time, transmit_time, acc}
                6.cur_flow_index
                7.scenario_data:{obj_num, obj_size, stable}
                8.content_data (middle_result/result)
                9.tmp_data:{} (middle_record)
                
                """
                meta_data = {'resolution_raw': resolution_raw, 'fps_raw': fps_raw, 'resolution': frame_resolution,
                             'fps': fps, 'frame_number': frames_per_task, 'encoding': frame_fourcc}

                data = {'source_id': self.generator_id, 'task_id': cur_id, 'priority': priority,
                        'meta_data': meta_data, 'pipeline_flow': pipeline, 'tmp_data': {}, 'cur_flow_index': 0,
                        'content_data': None, 'scenario_data': {}}

                # start record transmit time
                data['tmp_data'], _ = record_time(data['tmp_data'], f'transmit_time_{data["cur_flow_index"]}')

                # post task to local controller
                requests.post(data['pipeline_flow'][data['cur_flow_index']]['execute_address'],
                              data={'data': json.dumps(data)},
                              files={'file': (f'tmp_{self.generator_id}.mp4',
                                              open(compressed_video_pth, 'rb'),
                                              'video/mp4')})

                cur_id += 1
                temp_frame_buffer = []
                os.remove(compressed_video_pth)

                response = requests.get(self.schedule_address, json={'source_id': self.generator_id,
                                                                     'resolution_raw': resolution_raw,
                                                                     'fps_raw': fps_raw,
                                                                     'pipeline': pipeline})
                tuned_parameters = response.json()['plan']

                frame_resolution = tuned_parameters['resolution']
                frame_fourcc = tuned_parameters['encoding']
                fps = tuned_parameters['fps']
                priority = tuned_parameters['priority']
                pipeline = tuned_parameters['pipeline']

                fps = min(fps, fps_raw)
                fps_mode, skip_frame_interval, remain_frame_interval = self.get_fps_adjust_mode(fps_raw, fps)

    def get_fps_adjust_mode(self, fps_raw, fps):
        fps_mode = None
        skip_frame_interval = 0
        remain_frame_interval = 0
        if fps == fps_raw:
            fps_mode = 'same'
        elif fps < fps_raw // 2:
            fps_mode = 'remain'
            remain_frame_interval = fps_raw // fps
        else:
            fps_mode = 'skip'
            skip_frame_interval = fps_raw // (fps_raw - fps)

        return fps_mode, skip_frame_interval, remain_frame_interval

    def compress_frames(self, frames, fourcc):
        fourcc = cv2.VideoWriter_fourcc(*fourcc)
        height, width, _ = frames[0].shape
        buffer_path = f'temp_{self.generator_id}.mp4'
        out = cv2.VideoWriter(buffer_path, fourcc, 30, (width, height))
        for frame in frames:
            out.write(frame)
        out.release()

        return buffer_path
