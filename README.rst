Redbot cogs for Red-DiscordBot V3
==================================================

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
.. admonition:: **Welcome**
  
   "This feature sends a welcome message with a generated image that includes the new user's profile picture and the current member count to a designated channel. 
   
   Use the ``!setchannel`` command to specify the channel for the welcome message."

   .. code-block:: shell

       !setchannel #welcome

   To unset the channel for the welcome message, use the ``!unsetchannel`` command.

   .. code-block:: shell

       !unsetchannel
     
------------
  Example
------------
  
   .. image:: https://i.imgur.com/yzaOSzI.png

   This cog was inspired by `Welcome-Bot <https://github.com/hattvr/Welcomer-Bot>`_.

   NOTE: If the welcome channel hasn't been set, the bot will send a message to the server owner reminding them to set the welcome channel.
