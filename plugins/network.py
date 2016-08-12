import psutil


def run(config):
    return psutil.net_io_counters(pernic=True)