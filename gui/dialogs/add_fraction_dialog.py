from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLineEdit,
                             QDialogButtonBox, QLabel)


from core.utils import check_fraction

class AddFractionDialog(QDialog):
    """
    一个模态对话框，包含即时输入验证和错误信息显示。
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("添加质量分数")
        self.setMinimumWidth(350)
        
        self.valid_data = None

        # --- UI元素 ---
        self.symbol_input = QLineEdit()
        self.fraction_input = QLineEdit()

        # --- 错误信息标签 ---
        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: red;")
        self.error_label.setWordWrap(True)

        # --- 布局 ---
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        form_layout.addRow("元素/符号 (例如: C, H, ?):", self.symbol_input)
        form_layout.addRow("质量分数 (%):", self.fraction_input)
        layout.addLayout(form_layout)
        layout.addWidget(self.error_label)
        
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self._validate_and_accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.symbol_input.textChanged.connect(self.error_label.clear)
        self.fraction_input.textChanged.connect(self.error_label.clear)

    def _validate_and_accept(self):
        """
        验证输入。如果有效，则接受对话框；否则，显示错误信息。
        """
        self.error_label.clear()
        
        try:
            symbol = self.symbol_input.text().strip()
            fraction_str = self.fraction_input.text().strip()
            
            # 调用核心验证函数
            valid_symbol, valid_fraction = check_fraction(symbol, fraction_str)
            
            self.valid_data = (valid_symbol, valid_fraction)
            self.accept()
            
        except ValueError as e:
            self.error_label.setText(str(e))
            
    def get_data(self) -> tuple | None:
        """返回已验证的数据。"""
        return self.valid_data

    @staticmethod
    def get_new_fraction(parent=None) -> tuple | None:
        """静态方法：创建、显示对话框，并返回结果。"""
        dialog = AddFractionDialog(parent)
        if dialog.exec_() == QDialog.Accepted:
            return dialog.get_data()
        return None