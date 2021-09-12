import subprocess
import os
import signal
import random
import shutil
import json
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
                outputData = '[Error]Compile Error:\n' + outputData
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


@socketio.on('new_project')
def on_new_project(data):
    print("Got Create Project")
    if os.path.exists('workspace/{}'.format(data["dir"])):
        emit('mes', {
            "type": "error",
            "message": "项目已经存在了"
        })
    else:
        os.mkdir('workspace/{}'.format(data["dir"]))
        with open('workspace/{}/settings.cp'.format(data["dir"]), 'w') as f:
            f.write(json.dumps({
                "title": data["title"],
                "dir": data["dir"]
            }, sort_keys=True, indent=4, separators=(',', ':')))
        with open('workspace/{}/export.cp'.format(data["dir"]), 'w') as f:
            f.write(json.dumps({
                "hiddens": ["*.cp", "*.exe", "*.in", "*.out"],
                "copies": {
                    "source": "*.cpp",
                    "to": "*"
                }
            }, sort_keys=True, indent=4, separators=(',', ':')))
        emit('mes', {
            "type": "success",
            "message": "创建成功"
        })
        emit('enter_project', {
            'settings': {
                "title": data["title"],
                "dir": data["dir"]
            },
            'files': os.listdir('workspace/{}/'.format(data["dir"]))
        })
    emit('handle_new_project', {}) 

@socketio.on('all_projects')
def on_all_projects(data):
    allProjects = []
    allDirs = os.listdir('workspace')
    for i in allDirs:
        if os.path.exists('workspace/{}/settings.cp'.format(i)):
            with open('workspace/{}/settings.cp'.format(i), 'w') as f:
                projectSettings = json.load(f)
                if ('title' in projectSettings) and ('dir' in projectSettings):
                    allProjects.append({
                        "title": projectSettings["title"],
                        "dir": projectSettings["dir"]
                    })
    emit('all_projects', {
        'p': allProjects
    })

if __name__ == '__main__':
    print("Running at *:3000")
    socketio.run(app, port=3000, host='0.0.0.0')
