with open('preload.js', 'r') as f:
    content = f.read()

invoke_code = """
    invoke: (channel, ...args) => {
        const allowedInvokeChannels = [
            'export-excel'
        ];
        if (allowedInvokeChannels.includes(channel)) {
            return ipcRenderer.invoke(channel, ...args);
        } else {
            console.warn(`Blocked unauthorized IPC invoke on channel: ${channel}`);
            return Promise.reject(`Unauthorized IPC channel: ${channel}`);
        }
    },
"""

if "invoke:" not in content:
    content = content.replace("on: (channel, listener) => {", invoke_code + "    on: (channel, listener) => {")
    with open('preload.js', 'w') as f:
        f.write(content)
    print("Added invoke to preload.js")
else:
    print("Invoke already exists.")
