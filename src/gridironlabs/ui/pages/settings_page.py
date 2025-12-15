"""Settings page built with the Page → GridCanvas → PanelCard framework."""



from __future__ import annotations



from datetime import datetime



from PySide6.QtCore import Qt

from PySide6.QtGui import QColor, QTextCursor, QTextOption

from PySide6.QtWidgets import (

    QFormLayout,

    QFrame,

    QHBoxLayout,

    QLabel,

    QLineEdit,

    QPushButton,

    QTextEdit,

    QVBoxLayout,

    QWidget,

)



from gridironlabs.core.config import AppConfig, AppPaths

from gridironlabs.ui.overlays.grid_overlay import GridOverlayConfig

from gridironlabs.ui.pages.base_page import BasePage

from gridironlabs.ui.style.tokens import GRID

from gridironlabs.ui.widgets.base_components import (

    AppCheckbox,

    AppComboBox,

    AppLineEdit,

    AppSlider,

    AppSpinBox,

    AppSwitch,

)

from gridironlabs.ui.widgets.panel_card import PanelCard





class SettingsPage(BasePage):

    """Settings page example composed of panel cards placed on a grid."""



    def __init__(

        self,

        *,

        config: AppConfig,

        paths: AppPaths,

        overlay_config: GridOverlayConfig | None = None,

    ) -> None:

        self.config = config

        self.paths = paths

        self.overlay_config = overlay_config or GridOverlayConfig()



        super().__init__(cols=GRID.cols, rows=12, overlay_config=self.overlay_config)

        self.setObjectName("page-settings")



        # 24-col grid: 10/7/7 (4/3/3) width split.

        self.grid.set_grid_config(cols=GRID.cols, rows=12, gap=12)



        self.debug_panel = DebugOutputPanel()

        self.data_panel = DataGenerationPanel()

        self.grid_panel = UIGridLayoutPanel(overlay_config=self.overlay_config)

        self.tests_panel = TestCasesPanel(debug_output=self.debug_panel)



        self.add_panel(self.data_panel, col=0, row=0, col_span=10, row_span=12)

        self.add_panel(self.grid_panel, col=10, row=0, col_span=7, row_span=5)

        self.add_panel(self.tests_panel, col=10, row=5, col_span=7, row_span=7)

        self.add_panel(self.debug_panel, col=17, row=0, col_span=7, row_span=12)





class DataGenerationPanel(PanelCard):

    """Settings panel for data generation toggles and basic controls."""



    def __init__(self) -> None:

        super().__init__("Data Generation")



        content = QHBoxLayout()

        content.setContentsMargins(0, 0, 0, 0)

        content.setSpacing(12)



        left = QVBoxLayout()

        left.setContentsMargins(0, 0, 0, 0)

        left.setSpacing(10)

        left.addLayout(_season_range_row())

        left.addLayout(_switch_row("Real Data", checked=True))

        left.addLayout(_switch_row("Pull NFLverse", checked=True))

        left.addLayout(_switch_row("Pull Pro-Football-Reference", checked=True))



        left.addWidget(_checkbox_group("Generate Data", ["Generate Teams", "Generate Coaches", "Generate Players"]))

        left.addWidget(_checkbox_group("Player Types", ["Offense", "Defense", "Special Teams"]))

        left.addStretch(1)



        right = QVBoxLayout()

        right.setContentsMargins(0, 0, 0, 0)

        right.setSpacing(10)

        right.addWidget(_last_update_table())

        right.addLayout(_total_row("Total Data Size", "35GB"))



        generate_button = QPushButton("Generate Data")

        generate_button.setObjectName("PrimaryButton")

        generate_button.setMinimumHeight(40)

        right.addWidget(generate_button)



        content.addLayout(left, 1)

        content.addLayout(right, 1)

        self.body_layout.addLayout(content)





