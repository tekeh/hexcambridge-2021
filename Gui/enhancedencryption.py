from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.factory import Factory
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.lang import Builder

import numpy as np

import sys
# sys.path.append('/home/res0lve/research/hexcambridge-2021/Model')
# import local_run as chive


import os

class LoadDialog(FloatLayout):
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)


class SaveDialog(FloatLayout):
    save = ObjectProperty(None)
    data_input = ObjectProperty(None)
    cancel = ObjectProperty(None)


class MainScreen(Screen):
    pass

class ReceiverScreen(Screen):
    pass

class ScreenManagement(ScreenManager):
    pass


class OwnerScreen(Screen):
    loadfile = ObjectProperty(None)
    savefile = ObjectProperty(None)
    text_input = ObjectProperty(None)
    plain_x_dat = ObjectProperty(None)
    plain_y_dat = ObjectProperty(None)

    def dismiss_popup(self):
        self._popup.dismiss()

    def show_load(self):
        content = LoadDialog(load=self.load, cancel=self.dismiss_popup)
        self._popup = Popup(title="Load file", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()

    def show_save(self):
        content = SaveDialog(save=self.save, cancel=self.dismiss_popup)
        self._popup = Popup(title="Save file", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()

    def load(self, path, filename):
        #'with open(os.path.join(path, filename[0])) as stream:
            #self.data_input = stream.read()
            #np.genfromtxt(
        self.data_input = np.loadtxt(filename[0], delimiter=",")
        self.plain_x_dat = self.data_input[0]
        self.plain_y_dat = self.data_input[1]

        self.dismiss_popup()

    def encrypt_and_compute(self):
        # chive.main(x=self.plain_x_dat, y=self.plain_y_dat)
        pass

    def save(self, path, filename):
        with open(os.path.join(path, filename), 'w') as stream:
            stream.write(self.text_input.text)

        self.dismiss_popup()

    # def process_ip(self):
    #     text_input = self.ids.ip_input.text
    #     print(text_input)

    def process_publickey(self):
        text_input = self.ids.publickey_input.text
        print(text_input)

presentation = Builder.load_file("enhancedencryption.kv")

class EnhancedEncryption(App):

    def build(self):
        return presentation


Factory.register('OwnerScreen', cls=OwnerScreen)
Factory.register('LoadDialog', cls=LoadDialog)
Factory.register('SaveDialog', cls=SaveDialog)


if __name__ == '__main__':
    EnhancedEncryption().run()
