import json
import os
import sys

import nest_asyncio
from prompt_toolkit.application import Application
from prompt_toolkit.layout import Layout, DynamicContainer
from prompt_toolkit.shortcuts import set_title
from prompt_toolkit.widgets import Frame

import menus
from riitag import oauth2, user, watcher, presence, preferences

nest_asyncio.apply()

try:
    with open('config.json', 'r') as file:
        CONFIG: dict = json.load(file)
except FileNotFoundError:
    print('[!] The config file seems to be missing.')
    print('[!] Please re-download this program or create it manually.')

    sys.exit(1)

if not os.path.isdir('cache'):
    os.mkdir('cache/')


class RiiTagApplication(Application):
    def __init__(self, *args, **kwargs):
        self._current_menu: menus.Menu = None

        self.set_menu(menus.SplashScreen)
        set_title(self.version_string)

        super().__init__(*args, **kwargs,
                         layout=Layout(DynamicContainer(self._get_layout)),
                         full_screen=True)

        self.token: oauth2.OAuth2Token = None
        self.user: user.User = None

        self.preferences = preferences.Preferences.load('cache/prefs.json')
        self.oauth_client = oauth2.OAuth2Client(CONFIG.get('oauth2'))
        self.rpc_handler = presence.RPCHandler(
            CONFIG.get('rpc', {}).get('client_id')
        )
        self.riitag_watcher: watcher.RiitagWatcher = None

        self.oauth_client.start_server(CONFIG.get('port', 4000))

    def _get_layout(self):
        menu_layout = self._current_menu.get_layout()
        if self._current_menu.is_framed:
            menu_layout = Frame(menu_layout, title=self.header_string)

        return menu_layout

    ######################
    # Overridden Methods #
    ######################

    @property
    def key_bindings(self):
        return self._current_menu.get_all_kb()

    @key_bindings.setter
    def key_bindings(self, value):
        return

    ##################
    # Custom Methods #
    ##################

    @property
    def version_string(self):
        version = CONFIG.get('version', '<unknown version>')

        return f'RiiTag-RPC v{version}'

    @property
    def header_string(self):
        return f'RiiTag-RPC - {self._current_menu.name}'

    def set_menu(self, menu):
        if not issubclass(menu, menus.Menu):
            raise ValueError('menu must be a subclass of menus.Menu')

        if self._current_menu:
            self._current_menu.on_exit()

        self._current_menu = menu(self)
        if hasattr(self, '_is_running'):
            self.invalidate()
        self._current_menu.on_start()


def main():
    application = RiiTagApplication()
    application.run()


if __name__ == "__main__":
    main()