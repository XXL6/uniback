from uniback.app_generator import create_app
from werkzeug.serving import make_server
from threading import Thread
from traceback import format_exc
# app = create_app()

# if __name__ == '__main__':
    # app.run(debug=True, use_reloader=False)


class ServerThread(Thread):

    def __init__(self, app):
        super(ServerThread, self).__init__()
        self.srv = make_server('127.0.0.1', 5000, app)
        self.context = app.app_context()
        self.context.push()
    
    def run(self):
        self.srv.serve_forever()

    def shutdown(self):
        self.srv.shutdown()


def start_server():
    global server
    try:
        app = create_app()
        server = ServerThread(app)
        server.start()
    except Exception as e:
        print("General app start failure")
        print(format_exc())
        print(f"{e}")


def stop_server():
    global server
    server.shutdown()
