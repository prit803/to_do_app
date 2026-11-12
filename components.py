"""Reusable UI building blocks: cards, buttons, dialogs, the task form..."""
from datetime import date, datetime, timedelta

from kivy.clock import Clock
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import BooleanProperty, ListProperty, NumericProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.modalview import ModalView
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from kivy.utils import escape_markup

import theme as T
from database import PRIORITIES

Builder.load_string('''
#:import T theme

<Card>:
    canvas.before:
        Color:
            rgba: self.bg_color
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [self.radius_dp]

<RoundedButton>:
    background_normal: ''
    background_down: ''
    background_color: 0, 0, 0, 0
    color: self.text_color
    font_size: '16sp'
    bold: True
    canvas.before:
        Color:
            rgba: self.bg_color
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [self.radius_dp]
        Color:
            rgba: 0, 0, 0, (0.12 if self.state == 'down' else 0)
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [self.radius_dp]

<FloatingButton>:
    size_hint: None, None
    size: dp(62), dp(62)
    radius_dp: dp(31)
    font_size: '36sp'
    text: '+'

<Badge>:
    size_hint: None, None
    size: self.texture_size[0] + dp(20), dp(24)
    font_size: '12sp'
    bold: True
    color: self.fg_color
    canvas.before:
        Color:
            rgba: self.bg_color
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(12)]

<CheckCircle>:
    size_hint: None, None
    size: dp(34), dp(34)
    canvas:
        Color:
            rgba: T.ACCENT[0], T.ACCENT[1], T.ACCENT[2], (1 if self.done else 0)
        Ellipse:
            pos: self.pos
            size: self.size
        Color:
            rgba: T.ACCENT
        Line:
            circle: self.center_x, self.center_y, self.width / 2 - dp(1)
            width: dp(1.6)
        Color:
            rgba: 1, 1, 1, (1 if self.done else 0)
        Line:
            points: self.center_x - dp(8), self.center_y, self.center_x - dp(2), self.center_y - dp(6), self.center_x + dp(8), self.center_y + dp(6)
            width: dp(2)

<ProgressStrip>:
    size_hint_y: None
    height: dp(8)
    canvas:
        Color:
            rgba: 1, 1, 1, 0.3
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(4)]
        Color:
            rgba: 1, 1, 1, 1
        RoundedRectangle:
            pos: self.pos
            size: self.width * self.value, self.height
            radius: [dp(4)]

<NavBar>:
    canvas.before:
        Color:
            rgba: 1, 1, 1, 1
        Rectangle:
            pos: self.pos
            size: self.size
        Color:
            rgba: T.LINE
        Rectangle:
            pos: self.x, self.top - dp(1)
            size: self.width, dp(1)

<NavButton>:
    background_normal: ''
    background_down: ''
    background_color: 0, 0, 0, 0
    font_size: '15sp'
    bold: self.active
    color: T.ACCENT if self.active else T.MUTED
    canvas.before:
        Color:
            rgba: T.ACCENT_SOFT[0], T.ACCENT_SOFT[1], T.ACCENT_SOFT[2], (1 if self.active else 0)
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(16)]
''')


# ---------------------------------------------------------------- helpers
def auto_height(box):
    """Make a BoxLayout exactly as tall as its children."""
    box.size_hint_y = None
    box.bind(minimum_height=box.setter('height'))
    return box


def wrap_label(text='', halign='left', **kwargs):
    """A label that wraps its text and grows in height to fit it."""
    kwargs.setdefault('color', T.TEXT)
    label = Label(text=text, size_hint_y=None, halign=halign, valign='top', **kwargs)
    label.bind(width=lambda w, v: setattr(w, 'text_size', (v if v > 0 else None, None)))
    label.bind(texture_size=lambda w, size: setattr(w, 'height', size[1]))
    return label


def describe_due(due, completed=False):
    """Return (text, is_overdue) for a stored YYYY-MM-DD due date."""
    if not due:
        return 'No due date', False
    try:
        due_day = datetime.strptime(due, '%Y-%m-%d').date()
    except ValueError:
        return due, False
    delta = (due_day - date.today()).days
    if delta == 0:
        text = 'Due today'
    elif delta == 1:
        text = 'Due tomorrow'
    elif delta == -1:
        text = 'Due yesterday'
    else:
        text = 'Due ' + due_day.strftime('%d %b %Y')
    return text, (delta < 0 and not completed)


# ---------------------------------------------------------------- basic widgets
class Card(BoxLayout):
    bg_color = ListProperty(T.CARD)
    radius_dp = NumericProperty(dp(16))


class RoundedButton(Button):
    bg_color = ListProperty(T.ACCENT)
    text_color = ListProperty(T.WHITE)
    radius_dp = NumericProperty(dp(14))


class FloatingButton(RoundedButton):
    pass


class Badge(Label):
    bg_color = ListProperty(T.ACCENT_SOFT)
    fg_color = ListProperty(T.ACCENT)


class CheckCircle(ButtonBehavior, Widget):
    done = BooleanProperty(False)


