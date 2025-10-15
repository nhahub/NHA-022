from flask import Flask
import os
from flask_socketio import SocketIO, emit
import traceback

# Upload endpoints functions
from endpoints.upload_image import detect_endpoint
from endpoints.test import test

# init flask api for normal backend endpoints
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'

# init websocket server for streaming endpoints
socketio = SocketIO(app, cors_allowed_origins="*")

# Create folders if not exists ------------------------------------------------------------
os.makedirs('processed', exist_ok=True)

# Just to test the backend is running ------------------------------------------------------
@app.route('/', methods=['GET'])
def root():
  return test()

## ----------------- websocket for streaming -------------------------------------------
# Global error handler
@socketio.on_error_default
def default_error_handler(e):
  print('❌ WebSocket error:', str(e))
  traceback.print_exc()

@socketio.on("connect")
def handle_connect():
    try:
        print('✅ Client connected!')
        emit('connection_status', {'status': 'connected'})
    except Exception as e:
        print('❌ Connect error:', e)
        traceback.print_exc()


@socketio.on("disconnect")
def handle_disconnect():
  print('❌ Client disconnected!')

# connection between the flutter app
@socketio.on("stream_image")
def stream(data):
  try:
    
    # This function prepares data and then calls the model
    # then sends the response
    res = detect_endpoint(data)

    # show response to client with detected labels
    emit("response", res)

  except Exception as e:
    emit('response', {
        'status': 'error',
        'error': str(e)
    })

# ---------------------------------------------------------------------------------------------
if __name__ == '__main__':
  socketio.run(app, host='0.0.0.0', port=5000)