class UIGridLayoutPanel(PanelCard):

    """Panel that controls the debug grid overlay."""



    def __init__(self, *, overlay_config: GridOverlayConfig) -> None:

        super().__init__("UI Grid Layout")

        self._overlay_config = overlay_config



        self._enable_switch = AppSwitch(checked=self._overlay_config.enabled)

        self._opacity_slider = AppSlider(Qt.Horizontal)

        self._opacity_slider.setRange(0, 100)

        self._opacity_slider.setValue(int(self._overlay_config.opacity * 100))

        self._opacity_value = QLabel(f"{self._opacity_slider.value()}%")

        self._opacity_value.setObjectName("SettingsLabel")



        self._color_swatch = QFrame()

        self._color_swatch.setObjectName("ColorSwatch")

        self._color_swatch.setFixedSize(42, 26)



        self._color_input = AppLineEdit(self._overlay_config.color_hex.upper())

        self._color_input.setMaxLength(7)

        self._color_input.setFixedWidth(110)



        self._cell_spin = AppSpinBox()

        self._cell_spin.setRange(6, 100)

        self._cell_spin.setValue(int(self._overlay_config.cell_size))

        self._cell_spin.setSuffix(" px")

        self._cell_spin.setFixedWidth(90)



        self._refresh_color_swatch()



        self.body_layout.addLayout(_labeled_widget_row("Enable Grid", self._enable_switch))

        self.body_layout.addLayout(self._opacity_row())

        self.body_layout.addLayout(self._color_row())

        self.body_layout.addLayout(_labeled_widget_row("Cell Size", self._cell_spin))

        self.body_layout.addStretch(1)



        self._wire_events()

        self._overlay_config.changed.connect(self._sync_from_config)



    def _opacity_row(self) -> QHBoxLayout:

        row = QHBoxLayout()

        row.setSpacing(10)

        row.addWidget(_settings_label("Opacity"))

        row.addWidget(self._opacity_slider, 1)

        row.addWidget(self._opacity_value)

        return row



    def _color_row(self) -> QHBoxLayout:

        row = QHBoxLayout()

        row.setSpacing(10)

        row.addWidget(_settings_label("Color"))

        row.addWidget(self._color_swatch, 0, Qt.AlignLeft)

        row.addWidget(self._color_input)

        row.addStretch(1)

        return row



    def _wire_events(self) -> None:

        self._enable_switch.toggled.connect(self._overlay_config.set_enabled)



        def on_opacity(value: int) -> None:

            self._opacity_value.setText(f"{value}%")

            self._overlay_config.set_opacity(value / 100.0)



        self._opacity_slider.valueChanged.connect(on_opacity)



        self._cell_spin.valueChanged.connect(lambda value: self._overlay_config.set_cell_size(int(value)))



        self._color_input.returnPressed.connect(lambda: self._apply_hex_color())

        self._color_input.editingFinished.connect(lambda: self._apply_hex_color())



    def _apply_hex_color(self) -> None:

        value = _normalize_hex(self._color_input.text())

        self._overlay_config.set_color_hex(value)



    def _sync_from_config(self) -> None:
        widgets = (self._enable_switch, self._opacity_slider, self._cell_spin, self._color_input)
        for widget in widgets:
            widget.blockSignals(True)
        try:
            self._enable_switch.setChecked(self._overlay_config.enabled)
            self._opacity_slider.setValue(int(self._overlay_config.opacity * 100))
            self._cell_spin.setValue(int(self._overlay_config.cell_size))
            self._color_input.setText(self._overlay_config.color_hex.upper())
            self._refresh_color_swatch()
        finally:
            for widget in widgets:
                widget.blockSignals(False)



    def _refresh_color_swatch(self) -> None:

        value = _normalize_hex(self._overlay_config.color_hex)

        self._color_swatch.setStyleSheet(f"background-color: {value};")





class TestCasesPanel(PanelCard):

    """Panel with simple test toggles that write to the debug output."""



    def __init__(self, *, debug_output: "DebugOutputPanel") -> None:

        super().__init__("Test Cases")

        self._debug_output = debug_output



        self._test1 = AppSwitch(checked=True)

        self._test2 = AppSwitch(checked=True)

        self._test3 = AppSwitch(checked=True)



        self.body_layout.addLayout(_labeled_widget_row("Test 1", self._test1))

        self.body_layout.addLayout(_labeled_widget_row("Test 2", self._test2))

        self.body_layout.addLayout(_labeled_widget_row("Test 3", self._test3))



        button_row = QHBoxLayout()

        button_row.addStretch(1)

        execute = QPushButton("Execute Tests")

        execute.setObjectName("GhostButton")

        execute.setMinimumHeight(36)

        execute.clicked.connect(self._run)

        button_row.addWidget(execute, 0, Qt.AlignRight)

        self.body_layout.addStretch(1)

        self.body_layout.addLayout(button_row)



    def _run(self) -> None:

        self._debug_output.append_log('> Executing "Test 1"...')

        if self._test1.isChecked():

            self._debug_output.append_log('> "Test 1" passed!')

        self._debug_output.append_log('> Executing "Test 2"...')

        if self._test2.isChecked():

            self._debug_output.append_log('> "Test 2" failed...')

        self._debug_output.append_log('> Executing "Test 3"...')

        if self._test3.isChecked():

            self._debug_output.append_log('> "Test 3" running...')





