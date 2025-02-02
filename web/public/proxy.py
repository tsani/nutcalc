from browser import bind, document, worker, window

TIMEOUT_MS = 1000

import nutcalc

WORKER = None

def onready(w):
    global WORKER
    print('worker ready')
    WORKER = w
    document.dispatchEvent(window.CustomEvent.new('nutcalc_restarted'))
        
def onmessage(msg):
    """Runs when the worker sends a message back to us with the result of the computation."""
    print(msg)
    data = msg.data
    if data.type == 'debug':
        console.log(data.message)
    else:
        respond(msg.data)
            
def onerror(msg):
    print('worker error:', msg)
        
def respawn_worker():
    global WORKER
    if WORKER is not None:
        WORKER.worker.terminate()
    WORKER = None
    worker.create_worker('nutcalc_worker', onready, onmessage, onerror)
        
def send(msg):
    global WORKER
    if WORKER is None:
        print('error: worker not initialized')
        return
    WORKER.send(msg)

def respond(response):
    document.dispatchEvent(
        window.CustomEvent.new(
            'nutcalc_from', {
                'detail': response,
            },
        ),
    )
        
@bind(document, 'nutcalc_to')
def main(e):
    print('proxy received request from JS')
    global WORKER
    WORKER.send(e.detail)
    
respawn_worker()

print('proxy loaded')