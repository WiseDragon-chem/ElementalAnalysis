# gui/dialogs/add_component_dialog.py
"""
定义一个用于添加新化学组分的弹出对话框，并包含输入验证逻辑。
"""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLineEdit,
                             QDialogButtonBox, QLabel)
from PyQt5.QtCore import Qt

from core.utils import check_component

class AddComponentDialog(QDialog):
    """
    一个模态对话框，包含即时输入验证和错误信息显示。
    """
    def __init__(self, existing_symbols: list[str],parent=None):
        super().__init__(parent)
        self.setWindowTitle("添加化学组分")
        self.setMinimumWidth(350)

        self.existing_symbols = existing_symbols
        self.valid_data = None
        
        self.symbol_input = QLineEdit()
        self.formula_input = QLineEdit()
        
        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: red;")
        self.error_label.setWordWrap(True) # 允许错误信息换行

        layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        form_layout.addRow("组分符号 (例如: OAc, C, ?):", self.symbol_input)
        form_layout.addRow("化学式 (仅原子团, 例如: C2H3O2):", self.formula_input)
        layout.addLayout(form_layout)
        layout.addWidget(self.error_label) # 将错误标签添加到布局中
        
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)

        # 连接OK按钮的点击事件到我们自己的验证方法
        button_box.accepted.connect(self._validate_and_accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        # 当用户开始编辑时，清除错误信息
        self.symbol_input.textChanged.connect(self.error_label.clear)
        self.formula_input.textChanged.connect(self.error_label.clear)
        
        # 获取实际的OK按钮
        self.real_ok_button = button_box.button(QDialogButtonBox.Ok)
        
        # 连接文本变化信号
        self.symbol_input.textChanged.connect(self.error_label.clear)
        self.formula_input.textChanged.connect(self.error_label.clear)
        
        # 设置Enter键行为
        self._setup_enter_key_behavior()

    def _setup_enter_key_behavior(self):
        """配置Enter键的焦点转移和确认行为"""
        # 设置符号输入框的回车行为 - 跳转到分数输入框
        self.symbol_input.returnPressed.connect(
            lambda: self.formula_input.setFocus()
        )
        
        # 设置分数输入框的回车行为 - 执行确认操作
        self.formula_input.returnPressed.connect(
            self._trigger_accept
        )
        
        # 设置两个输入框都接受Enter键
        self.symbol_input.setFocusPolicy(Qt.StrongFocus)
        self.formula_input.setFocusPolicy(Qt.StrongFocus)

    def _trigger_accept(self):
        """触发确认操作（模拟点击OK按钮）"""
        if self.real_ok_button.isEnabled():
            self.real_ok_button.click()
        else:
            # 如果OK按钮不可用，保持焦点在当前输入框
            self.formula_input.setFocus()

    def _validate_and_accept(self):
        """
        验证输入。如果有效，则接受对话框；否则，显示错误信息。
        """
        # 清除旧的错误信息
        self.error_label.clear()
        
        try:
            symbol = self.symbol_input.text().strip()
            formula = self.formula_input.text().strip()
            
            # 调用核心验证函数
            # print(symbol,formula)
            valid_symbol, valid_formula = check_component(symbol, formula, self.existing_symbols )
            
            self.valid_data = {'symbol': valid_symbol, 'formula': valid_formula}
            self.accept()

        except ValueError as e:
            self.error_label.setText(str(e))
    
    def get_data(self) -> dict:
        """返回已验证的数据。"""
        return self.valid_data

    @staticmethod
    def get_new_component(existing_symbols: list[str], parent=None) -> dict | None:
        """静态方法：创建、显示对话框，并返回结果。"""
        dialog = AddComponentDialog(existing_symbols,parent)
        if dialog.exec_() == QDialog.Accepted:
            return dialog.get_data()
        return None