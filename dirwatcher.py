import sys
import time
import logging
import os
import signal
import argparse

exit_flag = False
checked = {}

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler('log.txt')
formatter = logging.Formatter(
    "%(asctime)s:%(levelname)s:%(threadName)s:%(message)s")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


def signal_handler(sig_num, frame):
    global exit_flag
    if sig_num == signal.SIGINT:
        exit_flag = True
    if sig_num == signal.SIGTERM:
        exit_flag = True
    return None


def look_for_magic(file, directory):
    magic = "Ash"
    with open(directory + '/' + file) as current:
        for x, line in enumerate(current):
            if magic in line and x not in checked[file]:
                logger.info(
                    "{} found at line {} in {}".format(magic, x+1, file))
                checked[file].append(x)


def log_loop(args):
    directory = os.path.abspath(args.dir)
    txt_file = [t for t in os.listdir(directory) if ".txt" in t]
    if len(txt_file) > len(checked):
        for file in txt_file:
            if file not in checked:
                logger.info("{} found in {}".format(file, args.dir))
                checked[file] = []
    elif len(txt_file) < len(checked):
        for file in checked:
            if file not in txt_file:
                logger.info("{} removed from {}".format(file, args.dir))
                checked.pop(file, None)
    for file in txt_file:
        look_for_magic(file, directory)


def main():
    start_time = time.time()
    parser = argparse.ArgumentParser(
        description="Continuesly loop through dir and log created and delted files")
    parser.add_argument('dir', help="dir to be monitored")

    args = parser.parse_args()

    logger.info("Program searching in {}".format(args.dir))

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    while not exit_flag:
        try:
            log_loop(args)
            time.sleep(2)
        except Exception:
            logger.exception("EXCEPTION")
    logger.info("Program uptime: {} seconds".format(time.time() - start_time))


if __name__ == '__main__':
        main()