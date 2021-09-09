import subprocess
import os
import signal
import random
import shutil
from flask import Flask, request
from flask_socketio import SocketIO, emit


def ranstr(num):
    # 猜猜变量名为啥叫 H
    H = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
    salt = ''
    for i in range(num):
        salt += random.choice(H)
    return salt


langSettings = {
    "C++": {
        "suffix": '.cpp',
        "type": 1,  # Compile
        "compile": "g++ {file}.cpp -o {file} -std=c++2a",
        "run": "./{file}"
    },
    "Python3": {
        "suffix": '.py',
        "type": 2,  # Explain
        "compile": "",
        "run": "python3 {file}.py",
    },
    "Nodejs": {
        "suffix": '.js',
        "type": 2,  # Explain
        "compile": "",
        "run": "node.exe {file}.js"
    }
}


def run_cmd(cmd_string, inputFile='', timeout=5):
    print("Start Run: {}".format(cmd_string))
    if not inputFile:
        f = subprocess.PIPE
    else:
        f = open(inputFile, 'r')
    p = subprocess.Popen(cmd_string, stdin=f, stderr=subprocess.STDOUT,
                         stdout=subprocess.PIPE, shell=True, close_fds=True, preexec_fn=os.setsid)
    try:
        (msg, errs) = p.communicate(timeout=timeout)
        ret_code = p.poll()
        if ret_code:
            code = 1
            msg = "[Error]Called Error: {}".format((str)(msg.decode('utf-8')))
        else:
            code = 0
            msg = (str)(msg.decode('utf-8'))
    except subprocess.TimeoutExpired:
        p.kill()
        p.terminate()
        os.killpg(p.pid, signal.SIGTERM)

        code = 2
        msg = "[Error]Timed Out"
    except Exception as e:
        code = 3
        msg = "[Error]{}".format(str(e))
    return code, msg[0:200]


def RunCode(code, lang, inputData=''):
    code = code.replace("system", "")
    code = code.replace("popen", "")
    code = code.replace("rm -rf", "")
    code = code.replace("subprocess", "")
    onlyKey = ranstr(8)
    try:
        if not lang in langSettings:
            raise Exception("Cannot Find Such Language")
        langS = langSettings[lang]
        if os.path.exists('tmp/{}'.format(onlyKey)):
            shutil.rmtree('tmp/{}'.format(onlyKey))
        os.mkdir('tmp/{}'.format(onlyKey))
        with open('tmp/{}/code{}'.format(onlyKey, langS["suffix"]), "w") as f:
            f.write(code)
        with open('tmp/{}/input.in'.format(onlyKey), "w") as f:
            f.write(inputData)
        if langS["type"] == 1:
            (ret_code, outputData) = run_cmd(
                langS["compile"].format(file='tmp/{}/code'.format(onlyKey)))
            ret_code += 800
            if ret_code != 800:
                outputData = '[Error]Compile Error'
            else:
                (ret_code, outputData) = run_cmd(
                    langS["run"].format(file='tmp/{}/code'.format(onlyKey)), inputFile='tmp/{}/input.in'.format(onlyKey))
        else:
            (ret_code, outputData) = run_cmd(
                langS["run"].format(file='tmp/{}/code'.format(onlyKey)), inputFile='tmp/{}/input.in'.format(onlyKey))
        shutil.rmtree('tmp/{}'.format(onlyKey))
    except Exception as e:
        ret_code = 999
        outputData = '[Error]{}'.format(str(e))
    return ret_code, outputData


app = Flask(__name__, static_url_path='')
socketio = SocketIO(app, cors_allowed_origins='*', async_mode='eventlet')


@app.route('/')
def index():
    return app.send_static_file('index.html')


@socketio.on('connect')
def on_connect():
    print("JOIN:" + request.sid)


@socketio.on('run_code')
def on_run_code(data):
    print("Got Code")
    (rer, oer) = RunCode(data["code"], data["lang"], data["inputData"])
    emit('res', {
        "code": rer,
        "outputFile": oer
    })


if __name__ == '__main__':
    print("Running at *:3000")
    socketio.run(app, port=3000, host='0.0.0.0')
