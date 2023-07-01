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
import adafruit_requests
import binascii

def isalpha(char):
    """CircuitPython implementation of .isalpha()"""
    if not (char >= 'a' <= 'z' or char >= 'A' <= 'Z'):
        return False
    return True

def isdigit(char):
    """CircuitPython implementation of .isdigit()"""
    char_ascii = ord(char)
    if not (char_ascii >= 48 and char_ascii <= 57):
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
        if isalnum(char) or char in ['-', '_', '.', '~']:
            encoded_url += char
        elif is_valid_codepoint(char):
            encoded_url += '%' + binascii.hexlify(char.encode(), '%').decode().upper()
    return encoded_url

class RESTAPI:
    """Class for Discord's REST API"""
    def __init__(self, base_url, auth_type, token, pool, ssl=None):
        self.base_url = base_url
        self.auth_type = auth_type
        self.token = token
        self.requests = adafruit_requests.Session(pool, ssl)
        self.headers = {
            'Authorization': f'{auth_type} {token}',
            'Content-Type': 'application/json',
            'Content-Length': '0'
        }
    
    # Channel
    
    def get_channel(self, channel_id):
        """Get a channel by ID.
        Returns a channel object."""
        url = (
            f'{self.base_url}/channels/{channel_id}'
        )
        response = self.requests.get(url, headers=self.headers)
        if response.status_code == 200:
            jresponse = json.loads(response.content.decode("utf-8"))
            return jresponse
        else:
            print(
              f'Failed to get channel with status code {response.status_code}.'
            )
    
    def modify_channel(self, channel_id, channel_name):
        """Update a channel's settings.
        Returns a channel on success, and a 400 BAD REQUEST on invalid parameters.
        All JSON parameters are optional."""
        url = (
            f'{self.base_url}/channels/{channel_id}'
        )
        payload = {
            'name': channel_name
        }
        response = self.requests.patch(url, headers=self.headers, data=json.dumps(payload))
        if response.status_code == 200:
            jresponse = json.loads(response.content.decode("utf-8"))
            return jresponse
        else:
            print(
              f'Failed to modify channel with status code {response.status_code}.'
            )
    
    def delete_close_channel(self, channel_id):
        """Delete a channel, or close a private message.
        Returns a channel object on success."""
        url = (
            f'{self.base_url}/channels/{channel_id}'
        )
        response = self.requests.delete(url, headers=self.headers)
        if response.status_code == 200:
            jresponse = json.loads(response.content.decode("utf-8"))
            return jresponse
        else:
            print(
              f'Failed to get delete/close channel with status code {response.status_code}.'
            )
    
    def get_channel_messages(self, channel_id):
        """Retrieves the messages in a channel.
        Returns an array of message objects on success."""
        url = (
            f'{self.base_url}/channels/{channel_id}/messages'
        )
        response = self.requests.get(url, headers=self.headers)
        if response.status_code == 200:
            jresponse = json.loads(response.content.decode("utf-8"))
            return jresponse
        else:
            print(
              f'Failed to get channel messages with status code {response.status_code}.'
            )
    
    def get_channel_message(self, channel_id, message_id):
        url = f'{self.base_url}/channels/{channel_id}/messages/{message_id}'
        response = self.requests.get(url, headers=self.headers)
        if response.status_code == 200:
            jresponse = json.loads(response.content.decode("utf-8"))
            return jresponse
        else:
            print(
              f'Failed to get channel message with status code {response.status_code}.'
            )
    
    def create_message(self, channel_id, content):
        url = f'{self.base_url}/channels/{channel_id}/messages'
        payload = {
            'content': content
        }
        response = self.requests.post(url, headers=self.headers, data=json.dumps(payload))
        if response.status_code == 200:
            jresponse = json.loads(response.content.decode("utf-8"))
            return jresponse
        else:
            print(
              f'Failed to create message with status code {response.status_code}.'
            )
    
    def crosspost_message(self, channel_id, message_id):
        url = f'{self.base_url}/channels/{channel_id}/messages/{message_id}/crosspost'
        response = self.requests.post(url, headers=self.headers)
        if response.status_code == 200:
            jresponse = json.loads(response.content.decode("utf-8"))
            return jresponse
        else:
            print(
              f'Failed to crosspost message with status code {response.status_code}.'
            )
    
    def create_reaction(self, channel_id, message_id, emoji):
        encoded_emoji = url_encoder(emoji)
        url = (
            f'{self.base_url}/channels/{channel_id}/messages/{message_id}/reactions/{encoded_emoji}/@me'
        )
        response = self.requests.put(url, headers=self.headers)
        if response.status_code == 204:
            print("Success.")
        else:
            print(
              f'Failed to create reaction with status code {response.status_code}.'
            )
    
    def delete_own_reaction(self, channel_id, message_id, emoji):
        encoded_emoji = url_encoder(emoji)
        url = f'{self.base_url}/channels/{channel_id}/messages/{message_id}/reactions/{encoded_emoji}/@me'
        response = self.requests.delete(url, headers=self.headers)
        if response.status_code == 204:
            print("Success.")
        else:
            print(
              f'Failed to delete own reaction with status code {response.status_code}.'
            )
    
    def delete_user_reaction(self, channel_id, message_id, emoji, user_id):
        encoded_emoji = url_encoder(emoji)
        url = f'{self.base_url}/channels/{channel_id}/messages/{message_id}/reactions/{encoded_emoji}/{user_id}'
        response = self.requests.delete(url, headers=self.headers)
        if response.status_code == 204:
            print("Success.")
        else:
            print(
              f'Failed to delete user reaction with status code {response.status_code}.'
            )
    
    def edit_message(self, channel_id, message_id, content):
        url = f'{self.base_url}/channels/{channel_id}/messages/{message_id}'
        payload = {
            'content': content
        }
        response = self.requests.patch(url, headers=self.headers, data=json.dumps(payload))
        if response.status_code == 200:
            jresponse = json.loads(response.content.decode("utf-8"))
            return jresponse
        else:
            print(
              f'Failed to edit message with status code {response.status_code}.'
            )
    
    def bulk_delete_messages(self, channel_id, message_ids):
        url = f'{self.base_url}/channels/{channel_id}/messages/bulk-delete'
        payload = {
            'messages': message_ids
        }
        response = self.requests.post(url, headers=self.headers, data=json.dumps(payload))
        if response.status_code == 204:
            print("Success.")
        else:
            print(
              f'Failed to bulk delete messages with status code {response.status_code}.'
            )
    
    def edit_channel_permissions(self, channel_id, overwrite_id, id_type, allow="0", deny="0"):
        url = f'{self.base_url}/channels/{channel_id}/permissions/{overwrite_id}'
        payload = {
            'allow': f'{allow}',
            'deny': f'{deny}',
            'type': id_type
        }
        response = self.requests.put(url, headers=self.headers, data=json.dumps(payload))
        if response.status_code == 204:
            print("Success.")
        else:
            print(
              f'Failed to edit channel permissions with status code {response.status_code}.'
            )
    
    def get_channel_invites(self, channel_id):
        url = f'{self.base_url}/channels/{channel_id}/invites'
        response = self.requests.get(url, headers=self.headers)
        if response.status_code == 200:
            jresponse = json.loads(response.content.decode("utf-8"))
            return jresponse
        else:
            print(
              f'Failed to get channel invites with status code {response.status_code}.'
            )
    
    def create_channel_invite(self, channel_id):
        url = f'{self.base_url}/channels/{channel_id}/invites'
        response = self.requests.post(url, headers=self.headers, data={})
        if response.status_code == 200:
            jresponse = json.loads(response.content.decode("utf-8"))
            return jresponse
        else:
            print(
              f'Failed to create channel invite with status code {response.status_code}.'
            )
    
    def delete_channel_permission(self, channel_id, overwrite_id):
        url = f'{self.base_url}/channels/{channel_id}/permissions/{overwrite_id}'
        response = self.requests.delete(url, headers=self.headers)
        if response.status_code == 204:
            print("Success.")
        else:
            print(
              f'Failed to delete channel permission with status code {response.status_code}.'
            )
    
    # Guild
    
    def create_guild(self, guild_name, channel_name):
        url = f'{self.base_url}/guilds'
        payload = {
            'name': guild_name,
            'channels': [
                {
                    'name': channel_name,
                    'type': 0
                }
            ]
        }
        response = self.requests.post(url, headers=self.headers, data=json.dumps(payload))
        if response.status_code == 201:
            jresponse = json.loads(response.content.decode("utf-8"))
            return jresponse
        else:
            print(
              f'Failed to create guild with status code {response.status_code}.'
            )
    
    def get_guild_channels(self, guild_id):
        url = f'{self.base_url}/guilds/{guild_id}/channels'
        response = self.requests.get(url, headers=self.headers)
        if response.status_code == 200:
            jresponse = json.loads(response.content.decode("utf-8"))
            return jresponse
        else:
            print(
              f'Failed to get guild channels with status code {response.status_code}.'
            )
    
    def create_guild_channel(self, guild_id, channel_name):
        url = f'{self.base_url}/guilds/{guild_id}/channels'
        response = self.requests.get(url, headers=self.headers)
        if response.status_code == 201:
            jresponse = json.loads(response.content.decode("utf-8"))
            return jresponse
        else:
            print(
              f'Failed to create guild channel with status code {response.status_code}.'
            )
    
    def list_guild_members(self, guild_id):
        url = f'{self.base_url}/guilds/{guild_id}/members'
        response = self.requests.get(url, headers=self.headers)
        if response.status_code == 200:
            jresponse = json.loads(response.content.decode("utf-8"))
            return jresponse
        else:
            print(
              f'Failed to list guild members with status code {response.status_code}.'
            )
    
    def get_guild_roles(self, guild_id):
        url = f'{self.base_url}/guilds/{guild_id}/roles'
        response = self.requests.get(url, headers=self.headers)
        if response.status_code == 200:
            jresponse = json.loads(response.content.decode("utf-8"))
            return jresponse
        else:
            print(
              f'Failed to list guild members with status code {response.status_code}.'
            )
    
    # User
    
    def get_current_user(self):
        url = f'{self.base_url}/users/@me'
        response = self.requests.get(url, headers=self.headers)
        if response.status_code == 200:
            jresponse = json.loads(response.content.decode("utf-8"))
            return jresponse
        else:
            print(
              f'Failed to get current user with status code {response.status_code}.'
            )
    
    def get_current_user_guilds(self):
        url = f'{self.base_url}/users/@me/guilds'
        response = self.requests.get(url, headers=self.headers)
        if response.status_code == 200:
            jresponse = json.loads(response.content.decode("utf-8"))
            return jresponse
        else:
            print(
              f'Failed to get current user guilds with status code {response.status_code}.'
            )
    
    # Gateway
    
    def get_gateway(self):
        url = f'{self.base_url}/gateway'
        response = self.requests.get(url, headers=self.headers)
        if response.status_code == 200:
            jresponse = json.loads(response.content.decode("utf-8"))
            return jresponse
        else:
            print(
              f'Failed to get gateway with status code {response.status_code}.'
            )
    
    def get_gateway_bot(self):
        url = f'{self.base_url}/gateway/bot'
        response = self.requests.get(url, headers=self.headers)
        if response.status_code == 200:
            jresponse = json.loads(response.content.decode("utf-8"))
            return jresponse
        else:
            print(
              f'Failed to get gateway bot with status code {response.status_code}.'
            )
