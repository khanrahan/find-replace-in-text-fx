"""
Find and Replace in Text TimelineFX

URL:
    https://github.com/khanrahan/find-replace-in-text-fx

Description:

    This script will find a specified search string within a Text Timeline FX and
    replace that search term with something else without having to enter the Text
    editor.

    Works on segments or sequences containing Text Timeline FX.  For sequences, it will
    find all segments that have Text Timeline FX and perform the find & replace.

Menus:

    Right-click selected segments in a sequence -> Edit... -> Find and Replace in Text
        Timeline FX

    Right-click selected sequence or sequences -> Edit... -> Find and Replace in Text
        Timeline FX

To Install:

    For all users, copy this file to:
    /opt/Autodesk/shared/python

    For a specific user, copy this file to:
    /opt/Autodesk/user/<user name>/python
"""


from __future__ import print_function
from PySide2 import QtWidgets, QtCore


TEMP_SETUP = "/var/tmp/temp"
VERSION = (0, 0, 1)


class FlameButton(QtWidgets.QPushButton):
    """
    Custom Qt Flame Button Widget
    To use:
    button = FlameButton('Button Name', do_when_pressed, window)
    """

    def __init__(self, button_name, do_when_pressed, parent_window, *args, **kwargs):
        super(FlameButton, self).__init__(*args, **kwargs)

        self.setText(button_name)
        self.setParent(parent_window)
        self.setMinimumSize(QtCore.QSize(110, 28))
        self.setMaximumSize(QtCore.QSize(110, 28))
        self.setFocusPolicy(QtCore.Qt.NoFocus)
        self.clicked.connect(do_when_pressed)
        self.setStyleSheet("""QPushButton {color: #9a9a9a;
                                           background-color: #424142;
                                           border-top: 1px inset #555555;
                                           border-bottom: 1px inset black;
                                           font: 14px 'Discreet'}
                           QPushButton:pressed {color: #d9d9d9;
                                                background-color: #4f4f4f;
                                                border-top: 1px inset #666666;
                                                font: italic}
                           QPushButton:disabled {color: #747474;
                                                 background-color: #353535;
                                                 border-top: 1px solid #444444;
                                                 border-bottom: 1px solid #242424}
                           QToolTip {color: black;
                                     background-color: #ffffde;
                                     border: black solid 1px}""")


class FlameLabel(QtWidgets.QLabel):
    """
    Custom Qt Flame Label Widget
    For different label looks set label_type as: 'normal', 'background', or 'outline'
    To use:
    label = FlameLabel('Label Name', 'normal', window)
    """

    def __init__(self, label_name, label_type, parent_window, *args, **kwargs):
        super(FlameLabel, self).__init__(*args, **kwargs)

        self.setText(label_name)
        self.setParent(parent_window)
        self.setMinimumSize(110, 28)
        self.setMaximumHeight(28)
        self.setFocusPolicy(QtCore.Qt.NoFocus)

        # Set label stylesheet based on label_type

        if label_type == 'normal':
            self.setStyleSheet("""QLabel {color: #9a9a9a;
                                          border-bottom: 1px inset #282828;
                                          font: 14px 'Discreet'}
                                  QLabel:disabled {color: #6a6a6a}""")
        elif label_type == 'background':
            self.setAlignment(QtCore.Qt.AlignCenter)
            self.setStyleSheet("""QLabel {color: #9a9a9a;
                                          background-color: #393939;
                                          font: 14px 'Discreet'}
                                  QLabel:disabled {color: #6a6a6a}""")
        elif label_type == 'outline':
            self.setAlignment(QtCore.Qt.AlignCenter)
            self.setStyleSheet("""QLabel {color: #9a9a9a;
                                          background-color: #212121;
                                          border: 1px solid #404040;
                                          font: 14px 'Discreet'}
                                  QLabel:disabled {color: #6a6a6a}""")


