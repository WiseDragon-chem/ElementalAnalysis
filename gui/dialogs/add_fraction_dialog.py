from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLineEdit,
                             QDialogButtonBox, QLabel)
from PyQt5.QtGui import QDoubleValidator

class AddFractionDialog(QDialog):
    """一个模态对话框，包含用于输入元素符号和质量分数的字段。"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("添加质量分数")
        
        self.symbol_input = QLineEdit()
        self.fraction_input = QLineEdit()
        # 只允许输入浮点数
        self.fraction_input.setValidator(QDoubleValidator(0.0, 100.0, 4, self))

        layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        form_layout.addRow(QLabel("元素/符号 (例如: C, H, ?):"), self.symbol_input)
        form_layout.addRow(QLabel("质量分数 (%):"), self.fraction_input)
        layout.addLayout(form_layout)
        
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def get_data(self) -> tuple | None:
        """返回用户输入的数据。"""
        symbol = self.symbol_input.text().strip()
        fraction_str = self.fraction_input.text().strip()
        
        if symbol and fraction_str:
            try:
                return symbol, float(fraction_str)
            except ValueError:
                return None
        return None

    @staticmethod
    def get_new_fraction(parent=None) -> tuple | None:
        """静态方法：创建、显示对话框，并返回结果。"""
        dialog = AddFractionDialog(parent)
        if dialog.exec_() == QDialog.Accepted:
            return dialog.get_data()
        return None