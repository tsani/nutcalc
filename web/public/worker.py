# from browser import bind, self

# Message types
# =============
# 
# Sometimes, the PY side that it cannot complete a request unless more information is provided.
# (e.g. another module's code is needed from the JS side)
# In that case, _while processing a request from the JS side,_ the PY side makes a request to the JS side.
# 
# Therefore, either side can send this message to the other side, to provide a response to a request:
# 
# - { type: 'response': of: string, data: any }
#     - `of` holds the ID of the request
# 
# JS -> PY
# - { type: 'load-module', id: string, name: string, contents: string }
#     -> loads the module with the given contents and the given name. The name is crucial for the import mechanism.
# - { type: 'eval', id: string, contents: string }
#     -> executes a single statement of nutcalc code
#     
# Each core request comes with an `id` field to identify that particular request.
# When the nutcalc worker has completed the request, it will send a message back with that ID containing the result.
#     
# PY -> JS
# - { type: 'load-module', id: string, name: string }
#     - request the code of the module with the given `name`

# class Worker():
#     def __init__(self, context):
#         self._context = context
#         self.reset()
# 
#         # map from unique strings to functions to continue a computation
#         self.continuations = {} 
#         
#     def reset(self):
#         self.interpreter = nutcalc.interpret.Interpreter()     
#         
#     def eval(self, contents):
#         stmt = nutcalc.parser.parse_stmt(contents)
#         self.interpreter.execute(stmt)
#         # TODO find a way to capture the generate stdout
#         # will probably want a way to generalize the interpreter's output stream to smth else
#         
#     def _debug(self, message):
#         try:
#             self._context.send({
#                 'type': 'debug',
#                 'message': message,
#             })
#         except:
#             print(message)
#     
#     def dispatch(self, message):
#         if 'hello' in dir(message):
#             print('worker received hello')
#             return
#         self._debug(f'worker received request')
#         match message:
#             case { 'type': 'response', 'of': of, 'data': data }:
#                 continuation = self.continuations.get(of)
#                 if continuation is None:
#                     raise RuntimeError("no such continuation")
#                     # TODO think of how to signal errors to the frontend?
#                     # should this error ever actually happen?
#                 continuation(data)
# 
#             case { 'type': 'eval', 'contents': contents }:
#                 try:
#                     output = self.eval(contents)
#                 except Error as e:
#                     self.respond_to(message, {
#                         'success': False,
#                         'error': str(e),
#                     })
#                 else:
#                     self.respond_to(message, {
#                         'success': True,
#                         'data': output,
#                     })
# 
#             case { 'type': 'load-module', 'name': name, 'contents': contents }:
#                 raise RuntimeError('todo')
#             
#             case _:
#                 self._debug(f'unhandled message type: {dir(message)}')
#                 
#     def respond_to(self, message, data):
#         self._context.send({
#             'type': 'response',
#             'of': message.id,
#             'data': data
#         }) 
# 
#     def send(self, message):
#         self._context.send(message)
# 
#     
# try:
#     WORKER = Worker(self)
# 
#     @bind(self, "message")
#     def on_message(e):
#         WORKER.dispatch(e.data)
#         
#     print('hello world')
# except Error as e:
#     self.send({
#         'type': 'debug',
#         'message': str(e),
#     })    

# @bind(self, 'message')
# def foo(evt):
#     self.send({
#         'type': 'debug',
#         'message': 'hello world!',
#     })