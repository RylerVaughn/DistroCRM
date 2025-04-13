
import asyncio, subprocess, logging, os, signal

def shut_down_processes():
    kill_port(8000)
    kill_port(3333)
    clear_redis_cache()
    kill_port(6379)
    try:
        subprocess.check_call(["pkill", "-f", "ngrok"])
        print("💀 Ngrok process killed.")
    except subprocess.CalledProcessError:
        print("✅ No ngrok processes were running.")

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

def clear_redis_cache():
    try:
        subprocess.run(["redis-cli", "FLUSHALL"])
        print("🧹 Redis cache flushed.")
    except Exception as e:
        print(f"❌ Failed to flush Redis: {e}")



