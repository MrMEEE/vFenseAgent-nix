import os
import cPickle

from src.utils import settings, logger
from serveroperation.operationqueue import OperationQueue
from serveroperation.sofoperation import SofOperation, ResultOperation

def save_operation_queue(queue):
    save_queue(queue, settings.operation_queue_file)

def save_result_queue(queue):
    save_queue(queue, settings.result_queue_file)

def save_queue(queue, file_path, protocol=-1):
    """
    Current way of saving queue is to take all items inside the queue
    and dump them into a list, this list is pickled into a file.
    """

    queue_dump = queue.queue_dump()

    savable_dump = []
    non_savable_dump = []
    for op in queue_dump:
        if isinstance(op, SofOperation) or isinstance(op, ResultOperation):
            if op.is_savable():
                savable_dump.append(op)

            else:
                try:
                    non_savable_dump.append((op.type, op.id))
                except Exception:
                    non_savable_dump.append(op)

                continue

        savable_dump.append(op)

    if non_savable_dump:
        logger.debug(
            "The following will not be saved in queue dump: {0}"
            .format(non_savable_dump)
        )

    try:

        with open(file_path, 'w') as _file:
            cPickle.dump(savable_dump, _file, protocol)

        os.chmod(file_path, 0600)

    except Exception as e:
        logger.error("Failed to dump queue to file: {0}".format(file_path))
        logger.exception(e)

        if os.path.exists(file_path):
            os.remove(file_path)

def load_operation_queue():
    return load_queue(settings.operation_queue_file)

def load_result_queue():
    return load_queue(settings.result_queue_file)

def load_queue(file_path):

    if not os.path.exists(file_path):
        return OperationQueue()

    loaded = []

    try:

        with open(file_path, 'r') as _file:
            loaded = cPickle.load(_file)

    except Exception as e:
        logger.error("Failed to load operations from: {0}".format(file_path))
        logger.exception(e)
        loaded = []

    logger.debug("Loaded operations: {0}".format(loaded))

    q = OperationQueue()

    for operaion in loaded:
        q.put(operaion)

    return q

