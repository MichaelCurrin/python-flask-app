# Notes

This gave an error not sufficient permissions further testing required.

```python
def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')'
    
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()

@app.route('/shutdown', methods=['POST'])
def shutdown():
    shutdown_server()
    
    return 'Server shutting down'
```
