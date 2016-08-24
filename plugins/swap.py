import psutil


def run(config):
    swap = {}
    mem = psutil.swap_memory()
    for name in mem._fields:
        swap[name] = getattr(mem, name)
    return swap


if __name__ == '__main__':
    pickle.dump(run(), sys.stdout)
