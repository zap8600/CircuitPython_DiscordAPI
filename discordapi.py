# SPDX-FileCopyrightText: 2017 Scott Shawcroft, written for Adafruit Industries
# SPDX-FileCopyrightText: Copyright (c) 2023 Zane
#
# SPDX-License-Identifier: MIT
"""
`discordapi`
================================================================================

An implementation of Discord's APIs in CircuitPython.


* Author(s): Zane

Implementation Notes
--------------------

**Hardware:**

.. todo:: Add links to any specific hardware product page(s), or category page(s).
  Use unordered list & hyperlink rST inline format: "* `Link Text <url>`_"

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://circuitpython.org/downloads

.. todo:: Uncomment or remove the Bus Device and/or the Register library dependencies
  based on the library's use of either.

# * Adafruit's Bus Device library: https://github.com/adafruit/Adafruit_CircuitPython_BusDevice
# * Adafruit's Register library: https://github.com/adafruit/Adafruit_CircuitPython_Register
"""

# imports

__version__ = "0.0.0+auto.0"
__repo__ = "https://github.com/zap8600/CircuitPython_DiscordAPI.git"

import json
import binascii
import adafruit_requests


def isalpha(char):
    """CircuitPython implementation of .isalpha()"""
    if not char >= "a" <= "z" or char >= "A" <= "Z":
        return False
    return True


def isdigit(char):
    """CircuitPython implementation of .isdigit()"""
    char_ascii = ord(char)
    if not char_ascii >= 48 <= 57:
        return False
    return True


def isalnum(char):
    """CircuitPython implementation of .isalnum()"""
    return isalpha(char) or isdigit(char)


def is_valid_codepoint(char):
    """Checks if the input character is a code point"""
    code_point = ord(char)
    return 0 <= code_point <= 0x10FFFF


def url_encoder(string):
    """Encodes a string in URL format"""
    encoded_url = ""
    for char in string:
        if isalnum(char) or char in ["-", "_", ".", "~"]:
            encoded_url += char
        elif is_valid_codepoint(char):
            encoded_url += "%" + binascii.hexlify(char.encode(), "%").decode().upper()
    return encoded_url


