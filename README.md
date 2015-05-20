# Firefox Accounts Device Manager

The device manager associates a Firefox Account with a user's "Foxes:" Firefox OS, Android, iOS, and Desktop. The service allows Firefox clients to register themselves, and exposes an API for other services to query an authenticated user's devices. During registration, the device specifies its name and type, as well as a push endpoint for other services to address it. This may be extended to support individual applications on the device, which will allow services to send broadcast and multicast push messages. The device manager also provides a remote logout mechanism that allows a user to invalidate a session on a lost or stolen device.

The Firefox client ("device") API requires a BrowserID assertion for registration, and issues a long-lived Hawk session token once registration is complete. The client uses this session token to update its information, either when the user changes the device name, or when its push endpoint changes. The service ("user") API is authenticated with an OAuth bearer token, and allows relying services to retrieve all device information for a user's account.

Two examples of relying services are the Firefox Accounts content server and Find My Device. The content server could use the API to display a user's active devices, and allow her to remotely log out of each. Likewise, Find My Device can use push notifications and remote logout to ring or lock a lost device.

## Installation

The server is built with [Tornado](https://tornado.readthedocs.org/), and requires Python >= 3.4. To check out a working copy of the source and install dependencies:

    git clone git@github.com:kitcambridge/fxa-device-manager-server.git
    cd fxa-device-manager-server
    make

### OS X

The server depends on the Python [cryptography](https://cryptography.io/en/latest/installation) library, which requires OpenSSL. If you're building the device manager on OS X with a custom version of OpenSSL, you'll need to set the `ARCHFLAGS` environment variable, and add your OpenSSL library path to `LDFLAGS` and `CFLAGS` before running `make build`:

    export ARCHFLAGS="-arch x86_64"
    # Homebrew installs OpenSSL to `/usr/local/opt/openssl` instead of
    # `/usr/local`.
    export LDFLAGS="-L/usr/local/lib" CFLAGS="-I/usr/local/include"

## License

MPL.
