import psutil

processes = [
    'mspdbsrv.exe',
    'cl.exe',
    'Tracker.exe',
    'vctip.exe'
]

for proc in psutil.process_iter():
    try:
        if proc.name() in processes:
            for child in proc.children(recursive=True):
                child.kill()
                print(f'Killed {child.name()}')

            proc.kill()

            print(f'Killed {proc.name()}')

    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        pass
