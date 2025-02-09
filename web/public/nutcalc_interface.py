from browser import bind, document, window

import nutcalc

from io import StringIO
from dataclasses import dataclass

class Nutcalc:
    def __init__(self):
        self.output_stream = StringIO()
        self.interpreter = nutcalc.interpret.Interpreter(output_stream=self.output_stream)
        self.continuations = {}

    def continuation(self, name):
        def wrapper(f):
            def wrapped(*args, **kwargs):
                del self.continuations[name]
                return f(*args, **kwargs)
            wrapped.__name__ = f'<continuation "{name}" {f.__name__}>'
            self.continuations[name] = wrapped
        return wrapper

    def dispatch(self, request):
        request = dict(request)
        print(f'received request {request}')
        match request:
            case { 'type': 'response', 'of': of, 'data': data }:
                continuation = self.continuations.get(of)
                if continuation is None:
                    raise RuntimeError("no such continuation")
                    # TODO think of how to signal errors to the frontend?
                    # should this error ever actually happen?
                continuation(data)

            case { 'type': 'eval', 'contents': line }:
                try:
                    self._eval_nutcalc(line)
                    output = self._collect_output()
                except Exception as e:
                    respond_to(request, {
                        'success': False,
                        'error': e.toString() if 'toString' in dir(e) else str(e),
                    })
                else:
                    respond_to(request, {
                        'success': True,
                        'data': output,
                    })

            case { 'type': 'load-module', 'name': name, 'contents': contents }:
                self._load_root_module(request, name, contents)

            case _:
                respond_to(request, {
                    'success': False,
                    'error': f'unhandled request type {request['type']}',
                })

    def _load_root_module(self, originator, name, contents):
        """Loads a module identified as a 'root module', i.e. the root of a DAG of
        modules to ultimately be loaded."""

        # Modules that are currently being loaded
        # This is a 'visited set', used to detect import loops.
        loading = set()

        # This is a continuation-based implementation of async module loading.

        # `load_module` implements the DFS through the DAG of modules as they're
        # being parsed. Once all of a module's imports are loaded into the
        # interpreter, then the module itself is loaded.
        # Whenever `load_module` needs to get the contents of a as-of-yet unknown
        # module, it yields its name and waits for someone to .send() it the
        # contents of that module.
        def load_module(name, contents):
            loading.add(name)
            module = nutcalc.parser.parse_module(StringIO(contents), source=name)
            for imp in module.imports:
                # Skip already loaded modules
                if imp.path in self.interpreter.modules: continue
                # error on module import loop
                if imp.path in loading:
                    raise ModuleLoopError(name, set(loading))
                new_contents = yield imp.path
                yield from _load_module(imp.path, new_contents)
            self.interpreter.load_module(name, module)
            loading.remove(name)

        # lm_it therefore emits a sequence of module names needing to be loaded
        lm_it = load_module(name, contents)

        # feed_module_contents(x) sends `x` as the contents of the last requested
        # module into the recursive `load_module` loop. The initial `x` has to be
        # None to kickstart the process.
        def feed_module_contents(contents):
            try:
                module_path = lm_it.send(contents)
            # Handle module loading completion or failure:
            except StopIteration:
                output = self._collect_output()
                respond_to(originator, {
                    'success': True,
                    'data': output,
                })
            except nutcalc.NutcalcError as e:
                respond_to(originator, {
                    'success': False,
                    'error': str(e),
                })
            # or send a request to the JS side for the module contents
            else:
                emit({
                    'type': 'load-module',
                    'id': name,
                    'name': name,
                })
                # Register a continuation so when the JS side gets back to us
                # we feed that module's contents into the DFS and keep going
                self._continue(module_path, feed_module_contents)

        feed_module_contents(None)

    def _continue(self, name, function):
        def continuation(response):
            del self.continuations[name]
            return function(response)
        self.continuations[name] = continuation

    def _eval_nutcalc(self, line):
        stmt = nutcalc.parser.parse_stmt(line)
        self.interpreter.execute(stmt)

    def _collect_output(self):
        self.output_stream.seek(0)
        output = self.output_stream.read()
        self.output_stream.truncate(0)
        return output

@bind(document, 'nutcalc_to')
def handle_nutcalc_request(e):
    NUTCALC.dispatch(e.detail)

@bind(document, 'nutcalc_reset')
def handle_nutcalc_reset(*e):
    global NUTCALC
    NUTCALC = Nutcalc()
    emit(True, 'nutcalc_ready')

def respond_to(message, data):
    emit({
        'type': 'response',
        'of': message['id'],
        'data': data
    })

def emit(message, key='nutcalc_from'):
    document.dispatchEvent(
        window.CustomEvent.new(key, {
            'detail': message,
        }),
    )

@dataclass
class ModuleLoopError(nutcalc.NutcalcError):
    location: str
    module_name: str
    loading_set: set[str]

    def __str__(self):
        return f'{self.location}: loading {self.module_name} causes an import ' \
            f'loop among already loaded modules {str(self.loading_set)}'

NUTCALC = None
handle_nutcalc_reset()

print('nutcalc interface loaded')