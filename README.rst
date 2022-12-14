Welcome Discord Bot
===================

This is a Discord bot that sends a welcome message to a specified channel when a new user joins the server.

Getting Started
---------------

To use this bot, you will need to have a Discord account and create a bot by following the instructions `here <https://discordpy.readthedocs.io/en/latest/discord.html>`_.

.. admonition:: Usage

   To set the channel for the welcome message, use the ``!setchannel`` command followed by the name of the channel you want to set.

   .. code-block:: shell

       !setchannel #welcome-channel

   To unset the channel for the welcome message, use the ``!unsetchannel`` command.

   .. code-block:: shell

       !unsetchannel

Notes
-----

If the welcome channel hasn't been set or if the server owner's account has been deleted, the bot will send a message to the server owner reminding them to set the welcome channel.

The bot will also send a list of the currently loaded cogs to the server owner.

License
-------

This project is licensed under the MIT License - see the `LICENSE <LICENSE>`_ file for details.