class FlameLineEdit(QtWidgets.QLineEdit):
    """
    Custom Qt Flame Line Edit Widget
    Main window should include this: window.setFocusPolicy(QtCore.Qt.StrongFocus)
    To use:
    line_edit = FlameLineEdit('Some text here', window)
    """

    def __init__(self, text, parent_window, *args, **kwargs):
        super(FlameLineEdit, self).__init__(*args, **kwargs)

        self.setText(text)
        self.setParent(parent_window)
        self.setMinimumHeight(28)
        self.setMinimumWidth(110)
        # self.setFocusPolicy(QtCore.Qt.NoFocus)
        self.setStyleSheet("""QLineEdit {color: #9a9a9a;
                                         background-color: #373e47;
                                         selection-color: #262626;
                                         selection-background-color: #b8b1a7;
                                         font: 14px 'Discreet'}
                              QLineEdit:focus {background-color: #474e58}
                              QLineEdit:disabled {color: #6a6a6a;
                                                  background-color: #373737}
                              QToolTip {color: black;
                                        background-color: #ffffde;
                                        border: black solid 1px}""")


class FindReplaceInTextFX(object):
    """Find and replace some text within a Text timelineFX."""


    def __init__(self, selection, **kwargs):

        self.selection = selection
        self.target = kwargs["target"]

        self.main_window()


    @staticmethod
    def save_text_timelineFX(segment, setup_path):
        """Save out a TTG node setup."""

        for timelineFX in segment.effects:
            if timelineFX.type == "Text":
                timelineFX.save_setup(setup_path)


    @staticmethod
    def load_text_timelineFX(segment, setup_path):
        """Load a TTG node setup to segment."""

        for timelineFX in segment.effects:
            if timelineFX.type == "Text":
                timelineFX.load_setup(setup_path)


    @staticmethod
    def add_timelineFX(segment, effect_type):
        """Add Timeline FX of effect_type to segment."""

        segment.create_effect(effect_type)


    @staticmethod
    def remove_timelineFX(segment, effect_type):
        """Remove Timeline FX of specified type from segment.  You have to remove before
        you can load a setup.  The setup load will not overwrite."""

        import flame

        for timelineFX in segment.effects:
            if timelineFX.type == effect_type:
                flame.delete(timelineFX)


    @staticmethod
    def convert_to_ttg_text(string):
        """Returns TTG style string"""

        return " ".join(str(ord(character)) for character in list(string))


    @staticmethod
    def filter_segments(selection):
        """Needed to filter the selection results of a segment.  flame api
        returns the segment or segments that are selected AND the timelineFX
        on those segments."""

        import flame

        filtered = []

        for item in selection:
            if isinstance(item, flame.PySegment):
                filtered.append(item)

        return filtered


    def find_and_write(self, ttg_node_file, find, replace):
        """Takes a path to a ttg setup and searches for a string and replaces
        it."""

        ttg_node_file += ".ttg_node" #append extension

        try:
            with open(ttg_node_file, newline='') as ttg:  #python3
                file_data = ttg.read()
        except TypeError:
            with open(ttg_node_file, 'rU') as ttg:  #python2.7
                file_data = ttg.read()

        #with open(ttg_node_file, 'rU') as file:
        #    file_data = file.read()

        new = file_data.replace(self.convert_to_ttg_text(find),
                                self.convert_to_ttg_text(replace))

        with open(ttg_node_file, "w") as ttg:
            ttg.write(new)


    def process_segments(self, find, replace):
        """Bulk process every selected segment."""


        segments = self.filter_segments(self.selection)

        for segment in segments:

            self.save_text_timelineFX(segment, TEMP_SETUP)
            self.remove_timelineFX(segment, "Text")
            self.add_timelineFX(segment, "Text")
            self.find_and_write(TEMP_SETUP, find, replace)
            self.load_text_timelineFX(segment, TEMP_SETUP)


    def process_sequences(self, find, replace):
        """Bulk process every segment found in the selected sequences."""


        for timeline in self.selection:
            for version in timeline.versions:
                for track in version.tracks:
                    for segment in track.segments:
                        for effect in segment.effects:
                            if effect.type == "Text":
                                self.save_text_timelineFX(segment, TEMP_SETUP)
                                self.remove_timelineFX(segment, "Text")
                                self.add_timelineFX(segment, "Text")
                                self.find_and_write(TEMP_SETUP,
                                                    find,
                                                    replace)
                                self.load_text_timelineFX(segment, TEMP_SETUP)


    def main_window(self):
        """The only popup window."""

        def okay_button():
            """Execute these when OK is pressed."""

            if self.target == "segments":
                self.process_segments(self.find.text(),
                                      self.replace.text())

            if self.target == "sequences":
                self.process_sequences(self.find.text(),
                                       self.replace.text())

            self.window.close()


        self.window = QtWidgets.QWidget()
        self.window.setMinimumSize(600, 130)
        self.window.setStyleSheet('background-color: #272727')
        self.window.setWindowTitle("Find and Replace in Text TimelineFX v{}".format(
                                   ".".join(str(num) for num in VERSION)))

        # FlameLineEdit class needs this
        self.window.setFocusPolicy(QtCore.Qt.StrongFocus)

        # Center Window
        resolution = QtWidgets.QDesktopWidget().screenGeometry()

        self.window.move((resolution.width() / 2) - (self.window.frameSize().width() / 2),
                         (resolution.height() / 2) - (self.window.frameSize().height() / 2))

        # Labels
        self.find_label = FlameLabel('Find', 'normal', self.window)
        self.replace_label = FlameLabel('Replace', 'normal', self.window)

        # Line Edits
        self.find = FlameLineEdit("", self.window)
        self.replace = FlameLineEdit("", self.window)

        # Buttons
        self.ok_btn = FlameButton('Ok', okay_button, self.window)
        self.ok_btn.setStyleSheet('background: #732020')

        self.cancel_btn = FlameButton("Cancel", self.window.close, self.window)

        # Tab Order
        #self.window.setTabOrder(self.find, self.replace)
        #self.window.setTabOrder(self.replace, self.ok_btn)
        #self.window.setTabOrder(self.ok_btn, self.cancel_btn)

        # Layout
        self.grid = QtWidgets.QGridLayout()
        self.grid.setVerticalSpacing(10)
        self.grid.setHorizontalSpacing(10)

        self.grid.addWidget(self.find_label, 0, 0)
        self.grid.addWidget(self.find, 0, 1)
        self.grid.addWidget(self.replace_label, 1, 0)
        self.grid.addWidget(self.replace, 1, 1)

        self.hbox03 = QtWidgets.QHBoxLayout()
        self.hbox03.addStretch(1)
        self.hbox03.addWidget(self.cancel_btn)
        self.hbox03.addWidget(self.ok_btn)

        self.vbox = QtWidgets.QVBoxLayout()
        self.vbox.setMargin(20)
        self.vbox.addLayout(self.grid)
        self.vbox.insertSpacing(2, 20)
        self.vbox.addLayout(self.hbox03)

        self.window.setLayout(self.vbox)
        self.window.show()

        return self.window


def find_replace_segments(selection):
    """Call the class with a target destination."""

    FindReplaceInTextFX(selection, target="segments")


def find_replace_sequences(selection):
    """Call the class with a target destination."""

    FindReplaceInTextFX(selection, target="sequences")


def scope_timeline(selection):
    """Return True if selection is a sequence."""

    import flame

    for item in selection:
        if isinstance(item, flame.PySequence):
            return True
    return False


def scope_timeline_segment(selection):
    """Return True if selection is a timeline segment."""

    import flame

    for item in selection:
        if isinstance(item, flame.PySegment):
            return True
    return False


def get_media_panel_custom_ui_actions():

    return [{'name': "Edit...",
             'actions': [{'name': "Find and Replace in Text TimelineFX",
                          'isVisible': scope_timeline,
                          'execute': find_replace_sequences,
                          'minimumVersion': "2020.3.1"}]
            }]


def get_timeline_custom_ui_actions():

    return [{'name': "Edit...",
             'actions': [{'name': "Find and Replace in Text TimelineFX",
                          'isVisible': scope_timeline_segment,
                          'execute': find_replace_segments,
                          'minimumVersion': "2020.3.1"}]
            }]
