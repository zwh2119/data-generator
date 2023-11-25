import time


def record_time(data: dict, time_sign: str):
    if time_sign in data:
        start_time = data[time_sign]
        end_time = time.time()
        del data[time_sign]
        return data, end_time-start_time
    else:
        data[time_sign] = time.time()
        return data, -1


def text2resolution(text):
    resolution_dict = {'1080p': (1920, 1080),
                       '720p': (1280, 720),
                       '360p': (640, 360)}

    assert text in resolution_dict
    return resolution_dict[text]
