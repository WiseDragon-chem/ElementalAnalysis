from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLineEdit,
                             QDialogButtonBox, QLabel)


from core.utils import check_fraction
from PyQt5.QtCore import Qt
from data.data_manager import DataManager

class AddFractionDialog(QDialog):
    """
    一个模态对话框，包含即时输入验证和错误信息显示。
    """
    def __init__(self,data_manager : DataManager ,parent=None):
        super().__init__(parent)
        self.setWindowTitle("添加质量分数")
        self.setMinimumWidth(350)

        self.data_manager = data_manager
        # self.valid_data = None

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

        # 获取实际的OK按钮
        self.real_ok_button = button_box.button(QDialogButtonBox.Ok)
        
        # 连接文本变化信号
        self.symbol_input.textChanged.connect(self.error_label.clear)
        self.fraction_input.textChanged.connect(self.error_label.clear)
        
        # 设置Enter键行为
        self._setup_enter_key_behavior()

    def _setup_enter_key_behavior(self):
        """配置Enter键的焦点转移和确认行为"""
        # 设置符号输入框的回车行为 - 跳转到分数输入框
        self.symbol_input.returnPressed.connect(
            lambda: self.fraction_input.setFocus()
        )
        
        # 设置分数输入框的回车行为 - 执行确认操作
        self.fraction_input.returnPressed.connect(
            self._trigger_accept
        )
        
        # 设置两个输入框都接受Enter键
        self.symbol_input.setFocusPolicy(Qt.StrongFocus)
        self.fraction_input.setFocusPolicy(Qt.StrongFocus)

    def _trigger_accept(self):
        """触发确认操作（模拟点击OK按钮）"""
        if self.real_ok_button.isEnabled():
            self.real_ok_button.click()
        else:
            # 如果OK按钮不可用，保持焦点在当前输入框
            self.fraction_input.setFocus()

    def _validate_and_accept(self):
        self.error_label.clear()
        try:
            symbol = self.symbol_input.text().strip()
            fracion = self.fraction_input.text().strip()
            
            # 直接调用DataManager的方法，所有验证逻辑都在那里
            self.data_manager.add_fraction(symbol, fracion)
            
            # 验证通过，接受对话框
            self.accept()
        except ValueError as e:
            self.error_label.setText(str(e))

    @staticmethod
    def show_dialog(data_manager : DataManager, parent=None) -> bool:
        """静态方法：创建、显示对话框，并返回是否成功添加。"""
        dialog = AddFractionDialog(data_manager, parent)
        return dialog.exec_() == QDialog.Accepted