
import webbrowser
import os
import subprocess
import time
import requests
from twilio.rest import Client
import signal


ROOT_PATH = "/home/ryler/Documents/ProgrammingProjects/DistributorCRM"
DISTRIBUTOR_PATH = ROOT_PATH + "/Distributor"
UVICORN_URL = DISTRIBUTOR_PATH + "/.venv/bin/uvicorn"
DJANGO_URL = DISTRIBUTOR_PATH + "/.venv/bin/python3"


def start_browser_and_django():
    kill_port('8000')

    env = os.environ.copy()
    env['DJANGO_SETTINGS_MODULE'] = "Distributor.settings"      

    # use this one went you want to test full functionality with websockets.
    uvicorn_server_proc = subprocess.Popen([UVICORN_URL, "Distributor.asgi:application", "--reload"], cwd=DISTRIBUTOR_PATH, env=env)\

    #use this one when developing so you get fast static reloads.
    #django_server_proc = subprocess.Popen([DJANGO_URL, "manage.py", "runserver", "8000"], env=env, cwd=DISTRIBUTOR_PATH)

    time.sleep(2)
    browser_proc = webbrowser.open("http://localhost:8000/")


def kill_existing_ngrok_sessions():
    try:
        subprocess.check_call(["pkill", "-f", 'ngrok'])
    except:
        print("\nFailed to terminate ngrok sessions.\n")


def start_ngrok_and_get_domain():
    kill_existing_ngrok_sessions()
    try:
        ngrok_proc = subprocess.Popen(["ngrok", "http", "3333"])
    except:
        print("\nNgrok Failed to start.\n")
    time.sleep(1)
    try:
        public_url = get_public_ngrok_url()
        print(f"\nUrl retrieval Successful, Ngrok url: {public_url}\n")
        return public_url
    except:
        #kill used because ngrok failed so we dont want to give the ngrok process time to clean up because it may be stuck, which would in turn timeout our program.
        try:
            ngrok_proc.kill()
            print("\nNgrok terminated.\n")
        except:
            print("\nNgrok failed.\n")

    
def update_twilio_webhook(pub_url):
    client = get_message_client()
    client.incoming_phone_numbers(os.getenv("TWILIO_NUMBER_SID")).update(sms_url=pub_url)


# run a retry loop and timeout after 10 seconds, requetsts is notorious for grabbing public url too fast and failing.
def get_public_ngrok_url():
    #send a request to the ngrok api and get the response back with the information about our tunnel, we then parse the json into python data structures and grab the public url.
    start_time = time.time()
    timeout = 10.0
    while time.time() - start_time < timeout:
        try:    
            res = requests.get("http://localhost:4040/api/tunnels")
            public_url = res.json()['tunnels'][0]['public_url']
            time.sleep(0.5)
            return public_url
        except:
            time.sleep(0.5)
    raise TimeoutError("Requests failed to grab the public ngrok url.")


def get_message_client() -> Client:
    return Client(
        os.getenv("TWILIO_STR_IDENTIFIER"),
        os.getenv("TWILIO_AUTH_TOKEN")
    )

def kill_port(port):
    try:
        pids = subprocess.check_output(['lsof', '-ti', f':{port}']).decode().split()
        for pid in pids:
            try:
                os.kill(int(pid), signal.SIGKILL)
                print(f"Killed process {pid} using port {port}")
            except PermissionError:
                print(f"⚠️  Permission denied trying to kill PID {pid}. Try running this script with elevated privileges (sudo).")
            except ProcessLookupError:
                print(f"⚠️  PID {pid} no longer exists.")
    except subprocess.CalledProcessError:
        print(f"✅ Port {port} is already free.")




def start_node_server():
    kill_port('3333')
    node_path = ROOT_PATH + "/DistroHook/index.js"
    try:
        subprocess.Popen(["node", node_path])
        print("\nNode startup Successful, Listening on port 3333\n")
    except:
        print("\nFailed to start node.js server\n")


def start_redis_server():
    subprocess.Popen(["redis-server"])
    time.sleep(1.0)


start_node_server()
start_redis_server()
public_ngrok_domain = start_ngrok_and_get_domain()
update_twilio_webhook(public_ngrok_domain)
start_browser_and_django()



