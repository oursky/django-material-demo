from django.db import models


class Settings(models.Model):
    managed = False

    primary_color = models.TextField()
    primary_color_light = models.TextField()
    primary_color_dark = models.TextField()
    secondary_color = models.TextField()
    secondary_color_light = models.TextField()
    success_color = models.TextField()
    error_color = models.TextField()
    link_color = models.TextField()

    def __init__(self, *args, **kwargs):
        self.session = kwargs['session']
        del kwargs['session']
        super().__init__(*args, **kwargs)
        self.load()

    def load(self):
        self.primary_color = self.session.get(
            'settings:--primary-color') or '#424242'
        self.primary_color_light = self.session.get(
            'settings:--primary-color-light') or '#686868'
        self.primary_color_dark = self.session.get(
            'settings:--primary-color-dark') or '#1c1c1c'
        self.secondary_color = self.session.get(
            'settings:--secondary-color') or '#37474f'
        self.secondary_color_light = self.session.get(
            'settings:--secondary-color-light') or '#56707c'
        self.success_color = self.session.get(
            'settings:--sucess-color') or '#607d8b'
        self.error_color = self.session.get(
            'settings:--error-color') or '#f44336'
        self.link_color = self.session.get(
            'settings:--link-color') or '#039be5'

    def save(self):
        self.session['settings:--primary-color'] = self.primary_color
        self.session['settings:--primary-color-light'] = self.primary_color_light
        self.session['settings:--primary-color-dark'] = self.primary_color_dark
        self.session['settings:--secondary-color'] = self.secondary_color
        self.session['settings:--secondary-color-light'] = self.secondary_color_light
        self.session['settings:--sucess-color'] = self.success_color
        self.session['settings:--error-color'] = self.error_color
        self.session['settings:--link-color'] = self.link_color