class RESTAPI:  # pylint: disable=too-many-public-methods
    """Class for Discord's REST API"""

    def __init__(
        self, base_url, token, pool, ssl=None, auth_type="Bot", user=False
    ):  # pylint: disable=too-many-arguments
        self.base_url = base_url
        self.auth_type = auth_type
        self.token = token
        self.requests = adafruit_requests.Session(pool, ssl)
        if user is False:
            self.headers = {
                "Authorization": f"{auth_type} {token}",
                "Content-Type": "application/json",
                "Content-Length": "0",
            }
        else:
            self.headers = {
                "Accept": "*/*",
                "Accept-Language": "en-US,en;q=0.9",
                "Authorization": token,
                "Cache-Control": "no-cache",
                "Content-Type": "application/json",
                "Pragma": "no-cache",
                "Referer": "https://discord.com/channels/@me",
                "Sec-Ch-Ua": '" Not A;Brand";v="99", "Chromium";v="103", "Google Chrome";v="103"',
                "Sec-Ch-Ua-Mobile": "?0",
                "Sec-Ch-Ua-Platform": '"Chrome OS"',
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
                "User-Agent": "Mozilla/5.0 (X11; CrOS x86_64 14816.131.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36",  # pylint: disable=line-too-long
                "X-Debug-Options": "bugReporterEnabled",
                "X-Discord-Locale": "en-US",
                "Origin": "https://discord.com",
            }
        # print(self.headers)

    # Channel

    def get_channel(self, channel_id):
        """Get a channel by ID.
        Returns a channel object."""
        url = f"{self.base_url}/channels/{channel_id}"
        response = self.requests.get(url, headers=self.headers)
        if response.status_code == 200:
            jresponse = json.loads(response.content.decode("utf-8"))
            return jresponse
        print(f"Failed to get channel with status code {response.status_code}.")
        return None

    def modify_channel(self, channel_id, channel_name):
        """Update a channel's settings.
        Returns a channel on success, and a 400 BAD REQUEST on invalid parameters."""
        url = f"{self.base_url}/channels/{channel_id}"
        payload = {"name": channel_name}
        response = self.requests.patch(
            url, headers=self.headers, data=json.dumps(payload)
        )
        if response.status_code == 200:
            jresponse = json.loads(response.content.decode("utf-8"))
            return jresponse
        print(f"Failed to modify channel with status code {response.status_code}.")
        return None

    def delete_close_channel(self, channel_id):
        """Delete a channel, or close a private message.
        Returns a channel object on success."""
        url = f"{self.base_url}/channels/{channel_id}"
        response = self.requests.delete(url, headers=self.headers)
        if response.status_code == 200:
            jresponse = json.loads(response.content.decode("utf-8"))
            return jresponse
        print(
            f"Failed to get delete/close channel with status code {response.status_code}."
        )
        return None

    def get_channel_messages(self, channel_id):
        """Retrieves the messages in a channel.
        Returns an array of message objects on success."""
        url = f"{self.base_url}/channels/{channel_id}/messages"
        response = self.requests.get(url, headers=self.headers)
        if response.status_code == 200:
            jresponse = json.loads(response.content.decode("utf-8"))
            return jresponse
        print(
            f"Failed to get channel messages with status code {response.status_code}."
        )
        return None

    def get_channel_message(self, channel_id, message_id):
        """Retrieves a specific message in the channel.
        Returns a message object on success."""
        url = f"{self.base_url}/channels/{channel_id}/messages/{message_id}"
        response = self.requests.get(url, headers=self.headers)
        if response.status_code == 200:
            jresponse = json.loads(response.content.decode("utf-8"))
            return jresponse
        print(f"Failed to get channel message with status code {response.status_code}.")
        return None

    def create_message(self, channel_id, content):
        """Post a message to a guild text or DM channel.
        Returns a message object."""
        url = f"{self.base_url}/channels/{channel_id}/messages"
        payload = {"content": content}
        response = self.requests.post(
            url, headers=self.headers, data=json.dumps(payload)
        )
        if response.status_code == 200:
            jresponse = json.loads(response.content.decode("utf-8"))
            return jresponse
        print(f"Failed to create message with status code {response.status_code}.")
        return None

    def crosspost_message(self, channel_id, message_id):
        """Crosspost a message in an Announcement Channel to following channels.
        Returns a message object."""
        url = f"{self.base_url}/channels/{channel_id}/messages/{message_id}/crosspost"
        response = self.requests.post(url, headers=self.headers)
        if response.status_code == 200:
            jresponse = json.loads(response.content.decode("utf-8"))
            return jresponse
        print(f"Failed to crosspost message with status code {response.status_code}.")
        return None

    def create_reaction(self, channel_id, message_id, emoji):
        """Create a reaction for the message.
        Returns a 204 empty response on success."""
        encoded_emoji = url_encoder(emoji)
        url = f"{self.base_url}/channels/{channel_id}/messages/{message_id}/reactions/{encoded_emoji}/@me"  # pylint: disable=line-too-long
        response = self.requests.put(url, headers=self.headers)
        if response.status_code == 204:
            print("Success.")
        else:
            print(f"Failed to create reaction with status code {response.status_code}.")

    def delete_own_reaction(self, channel_id, message_id, emoji):
        """Delete a reaction the current user has made for the message.
        Returns a 204 empty response on success."""
        encoded_emoji = url_encoder(emoji)
        url = f"{self.base_url}/channels/{channel_id}/messages/{message_id}/reactions/{encoded_emoji}/@me"  # pylint: disable=line-too-long
        response = self.requests.delete(url, headers=self.headers)
        if response.status_code == 204:
            print("Success.")
        else:
            print(
                f"Failed to delete own reaction with status code {response.status_code}."
            )

    def delete_user_reaction(self, channel_id, message_id, emoji, user_id):
        """Deletes another user's reaction.
        Returns a 204 empty response on success."""
        encoded_emoji = url_encoder(emoji)
        url = f"{self.base_url}/channels/{channel_id}/messages/{message_id}/reactions/{encoded_emoji}/{user_id}"  # pylint: disable=line-too-long
        response = self.requests.delete(url, headers=self.headers)
        if response.status_code == 204:
            print("Success.")
        else:
            print(
                f"Failed to delete user reaction with status code {response.status_code}."
            )

    def edit_message(self, channel_id, message_id, content):
        """Edit a previously sent message.
        Returns a message object."""
        url = f"{self.base_url}/channels/{channel_id}/messages/{message_id}"
        payload = {"content": content}
        response = self.requests.patch(
            url, headers=self.headers, data=json.dumps(payload)
        )
        if response.status_code == 200:
            jresponse = json.loads(response.content.decode("utf-8"))
            return jresponse
        print(f"Failed to edit message with status code {response.status_code}.")
        return None

    def bulk_delete_messages(self, channel_id, message_ids):
        """Delete multiple messages in a single request.
        Returns a 204 empty response on success."""
        url = f"{self.base_url}/channels/{channel_id}/messages/bulk-delete"
        payload = {"messages": message_ids}
        response = self.requests.post(
            url, headers=self.headers, data=json.dumps(payload)
        )
        if response.status_code == 204:
            print("Success.")
        else:
            print(
                f"Failed to bulk delete messages with status code {response.status_code}."
            )

    def edit_channel_permissions(
        self, channel_id, overwrite_id, id_type, allow="0", deny="0"
    ):  # pylint: disable=too-many-arguments
        """Edit the channel permission overwrites for a user or role in a channel.
        Returns a 204 empty response on success."""
        url = f"{self.base_url}/channels/{channel_id}/permissions/{overwrite_id}"
        payload = {"allow": f"{allow}", "deny": f"{deny}", "type": id_type}
        response = self.requests.put(
            url, headers=self.headers, data=json.dumps(payload)
        )
        if response.status_code == 204:
            print("Success.")
        else:
            print(
                f"Failed to edit channel permissions with status code {response.status_code}."
            )

    def get_channel_invites(self, channel_id):
        """Returns a list of invite objects (with invite metadata) for the channel."""
        url = f"{self.base_url}/channels/{channel_id}/invites"
        response = self.requests.get(url, headers=self.headers)
        if response.status_code == 200:
            jresponse = json.loads(response.content.decode("utf-8"))
            return jresponse
        print(f"Failed to get channel invites with status code {response.status_code}.")
        return None

    def create_channel_invite(self, channel_id):
        """Create a new invite object for the channel.
        Returns an invite object."""
        url = f"{self.base_url}/channels/{channel_id}/invites"
        response = self.requests.post(url, headers=self.headers, data={})
        if response.status_code == 200:
            jresponse = json.loads(response.content.decode("utf-8"))
            return jresponse
        print(
            f"Failed to create channel invite with status code {response.status_code}."
        )
        return None

    def delete_channel_permission(self, channel_id, overwrite_id):
        """Delete a channel permission overwrite for a user or role in a channel.
        Returns a 204 empty response on success."""
        url = f"{self.base_url}/channels/{channel_id}/permissions/{overwrite_id}"
        response = self.requests.delete(url, headers=self.headers)
        if response.status_code == 204:
            print("Success.")
        else:
            print(
                f"Failed to delete channel permission with status code {response.status_code}."
            )

    def follow_announcement_channel(self, channel_id, webhook_channel_id):
        """Follow an Announcement Channel to send messages to a target channel.
        Returns a followed channel object."""
        url = f"{self.base_url}/channels/{channel_id}/followers"
        payload = {"webhook_channel_id": webhook_channel_id}
        response = self.requests.post(
            url, headers=self.headers, data=json.dumps(payload)
        )
        if response.status_code == 200:
            jresponse = json.loads(response.content.decode("utf-8"))
            return jresponse
        print(
            f"Failed to follow announcement channel with status code {response.status_code}."
        )
        return None

    def trigger_typing_indicator(self, channel_id):
        """Post a typing indicator for the specified channel.
        Returns a 204 empty response on success."""
        url = f"{self.base_url}/channels/{channel_id}/typing"
        response = self.requests.post(url, headers=self.headers)
        if response.status_code == 204:
            print("Success.")
        else:
            print(
                f"Failed to trigger typing indicator with status code {response.status_code}."
            )

    def get_pinned_messages(self, channel_id):
        """Returns all pinned messages in the channel as an array of message objects."""
        url = f"{self.base_url}/channels/{channel_id}/pins"
        response = self.requests.get(url, headers=self.headers)
        if response.status_code == 200:
            jresponse = json.loads(response.content.decode("utf-8"))
            return jresponse
        print(f"Failed to get pinned messages with status code {response.status_code}.")
        return None

    def pin_message(self, channel_id, message_id):
        """Pin a message in a channel."""
        url = f"{self.base_url}/channels/{channel_id}/pins/{message_id}"
        response = self.requests.put(url, headers=self.headers)
        if response.status_code == 204:
            print("Success.")
        else:
            print(f"Failed to pin message with status code {response.status_code}.")

    def unpin_message(self, channel_id, message_id):
        """Unpin a message in a channel."""
        url = f"{self.base_url}/channels/{channel_id}/pins/{message_id}"
        response = self.requests.delete(url, headers=self.headers)
        if response.status_code == 204:
            print("Success.")
        else:
            print(f"Failed to unpin message with status code {response.status_code}.")

    def group_dm_add_recipient(self, channel_id, user_id, access_token, nick):
        """Adds a recipient to a Group DM using their access token."""
        url = f"{self.base_url}/channels/{channel_id}/recipients/{user_id}"
        payload = {"access_token": access_token, "nick": nick}
        response = self.requests.put(
            url, headers=self.headers, data=json.dumps(payload)
        )
        if response.status_code == 204:
            print("Success.")
        else:
            print(
                f"Failed to add group dm recipient with status code {response.status_code}."
            )

    def group_dm_remove_recipient(self, channel_id, user_id):
        """Unpin a message in a channel."""
        url = f"{self.base_url}/channels/{channel_id}/recipients/{user_id}"
        response = self.requests.delete(url, headers=self.headers)
        if response.status_code == 204:
            print("Success.")
        else:
            print(
                f"Failed to remove grouo dm recipient with status code {response.status_code}."
            )

    # Guild

    def create_guild(self, guild_name, channel_name):
        """Create a new guild.
        Returns a guild object on success."""
        url = f"{self.base_url}/guilds"
        payload = {"name": guild_name, "channels": [{"name": channel_name, "type": 0}]}
        response = self.requests.post(
            url, headers=self.headers, data=json.dumps(payload)
        )
        if response.status_code == 201:
            jresponse = json.loads(response.content.decode("utf-8"))
            return jresponse
        print(f"Failed to create guild with status code {response.status_code}.")
        return None

    def get_guild_channels(self, guild_id):
        """Returns a list of guild channel objects."""
        url = f"{self.base_url}/guilds/{guild_id}/channels"
        response = self.requests.get(url, headers=self.headers)
        if response.status_code == 200:
            jresponse = json.loads(response.content.decode("utf-8"))
            return jresponse
        print(f"Failed to get guild channels with status code {response.status_code}.")
        return None

    def create_guild_channel(self, guild_id, channel_name):
        """Create a new channel object for the guild.
        Returns the new channel object on success."""
        url = f"{self.base_url}/guilds/{guild_id}/channels"
        payload = {"name": channel_name}
        response = self.requests.post(
            url, headers=self.headers, data=json.dumps(payload)
        )
        if response.status_code == 201:
            jresponse = json.loads(response.content.decode("utf-8"))
            return jresponse
        print(
            f"Failed to create guild channel with status code {response.status_code}."
        )
        return None

    def list_guild_members(self, guild_id):
        """Returns a list of guild member objects that are members of the guild."""
        url = f"{self.base_url}/guilds/{guild_id}/members"
        response = self.requests.get(url, headers=self.headers)
        if response.status_code == 200:
            jresponse = json.loads(response.content.decode("utf-8"))
            return jresponse
        print(f"Failed to list guild members with status code {response.status_code}.")
        return None

    def get_guild_roles(self, guild_id):
        """Returns a list of role objects for the guild."""
        url = f"{self.base_url}/guilds/{guild_id}/roles"
        response = self.requests.get(url, headers=self.headers)
        if response.status_code == 200:
            jresponse = json.loads(response.content.decode("utf-8"))
            return jresponse
        print(f"Failed to get guild roles with status code {response.status_code}.")
        return None

    # todo: use the servers @everyone perms as the default instead of a fixed default

    def create_guild_role(
        self,
        guild_id,
        name="new role",
        permissions="137411140505153",
        color=0,
        hoist=False,
        image_data=None,
        unicode_emoji=None,
        mentionable=False,  # pylint: disable=line-too-long
    ):  # pylint: disable=too-many-arguments
        """Create a new role for the guild."""
        url = f"{self.base_url}/guilds/{guild_id}/roles"
        payload = {
            "name": name,
            "permissions": permissions,
            "color": color,
            "hoist": hoist,
            "image_data": image_data,
            "unicode_emoji": unicode_emoji,
            "mentionable": mentionable,
        }
        response = self.requests.post(
            url, headers=self.headers, data=json.dumps(payload)
        )
        if response.status_code == 200:
            jresponse = json.loads(response.content.decode("utf-8"))
            return jresponse
        print(f"Failed to create guild role with status code {response.status_code}.")
        return None

    # User

    def get_current_user(self):
        """Returns the user object of the requester's account."""
        url = f"{self.base_url}/users/@me"
        response = self.requests.get(url, headers=self.headers)
        if response.status_code == 200:
            jresponse = json.loads(response.content.decode("utf-8"))
            return jresponse
        print(f"Failed to get current user with status code {response.status_code}.")
        return None

    def get_current_user_guilds(self):
        """Returns a list of partial guild objects the current user is a member of."""
        url = f"{self.base_url}/users/@me/guilds"
        response = self.requests.get(url, headers=self.headers)
        if response.status_code == 200:
            jresponse = json.loads(response.content.decode("utf-8"))
            return jresponse
        print(
            f"Failed to get current user guilds with status code {response.status_code}."
        )
        return None

    # Gateway

    def get_gateway(self):
        """Returns an object with a valid WSS URL."""
        url = f"{self.base_url}/gateway"
        response = self.requests.get(url, headers=self.headers)
        if response.status_code == 200:
            jresponse = json.loads(response.content.decode("utf-8"))
            return jresponse
        print(f"Failed to get gateway with status code {response.status_code}.")
        return None

    def get_gateway_bot(self):
        """Returns an object based on the information in Get Gateway,
        plus additional metadata that can help during the operation of large or sharded bots.
        """
        url = f"{self.base_url}/gateway/bot"
        response = self.requests.get(url, headers=self.headers)
        if response.status_code == 200:
            jresponse = json.loads(response.content.decode("utf-8"))
            return jresponse
        print(f"Failed to get gateway bot with status code {response.status_code}.")
        return None
