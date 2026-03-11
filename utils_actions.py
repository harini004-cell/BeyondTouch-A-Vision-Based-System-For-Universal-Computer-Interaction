# utils_actions.py
import queue, threading, logging, os, time
if not os.path.exists("logs"):
    os.makedirs("logs")
logging.basicConfig(filename="logs/actions.log", level=logging.INFO, format="%(asctime)s %(message)s")

action_q = queue.Queue()

def _worker():
    while True:
        fn, args, kwargs = action_q.get()
        try:
            fn(*args, **kwargs)
        except Exception as e:
            logging.exception("Action error")
        finally:
            action_q.task_done()
        time.sleep(0.01)

t = threading.Thread(target=_worker, daemon=True)
t.start()

def enqueue(fn, *args, **kwargs):
    action_q.put((fn, args, kwargs))
    logging.info(f"ENQUEUE {fn.__name__} {args} {kwargs}")
