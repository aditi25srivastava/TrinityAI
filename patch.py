with open("app/routers/websocket.py", "r") as f:
    lines = f.read()
lines = lines.replace('print(f"Fatal error in websocket: {e}")', 
                      'print(f"Fatal error in websocket: {e}")\n        with open("fatal_error.txt", "w") as fef:\n            traceback.print_exc(file=fef)')
with open("app/routers/websocket.py", "w") as f:
    f.write(lines)
