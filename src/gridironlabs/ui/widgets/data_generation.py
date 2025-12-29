"""Data generation and ingestion panels for settings."""

from __future__ import annotations

from PySide6.QtWidgets import QLabel, QVBoxLayout, QPushButton
from gridironlabs.ui.panels import PanelChrome


class DataGenerationPanel(PanelChrome):
    """Panel for configuring and triggering synthetic data generation."""

    def __init__(self) -> None:
        super().__init__(title="Data Generation")

        # Descriptive text
        self.description = QLabel(
            "Configure and trigger the synthetic NFL data generation pipeline. "
            "This will populate the local Parquet storage with fresh rosters, "
            "ratings, and schedules."
        )
        self.description.setStyleSheet("color: #9ca3af; font-size: 14px;")
        self.description.setWordWrap(True)
        self.body_layout.addWidget(self.description)

        # Placeholder for configuration options
        self.config_placeholder = QLabel("Generation parameters (Years, Roster Size, etc) will go here.")
        self.config_placeholder.setStyleSheet("color: #6b7280; font-style: italic; margin-top: 10px;")
        self.body_layout.addWidget(self.config_placeholder)

        self.body_layout.addStretch(1)

        # Action Button
        self.generate_btn = QPushButton("Generate New Dataset")
        self.generate_btn.setObjectName("PrimaryActionButton") # Assuming a style for this
        self.generate_btn.setMinimumHeight(40)
        self.body_layout.addWidget(self.generate_btn)

