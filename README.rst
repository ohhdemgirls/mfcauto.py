==========
mfcauto.py
==========

mfcauto.py is a Python port of my `MFCAuto NodeJS module`_. Why? Primarily because I like Python and wanted an excuse to refresh my Python skills. Both packages are being actively maintained (as of April 16, 2016) so feel free to use whichever suits your scenario/tastes, although at the moment the NodeJS package is more feature complete and stable.

Initially the API surface will map very closely to that for NodeJS, but my intent is to update the API and make it more Pythonic over time. This means a lot of potentially breaking changes. See DIFFERENCES.rst for a partial list of known differences between the two packages.

.. _`MFCAuto NodeJS module`: https://github.com/ZombieAlex/MFCAuto

Setup
-----

This package requires Python 3.5 or later.

.. code-block:: bash

    # Install or upgrade to the latest version of mfcauto.py
    $ pip install --upgrade git+https://github.com/ZombieAlex/mfcauto.py@master

To install a specific commit or tag, refer to the `pip documentation`_.

.. _`pip documentation`: https://pip.pypa.io/en/latest/reference/pip_install/#git

Examples
--------

Query a model's details
~~~~~~~~~~~~~~~~~~~~~~~

SimpleClient is an abstraction that uses the default asyncio event loop. With SimpleClient, connect() is a blocking call that will not return until the connection to MFC's chat servers has been lost. So it should be the last call in your script.

Since connect() is blocking, to do something after connecting a SimpleClient you need to add a listener for the FCTYPE.CLIENT_CONNECTED event on the client instance before connecting.  SimpleClient also emits an FCTYPE.CLIENT_MODELSLOADED event when the model list has finished populating from the server.

.. code-block:: python

    from mfcauto import SimpleClient, FCTYPE

    client = SimpleClient()

    def handler(packet):
        print(packet)
        client.disconnect()

    client.on(FCTYPE.USERNAMELOOKUP, handler)
    client.on(FCTYPE.CLIENT_CONNECTED, lambda: client.tx_cmd(FCTYPE.USERNAMELOOKUP, 0, 20, 0, 'AspenRae'))

    client.connect(False)

There is a much more complete version of this example in the tests folder, userLookup.py, which can be run directly from there.

Using Client with your own event loop
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

SimpleClient is enough for the vast majority of cases. But if you need to do something more advanced like running multiple Clients simultaneously or running a Client on a different thread, you can manually manage your event loop like so...

.. code-block:: python

    import asyncio
    import mfcauto

    loop = asyncio.get_event_loop()
    client = mfcauto.Client(loop)

    ###########################################
    # Hook up any event handlers on the client object
    # and/or mfcauto.Model objects here.
    ###########################################

    loop.run_until_complete(client.connect())
    loop.run_forever()
    loop.close()

See the 'tests' folder for several other examples.