class ProgressStrip(Widget):
    value = NumericProperty(0)


class NavButton(Button):
    active = BooleanProperty(False)


class NavBar(BoxLayout):
    ITEMS = (('home', 'Home'), ('completed', 'Completed'), ('settings', 'Settings'))

    def __init__(self, on_select, **kwargs):
        super().__init__(orientation='horizontal', size_hint_y=None, height=dp(66),
                         padding=[dp(12), dp(9)], spacing=dp(8), **kwargs)
        self.buttons = {}
        for key, label in self.ITEMS:
            button = NavButton(text=label)
            button.bind(on_release=lambda _b, k=key: on_select(k))
            self.buttons[key] = button
            self.add_widget(button)
        self.set_active('home')

    def set_active(self, key):
        for name, button in self.buttons.items():
            button.active = (name == key)


class RoundedInput(Card):
    """A text field with a rounded background. Read/write text via `.text`."""

    def __init__(self, hint='', text='', multiline=False, height_dp=48, **kwargs):
        super().__init__(orientation='vertical', size_hint_y=None, height=dp(height_dp),
                         padding=[dp(14), dp(2)], **kwargs)
        pad = [0, dp(10), 0, dp(6)] if multiline else [0, dp(13), 0, dp(10)]
        self.input = TextInput(
            text=text, hint_text=hint, multiline=multiline, font_size='16sp',
            background_normal='', background_active='', background_color=(0, 0, 0, 0),
            foreground_color=T.TEXT, hint_text_color=T.MUTED, cursor_color=T.ACCENT,
            selection_color=(T.ACCENT[0], T.ACCENT[1], T.ACCENT[2], 0.3), padding=pad,
            write_tab=False)
        self.add_widget(self.input)

    @property
    def text(self):
        return self.input.text

    @text.setter
    def text(self, value):
        self.input.text = value


# ---------------------------------------------------------------- task card
class TaskCard(Card):
    def __init__(self, task, on_toggle, on_edit, on_delete, **kwargs):
        super().__init__(orientation='vertical', padding=dp(14), spacing=dp(10), **kwargs)
        auto_height(self)
        done = bool(task['completed'])

        main = auto_height(BoxLayout(orientation='horizontal', spacing=dp(12)))
        check = CheckCircle(done=done, pos_hint={'top': 1})
        check.bind(on_release=lambda *_: on_toggle(task))
        main.add_widget(check)

        column = auto_height(BoxLayout(orientation='vertical', spacing=dp(6)))
        title = escape_markup(task['title'])
        if done:
            title = '[s]' + title + '[/s]'
        column.add_widget(wrap_label(
            title, markup=True, font_size='18sp', bold=True,
            color=T.MUTED if done else T.TEXT))
        if task['description']:
            column.add_widget(wrap_label(
                task['description'], font_size='15sp', color=T.MUTED, max_lines=3))

        meta = BoxLayout(size_hint_y=None, height=dp(24), spacing=dp(8))
        meta.add_widget(Badge(text=task['priority'], fg_color=T.WHITE,
                              bg_color=T.PRIORITY_COLORS.get(task['priority'], T.ACCENT)))
        due_text, overdue = describe_due(task['due_date'], done)
        meta.add_widget(Badge(
            text=due_text,
            fg_color=T.DANGER if overdue else T.ACCENT,
            bg_color=T.DANGER_SOFT if overdue else T.ACCENT_SOFT))
        meta.add_widget(Widget())
        column.add_widget(meta)
        main.add_widget(column)
        self.add_widget(main)

        actions = BoxLayout(size_hint_y=None, height=dp(38), spacing=dp(8))
        actions.add_widget(Widget())
        edit = RoundedButton(text='Edit', font_size='14sp', size_hint_x=None, width=dp(84),
                             bg_color=T.ACCENT_SOFT, text_color=T.ACCENT)
        edit.bind(on_release=lambda *_: on_edit(task))
        delete = RoundedButton(text='Delete', font_size='14sp', size_hint_x=None, width=dp(84),
                               bg_color=T.DANGER_SOFT, text_color=T.DANGER)
        delete.bind(on_release=lambda *_: on_delete(task))
        actions.add_widget(edit)
        actions.add_widget(delete)
        self.add_widget(actions)


# ---------------------------------------------------------------- dialogs
def _dim_modal_args():
    return dict(background='', background_color=(0, 0, 0, 0), overlay_color=(0, 0, 0, 0.5))


