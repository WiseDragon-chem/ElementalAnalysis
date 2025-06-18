from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLineEdit,
                             QDialogButtonBox, QLabel)

class AddComponentDialog(QDialog):
    """一个对话框，包含用于输入符号和化学式的字段"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("添加化学组分")
        
        self.symbol_input = QLineEdit()
        self.formula_input = QLineEdit()
        
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        form_layout.addRow(QLabel("组分符号 (例如: OAc, C, ?):"), self.symbol_input)
        form_layout.addRow(QLabel("化学式 (仅原子团, 例如: CH3O2):"), self.formula_input)
        layout.addLayout(form_layout)
        
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
    def get_data(self) -> dict:
        """返回用户输入的数据。"""
        return {
            'symbol': self.symbol_input.text().strip(),
            'formula': self.formula_input.text().strip()
        }

    @staticmethod
    def get_new_component(parent=None) -> dict | None:
        """
        静态方法：创建、显示对话框，并返回结果。
        这是从主窗口调用此对话框的推荐方式。
        """
        dialog = AddComponentDialog(parent)
        result = dialog.exec_() # exec_()会阻塞，直到对话框关闭
        if result == QDialog.Accepted:
            data = dialog.get_data()
            if data['symbol']: # 至少需要一个符号
                return data
        return None