"""The three screens: Home (pending), Completed and Settings."""
from datetime import date

from kivy.app import App
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView

import theme as T
from components import (Card, FloatingButton, ProgressStrip, RoundedButton, RoundedInput,
                        TaskCard, auto_height, wrap_label)


def page_header(title):
    box = auto_height(BoxLayout(orientation='vertical', spacing=dp(2)))
    box.add_widget(wrap_label(title, font_size='32sp', bold=True))
    subtitle = wrap_label('', font_size='15sp', color=T.MUTED)
    box.add_widget(subtitle)
    return box, subtitle


class PageScreen(Screen):
    """A screen with a scrolling column of content."""

    def __init__(self, bottom_pad=24, **kwargs):
        super().__init__(**kwargs)
        self.scroll = ScrollView(do_scroll_x=False, bar_width=dp(3), bar_color=T.ACCENT)
        self.content = auto_height(BoxLayout(
            orientation='vertical', spacing=dp(14),
            padding=[dp(18), dp(22), dp(18), dp(bottom_pad)]))
        self.scroll.add_widget(self.content)
        self.add_widget(self.scroll)

    def on_pre_enter(self, *args):
        self.refresh()

    def refresh(self):
        pass


class TaskListScreen(PageScreen):
    """Home shows pending tasks (+ dashboard); Completed shows finished ones."""

    def __init__(self, completed=False, **kwargs):
        super().__init__(bottom_pad=110, **kwargs)
        self.completed = completed

        header, self.subtitle = page_header('Completed' if completed else 'My Tasks')
        self.content.add_widget(header)

        if not completed:
            self._build_stats_card()

        self.search = RoundedInput(hint='Search tasks...')
        self.search.input.bind(text=lambda *_: self.refresh())
        self.content.add_widget(self.search)

        self.section = wrap_label('', font_size='18sp', bold=True)
        self.content.add_widget(self.section)
        self.list_box = auto_height(BoxLayout(orientation='vertical', spacing=dp(12)))
        self.content.add_widget(self.list_box)

        if not completed:
            fab = FloatingButton(pos_hint={'right': 0.94, 'y': 0.03})
            fab.bind(on_release=lambda *_: App.get_running_app().open_task_form())
            self.add_widget(fab)

    def _build_stats_card(self):
        card = Card(orientation='vertical', bg_color=T.ACCENT, radius_dp=dp(22),
                    padding=dp(18), spacing=dp(10), size_hint_y=None)
        auto_height(card)
        card.add_widget(wrap_label('Your progress', font_size='16sp', color=(1, 1, 1, 0.85)))
        row = BoxLayout(size_hint_y=None, height=dp(70))
        self.stat_labels = {}
        for key, caption in (('total', 'Total'), ('completed', 'Completed'),
                             ('pending', 'Pending')):
            box = BoxLayout(orientation='vertical')
            number = Label(text='0', font_size='30sp', bold=True, color=T.WHITE,
                           size_hint_y=0.65)
            box.add_widget(number)
            box.add_widget(Label(text=caption, font_size='13sp', color=(1, 1, 1, 0.85),
                                 size_hint_y=0.35))
            self.stat_labels[key] = number
            row.add_widget(box)
        card.add_widget(row)
        self.progress = ProgressStrip()
        card.add_widget(self.progress)
        self.content.add_widget(card)

    def refresh(self):
        app = App.get_running_app()
        query = self.search.text.strip()
        tasks = app.run_db(app.db.get_tasks, self.completed, query, default=[]) or []
        stats = app.run_db(app.db.get_stats,
                           default={'total': 0, 'completed': 0, 'pending': 0, 'overdue': 0})

        if self.completed:
            self.subtitle.text = '%d finished task%s' % (
                stats['completed'], '' if stats['completed'] == 1 else 's')
            self.section.text = 'Completed tasks (%d)' % len(tasks)
        else:
            self.subtitle.text = date.today().strftime('%A, %d %B')
            for key, label in self.stat_labels.items():
                label.text = str(stats[key])
            self.progress.value = (stats['completed'] / stats['total']) if stats['total'] else 0
            self.section.text = 'Pending tasks (%d)' % len(tasks)
            if stats['overdue']:
                self.subtitle.text += '   |   %d overdue' % stats['overdue']

        self.list_box.clear_widgets()
        if not tasks:
            if query:
                message = 'No tasks match "%s".' % query
            elif self.completed:
                message = 'Nothing completed yet.\nTick a task to see it here.'
            else:
                message = 'No pending tasks.\nTap + to add your first task!'
            self.list_box.add_widget(wrap_label(
                '\n' + message, halign='center', font_size='17sp', color=T.MUTED))
            return
        for task in tasks:
            self.list_box.add_widget(TaskCard(
                task, on_toggle=app.toggle_task, on_edit=app.open_task_form,
                on_delete=app.confirm_delete_task))


class SettingsScreen(PageScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        header, subtitle = page_header('Settings')
        subtitle.text = 'Manage your data'
        self.content.add_widget(header)

        self.summary = wrap_label('', font_size='17sp')
        summary_card = Card(orientation='vertical', padding=dp(18), spacing=dp(8),
                            size_hint_y=None)
        auto_height(summary_card)
        summary_card.add_widget(wrap_label('Overview', font_size='18sp', bold=True))
        summary_card.add_widget(self.summary)
        self.content.add_widget(summary_card)

        data_card = Card(orientation='vertical', padding=dp(18), spacing=dp(12),
                         size_hint_y=None)
        auto_height(data_card)
        data_card.add_widget(wrap_label('Data', font_size='18sp', bold=True))
        clear_done = RoundedButton(text='Delete completed tasks', size_hint_y=None,
                                   height=dp(50), bg_color=T.ACCENT_SOFT,
                                   text_color=T.ACCENT)
        clear_done.bind(on_release=lambda *_: App.get_running_app().confirm_clear_completed())
        clear_all = RoundedButton(text='Delete ALL tasks', size_hint_y=None, height=dp(50),
                                  bg_color=T.DANGER_SOFT, text_color=T.DANGER)
        clear_all.bind(on_release=lambda *_: App.get_running_app().confirm_clear_all())
        data_card.add_widget(clear_done)
        data_card.add_widget(clear_all)
        self.content.add_widget(data_card)

        about = Card(orientation='vertical', padding=dp(18), spacing=dp(6), size_hint_y=None)
        auto_height(about)
        about.add_widget(wrap_label('About', font_size='18sp', bold=True))
        about.add_widget(wrap_label(
            'To-Do List  v1.0\nAll tasks are stored only on this phone. '
            'No internet or account needed.', font_size='15sp', color=T.MUTED))
        self.content.add_widget(about)

    def refresh(self):
        app = App.get_running_app()
        stats = app.run_db(app.db.get_stats,
                           default={'total': 0, 'completed': 0, 'pending': 0, 'overdue': 0})
        self.summary.text = ('Total tasks: %(total)d\nCompleted: %(completed)d\n'
                             'Pending: %(pending)d\nOverdue: %(overdue)d') % stats
