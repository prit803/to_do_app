"""To-Do List app (Kivy + SQLite). Run on desktop with:  python main.py"""
import os

from kivy.app import App
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.modalview import ModalView
from kivy.uix.screenmanager import NoTransition, ScreenManager

import theme as T
from components import ConfirmDialog, NavBar, TaskForm
from database import TaskDatabase
from screens import SettingsScreen, TaskListScreen

Window.clearcolor = T.BG


class TodoApp(App):
    title = 'To-Do List'

    def build(self):
        # Keeps the focused text box visible when the Android keyboard opens.
        Window.softinput_mode = 'below_target'

        self.db = None
        try:
            self.db = TaskDatabase(os.path.join(self.user_data_dir, 'todo.db'))
        except Exception as exc:  # pragma: no cover
            print('Database error:', exc)

        root = BoxLayout(orientation='vertical')
        self.sm = ScreenManager(transition=NoTransition())
        self.screens = {
            'home': TaskListScreen(name='home', completed=False),
            'completed': TaskListScreen(name='completed', completed=True),
            'settings': SettingsScreen(name='settings'),
        }
        for screen in self.screens.values():
            self.sm.add_widget(screen)
        root.add_widget(self.sm)

        self.nav = NavBar(on_select=self.show_screen)
        root.add_widget(self.nav)

        Window.bind(on_keyboard=self._on_keyboard)
        return root

    def on_start(self):
        self.refresh_all()

    def on_pause(self):
        return True   # keep the app alive when it goes to the background

    # ---------- navigation ----------
    def show_screen(self, key):
        self.sm.current = key
        self.nav.set_active(key)

    def _on_keyboard(self, _window, key, *_args):
        """Android back button: close popups first, then go Home, then exit."""
        if key != 27:
            return False
        if any(isinstance(child, ModalView) for child in Window.children):
            return True
        if self.sm.current != 'home':
            self.show_screen('home')
            return True
        return False

    def refresh_all(self):
        for screen in self.screens.values():
            screen.refresh()

    # ---------- safe database access ----------
    def run_db(self, func, *args, default=None, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as exc:
            ConfirmDialog('Something went wrong', 'The action could not be completed.\n\n%s' % exc,
                          show_cancel=False).open()
            return default

    # ---------- task actions ----------
    def open_task_form(self, task=None):
        TaskForm(on_save=lambda data: self._save_task(task, data), task=task).open()

    def _save_task(self, task, data):
        if task:
            self.run_db(self.db.update_task, task['id'], **data)
        else:
            self.run_db(self.db.add_task, **data)
        self.refresh_all()

    def toggle_task(self, task):
        self.run_db(self.db.set_completed, task['id'], not task['completed'])
        self.refresh_all()

    def confirm_delete_task(self, task):
        ConfirmDialog('Delete task?', '"%s" will be permanently deleted.' % task['title'],
                      on_confirm=lambda: self._delete_task(task), confirm_text='Delete',
                      danger=True).open()

    def _delete_task(self, task):
        self.run_db(self.db.delete_task, task['id'])
        self.refresh_all()

    def confirm_clear_completed(self):
        ConfirmDialog('Delete completed tasks?', 'All completed tasks will be removed.',
                      on_confirm=lambda: self._clear(self.db.delete_completed),
                      confirm_text='Delete', danger=True).open()

    def confirm_clear_all(self):
        ConfirmDialog('Delete ALL tasks?', 'Every task will be permanently deleted.',
                      on_confirm=lambda: self._clear(self.db.delete_all),
                      confirm_text='Delete all', danger=True).open()

    def _clear(self, func):
        self.run_db(func)
        self.refresh_all()


if __name__ == '__main__':
    TodoApp().run()
