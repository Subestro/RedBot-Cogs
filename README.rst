
Redbot cogs for Red-DiscordBot V3
================================================

This is my cog repo for the redbot, a multifunctional Discord bot!

------------
Installation
------------

Primarily, make sure you have `downloader` loaded.

.. code-block:: ini

    [p]load downloader

Next, let's add my repository to your system.

.. code-block:: ini

    [p]repo add Subestro https://github.com/Subestro/RedBot-Cogs

To install a cog, use this command, replacing <cog> with the name of the cog you wish to install:

.. code-block:: ini

    [p]cog install Subestro <cog>
    
    (ex !cog install Subestro welcome)
-------------------
📝Cogs list
-------------------
**Welcome:**

This cog sends a welcome message with the user's profile picture and a generated welcome image that includes the current member count to a specified channel whenever a new user joins the server.


To set the channel for the welcome message, use the ``!setchannel`` command followed by the name of the channel you want to set.

.. code-block:: shell

    !setchannel #welcome-channel

To unset the channel for the welcome message, use the ``!unsetchannel`` command.

.. code-block:: shell

    !unsetchannel

NOTE: If the welcome channel hasn't been set or if the server owner's account has been deleted, the bot will send a message to the server owner reminding them to set the welcome channel.
