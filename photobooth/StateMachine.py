#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Photobooth - a flexible photo booth software
# Copyright (C) 2018  Balthasar Reuter <photobooth at re - web dot eu>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.


class Context:

    def __init__(self, initial_state):

        super().__init__()

        self.state = initial_state

    @property
    def state(self):

        return self._state

    @state.setter
    def state(self, new_state):

        if not isinstance(new_state, State):
            raise TypeError('new_state must implement State')

    def handleEvent(self, event):

        if not isinstance(event, Event):
            raise TypeError('event must implement Event')

        if isinstance(event, ErrorEvent):
            self.state = ErrorState(event.exception, self.state)
        elif isinstance(event, TeardownEvent):
            self.state = TeardownState(event.target)
        else:
            self.state.handleEvent(event, self)


class Event:

    def __init__(self, name):

        super().__init__()
        self.name = name

    def __str__(self):

        return self.name

    @property
    def name(self):

        return self._name

    @name.setter
    def name(self, name):

        if not isinstance(name, str):
            raise TypeError('name must be a str')

        self._name = name


class ErrorEvent(Event):

    def __init__(self, exception):

        super().__init__('Error')
        self.exception = exception

    def __str__(self):

        return str(self.exception)

    @property
    def exception(self):

        return self._exception

    @exception.setter
    def exception(self, exception):

        if not isinstance(exception, Exception):
            raise TypeError('exception must be derived from Exception')

        self._exception = exception


class TeardownEvent(Event):

    EXIT = 0
    RESTART = 1
    WELCOME = 2

    def __init__(self, target):

        self._target = target
        super().__init__('Teardown')

    @property
    def target(self):

        return self._target


class GuiEvent(Event):

    def __init__(self, name):

        super().__init__(name)


class GpioEvent(Event):

    def __init__(self, name):

        super().__init__(name)


class CameraEvent(Event):

    def __init__(self, name):

        super().__init__(name)


class WorkerEvent(Event):

    def __init__(self, name):

        super().__init__(name)


class State:

    def __init__(self):

        super().__init__()
        self.update()

    def update(self):

        pass

    def handleEvent(self, event, context):

        raise NotImplementedError()


class ErrorState(State):

    def __init__(self, exception, old_state):

        self.old_state = old_state
        super().__init__()

    @property
    def old_state(self):

        return self._old_state

    @old_state.setter
    def old_state(self, old_state):

        if not isinstance(old_state, State):
            raise TypeError('old_state must be derived from State')

        self._old_state = old_state

    def handleEvent(self, event, context):

        if isinstance(event, GuiEvent) and event.name == 'retry':
            context.state = self.old_state
            context.state.update()
        elif isinstance(event, GuiEvent) and event.name == 'abort':
            context.state = TeardownState()
        else:
            raise TypeError('Unknown Event type "{}"'.format(event))


class TeardownState(State):

    def __init__(self, target):

        super().__init__()


class WelcomeState(State):

    def __init__(self):

        super().__init__()

    def handleEvent(self, event, context):

        if isinstance(event, GuiEvent):
            if event.name == 'start':
                context.state = StartupState()
            elif event.name == 'settings':
                context.state = SettingsState()
            elif event.name == 'exit':
                context.state = TeardownState()
            else:
                raise ValueError('Unknown GuiEvent "{}"'.format(event.name))
        else:
            raise TypeError('Unknown Event type "{}"'.format(event))


class SettingsState(State):

    def __init__(self):

        super().__init__()

    def handleEvent(self, event, context):

        if isinstance(event, GuiEvent) and event.name == 'welcome':
            context.state = WelcomeState()
        else:
            raise TypeError('Unknown Event type "{}"'.format(event))


class StartupState(State):

    def __init__(self):

        super().__init__()

    def handleEvent(self, event, context):

        if isinstance(event, CameraEvent) and event.name == 'ready':
            context.state = IdleState()
        else:
            raise TypeError('Unknown Event type "{}"'.format(event))


class IdleState(State):

    def __init__(self):

        super().__init__()

    def handleEvent(self, event, context):

        if ((isinstance(event, GuiEvent) or isinstance(event, GpioEvent)) and
           event.name == 'trigger'):
            context.state = GreeterState()
        else:
            raise TypeError('Unknown Event type "{}"'.format(event))


class GreeterState(State):

    def __init__(self):

        super().__init__()

    def handleEvent(self, event, context):

        if ((isinstance(event, GuiEvent) or isinstance(event, GpioEvent)) and
           event.name == 'countdown'):
            context.state = CountdownState()
        else:
            raise TypeError('Unknown Event type "{}"'.format(event))


class CountdownState(State):

    def __init__(self):

        super().__init__()

    def handleEvent(self, event, context):

        if isinstance(event, GuiEvent) and event.name == 'capture':
            context.state == CaptureState()
        else:
            raise TypeError('Unknown Event type "{}"'.format(event))


class CaptureState(State):

    def __init__(self):

        super().__init__()

    def handleEvent(self, event, context):

        if isinstance(event, CameraEvent) and event.name == 'next':
            context.state = CountdownState()
        elif isinstance(event, CameraEvent) and event.name == 'assemble':
            context.state = AssembleState()
        else:
            raise TypeError('Unknown Event type "{}"'.format(event))


class AssembleState(State):

    def __init__(self):

        super().__init__()

    def handleEvent(self, event, context):

        if isinstance(event, CameraEvent) and event.name == 'review':
            context.state = ReviewState()
        else:
            raise TypeError('Unknown Event type "{}"'.format(event))


class ReviewState(State):

    def __init__(self):

        super().__init__()

    def handleEvent(self, event, context):

        if isinstance(event, GuiEvent) and event.name == 'postprocess':
            context.state == PostprocessState()
        else:
            raise TypeError('Unknown Event type "{}"'.format(event))


class PostprocessState(State):

    def __init__(self):

        super().__init__()

    def handleEvent(self, event, context):

        if ((isinstance(event, GuiEvent) or isinstance(event, GpioEvent)) and
           event.name == 'idle'):
            context.state == IdleState()
        else:
            raise TypeError('Unknown Event type "{}"'.format(event))
