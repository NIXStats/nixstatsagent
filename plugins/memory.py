import psutil


def run(config):
    memory = {}

    mem = psutil.virtual_memory()
    for name in mem._fields:
        memory[name] = getattr(mem, name)
    return memory