class ConfirmDialog(ModalView):
    """Small confirmation / message dialog."""

    def __init__(self, title, message, on_confirm=None, confirm_text='OK',
                 danger=False, show_cancel=True, **kwargs):
        super().__init__(size_hint=(0.86, None), height=dp(200), **_dim_modal_args(), **kwargs)
        card = Card(orientation='vertical', bg_color=T.WHITE, radius_dp=dp(24),
                    padding=dp(20), spacing=dp(14), size_hint_y=None)
        auto_height(card)
        card.add_widget(wrap_label(title, font_size='20sp', bold=True))
        card.add_widget(wrap_label(message, font_size='16sp', color=T.MUTED))

        buttons = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(10))
        if show_cancel:
            cancel = RoundedButton(text='Cancel', bg_color=T.CARD, text_color=T.MUTED)
            cancel.bind(on_release=lambda *_: self.dismiss())
            buttons.add_widget(cancel)
        ok = RoundedButton(text=confirm_text,
                           bg_color=T.DANGER if danger else T.ACCENT)

        def confirmed(*_):
            self.dismiss()
            if on_confirm:
                on_confirm()
        ok.bind(on_release=confirmed)
        buttons.add_widget(ok)
        card.add_widget(buttons)

        self.add_widget(card)
        card.bind(height=lambda _w, h: setattr(self, 'height', h))
        self.height = card.height


class TaskForm(ModalView):
    """Popup used for both adding and editing a task."""

    def __init__(self, on_save, task=None, **kwargs):
        super().__init__(size_hint=(0.94, None), auto_dismiss=False,
                         **_dim_modal_args(), **kwargs)
        self.height = min(dp(640), Window.height * 0.92)
        self.on_save = on_save
        task = task or {}
        self.priority = task.get('priority', 'Medium')

        card = Card(orientation='vertical', bg_color=T.WHITE, radius_dp=dp(24),
                    padding=dp(18), spacing=dp(10))
        card.add_widget(wrap_label('Edit task' if task else 'New task',
                                   font_size='24sp', bold=True))

        scroll = ScrollView(do_scroll_x=False, bar_width=dp(3))
        form = auto_height(BoxLayout(orientation='vertical', spacing=dp(8),
                                     padding=[0, 0, 0, dp(8)]))

        def caption(text):
            return wrap_label(text, font_size='14sp', bold=True, color=T.MUTED)

        form.add_widget(caption('Title *'))
        self.title_in = RoundedInput(hint='What needs to be done?', text=task.get('title', ''))
        form.add_widget(self.title_in)

        form.add_widget(caption('Description'))
        self.desc_in = RoundedInput(hint='Add some details (optional)', multiline=True,
                                    height_dp=100, text=task.get('description', ''))
        form.add_widget(self.desc_in)

        form.add_widget(caption('Due date (YYYY-MM-DD)'))
        self.due_in = RoundedInput(hint='e.g. 2026-12-31', text=task.get('due_date', ''))
        form.add_widget(self.due_in)

        quick = BoxLayout(size_hint_y=None, height=dp(38), spacing=dp(6))
        for label, offset in (('Today', 0), ('Tomorrow', 1), ('+1 Week', 7), ('Clear', None)):
            button = RoundedButton(text=label, font_size='13sp', radius_dp=dp(12),
                                   bg_color=T.ACCENT_SOFT, text_color=T.ACCENT)
            button.bind(on_release=lambda _b, o=offset: self._set_due(o))
            quick.add_widget(button)
        form.add_widget(quick)

        form.add_widget(caption('Priority'))
        row = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(8))
        self.priority_buttons = {}
        for name in PRIORITIES:
            button = RoundedButton(text=name, font_size='15sp')
            button.bind(on_release=lambda _b, n=name: self._select_priority(n))
            self.priority_buttons[name] = button
            row.add_widget(button)
        form.add_widget(row)
        self._select_priority(self.priority)

        self.error = wrap_label('', font_size='14sp', color=T.DANGER)
        form.add_widget(self.error)
        scroll.add_widget(form)
        card.add_widget(scroll)

        buttons = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        cancel = RoundedButton(text='Cancel', bg_color=T.CARD, text_color=T.MUTED)
        cancel.bind(on_release=lambda *_: self.dismiss())
        save = RoundedButton(text='Save')
        save.bind(on_release=lambda *_: self._save())
        buttons.add_widget(cancel)
        buttons.add_widget(save)
        card.add_widget(buttons)
        self.add_widget(card)

        if not task:   # new task: open the keyboard right away
            Clock.schedule_once(lambda _dt: setattr(self.title_in.input, 'focus', True), 0.3)

    def _set_due(self, offset):
        self.due_in.text = '' if offset is None else (
            date.today() + timedelta(days=offset)).isoformat()

    def _select_priority(self, name):
        self.priority = name
        for key, button in self.priority_buttons.items():
            selected = (key == name)
            button.bg_color = T.PRIORITY_COLORS[key] if selected else T.CARD
            button.text_color = T.WHITE if selected else T.MUTED

    def _show_error(self, message):
        self.error.text = message

    def _save(self):
        title = self.title_in.text.strip()
        if not title:
            self._show_error('Please enter a title.')
            return
        due = self.due_in.text.strip()
        if due:
            try:
                due = datetime.strptime(due, '%Y-%m-%d').date().isoformat()
            except ValueError:
                self._show_error('Due date must look like 2026-12-31.')
                return
        data = {'title': title, 'description': self.desc_in.text.strip(),
                'due_date': due, 'priority': self.priority}
        self.dismiss()
        self.on_save(data)