class DebugOutputPanel(PanelCard):

    """Monospace debug output panel."""



    def __init__(self) -> None:

        super().__init__("Debug Output")



        self.output = QTextEdit()

        self.output.setObjectName("TerminalOutput")

        self.output.setReadOnly(True)

        self.output.setWordWrapMode(QTextOption.NoWrap)



        palette = self.output.palette()

        palette.setColor(self.output.viewport().backgroundRole(), Qt.black)

        palette.setColor(self.output.backgroundRole(), Qt.black)

        palette.setColor(self.output.foregroundRole(), QColor("#e5e7eb"))

        palette.setColor(self.output.viewport().foregroundRole(), QColor("#e5e7eb"))

        self.output.setPalette(palette)

        self.output.viewport().setAutoFillBackground(True)



        self.body_layout.addWidget(self.output)



    def append_log(self, line: str) -> None:

        cursor = self.output.textCursor()

        cursor.movePosition(QTextCursor.End)

        cursor.insertText(str(line) + "\n")

        self.output.setTextCursor(cursor)

        self.output.ensureCursorVisible()





def _settings_label(text: str) -> QLabel:

    label = QLabel(text)

    label.setObjectName("SettingsLabel")

    return label





def _labeled_widget_row(label_text: str, widget: QWidget) -> QHBoxLayout:

    row = QHBoxLayout()

    row.setSpacing(8)

    row.addWidget(_settings_label(label_text))

    row.addStretch(1)

    row.addWidget(widget)

    return row





def _season_range_row() -> QHBoxLayout:

    row = QHBoxLayout()

    row.setSpacing(8)

    row.addWidget(_settings_label("Season Range"))



    start = AppComboBox()

    end = AppComboBox()



    current_year = datetime.now().year

    for year in range(1999, current_year + 1):

        start.addItem(str(year))

        end.addItem(str(year))



    start.setCurrentText("1999")

    end.setCurrentText(str(current_year))

    start.setFixedWidth(96)

    end.setFixedWidth(96)



    row.addWidget(start)

    row.addWidget(end)

    row.addStretch(1)

    return row





def _switch_row(text: str, *, checked: bool = False) -> QHBoxLayout:

    row = QHBoxLayout()

    row.setSpacing(8)

    row.addWidget(_settings_label(text))

    row.addStretch(1)

    row.addWidget(AppSwitch(checked))

    return row





def _checkbox_group(title: str, items: list[str]) -> QFrame:

    container = QFrame()

    container.setObjectName("SettingsGroup")

    layout = QVBoxLayout(container)

    layout.setContentsMargins(0, 0, 0, 0)

    layout.setSpacing(6)



    header = QLabel(title)

    header.setObjectName("CardTitleSmall")

    layout.addWidget(header)



    for item in items:

        cb = AppCheckbox(item)

        cb.setChecked(True)

        layout.addWidget(cb)



    return container





def _last_update_table() -> QFrame:

    frame = QFrame()

    frame.setObjectName("SettingsLastUpdate")

    layout = QFormLayout(frame)

    layout.setContentsMargins(10, 10, 10, 10)

    layout.setSpacing(6)



    header_row = QHBoxLayout()

    header_row.setSpacing(8)

    data_label = QLabel("Data Type")

    data_label.setObjectName("SettingsTableHeader")

    last_label = QLabel("Last Update")

    last_label.setObjectName("SettingsTableHeader")

    header_row.addWidget(data_label, 1)

    header_row.addWidget(last_label, 1)

    layout.addRow(header_row)



    now_text = datetime.now().strftime("%b %d, %Y @ %I:%M%p").lower()

    for data_type in ("Teams", "Coaches", "Players", "Offense", "Defense", "Spec Teams"):

        row = QHBoxLayout()

        row.setSpacing(8)

        label = QLabel(data_type)

        label.setObjectName("SettingsTableCell")

        stamp = QLabel(now_text)

        stamp.setObjectName("SettingsTableCell")

        row.addWidget(label, 1)

        row.addWidget(stamp, 1)

        layout.addRow(row)



    return frame





def _total_row(label_text: str, value_text: str) -> QHBoxLayout:

    row = QHBoxLayout()

    row.setSpacing(8)

    label = QLabel(label_text)

    label.setObjectName("SettingsCaption")

    value = QLabel(value_text)

    value.setObjectName("SettingsLabel")

    row.addWidget(label)

    row.addStretch(1)

    row.addWidget(value, 0, Qt.AlignRight)

    return row





def _normalize_hex(text: str) -> str:

    value = str(text).strip().lstrip("#")

    if len(value) not in (3, 6) or any(ch not in "0123456789abcdefABCDEF" for ch in value):

        return "#2563eb"

    if len(value) == 3:

        value = "".join(ch * 2 for ch in value)

    return f"#{value.lower()}"

