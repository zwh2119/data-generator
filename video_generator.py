from generator.generator import Generator
import cv2
import os
import time
import base64
import requests

from generator.video_task import VideoTask


class VideoGenerator(Generator):
    def __init__(self, data_source: str, generator_id: int, priority: int,
                 task_dag: list, schedule_address: str):
        super().__init__(data_source, generator_id, priority, task_dag)

        # TODO: add video open check
        self.data_source_capture = cv2.VideoCapture(data_source)
        self.schedule_address = schedule_address

    @classmethod
    def generator_type(cls) -> str:
        return 'video'

    @classmethod
    def generator_description(cls) -> str:
        return 'Video generator'

    # TODO： how to process video source in real-time
    #        currently some frames from video source will be discarded in the process of frame compress
    def run(self):

        cur_id = 0
        cnt = 0

        # TODO: complete details of requests to scheduler
        response = requests.get(self.schedule_address)
        tuned_parameters = response.json()

        frame_resolution = tuned_parameters['resolution']
        frame_fourcc = tuned_parameters['encoding']
        frames_per_task = tuned_parameters['frames_per_task']
        skipping_frame_interval = tuned_parameters()['skipping_frame_interval']
        temp_frame_buffer = []
        while True:

            ret, frame = self.data_source_capture.read()
            if not ret:
                break
            cnt += 1
            if cnt % skipping_frame_interval != 0:
                continue
            temp_frame_buffer.append(frame)
            if len(temp_frame_buffer) < frames_per_task:
                continue
            else:
                # compress all the frames in the buffer into a short video, send it as a task, and empty the buffer
                compressed_video = self.compress_frames(temp_frame_buffer, frame_fourcc)
                base64_frame = base64.b64encode(compressed_video).decode('utf-8')
                task = VideoTask(base64_frame, cur_id, self.generator_id, self.priority, tuned_parameters,
                                 self.task_dag)

                # TODO: post task to local controller
                """
                data structure
                
                1.source_id
                2.task_id
                3.priority 
                4.metadata:{resolution, frame rate,
                            frame number, encoding}
                
                5.pipeline_flow:[service1, service2,..., end]
                    service:{service_name, execute_address, execute_data}
                    execute_data:{service_time, transmit_time, acc}
                6.cur_flow_index
                7.scenario_data:{obj_num, obj_size, stable}
                8.content_data (frame/middle_result/result)
                9.tmp_data:{} (middle_record)
                
                
                
                """

                cur_id += 1
                temp_frame_buffer = []

    # TODO: optimize frames compress efficiency
    def compress_frames(self, frames, fourcc):
        fourcc = cv2.VideoWriter_fourcc(*fourcc)
        height, width, _ = frames[0].shape
        buffer_path = f'temp_{self.generator_id}.mp4'
        out = cv2.VideoWriter(buffer_path, fourcc, 30, (width, height))
        for frame in frames:
            out.write(frame)
        out.release()
        with open(buffer_path, 'rb') as f:
            compressed_video = f.read()
        # delete the temporary file
        os.remove(buffer_path)
        return compressed_video

    def generate_blank_data(self):
        data_structure = {}
        data_structure['source_id'] = -1
        data_structure['task_id'] = -1
        data_structure['priority'] = -1
        data_structure['metadata'] = {}
        data_structure['pipeline_flow'] = []
        data_structure['cur_flow_index'] = 0

        return data_structure
