from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QGroupBox, QTableWidget, 
                             QTableWidgetItem, QHeaderView)

class ResultsViewerWidget(QWidget):
    """展示不同模式下的计算结果。"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        group_box = QGroupBox("计算结果")
        layout.addWidget(group_box)

        group_layout = QVBoxLayout(group_box)
        self.table = QTableWidget()
        group_layout.addWidget(self.table)
    
    def clear_results(self):
        """清空表格内容和头部"""
        self.table.clear()
        self.table.setRowCount(0)
        self.table.setColumnCount(0)

    def display_results(self, results, mode):
        """
        根据不同的模式，在表格中显示结果。
        """
        self.clear_results()
        if not results:
            self.table.setColumnCount(1)
            self.table.setHorizontalHeaderLabels(["状态"])
            self.table.insertRow(0)
            self.table.setItem(0, 0, QTableWidgetItem("未找到匹配的解。"))
            self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            return

        if mode == 'unknown_element':
            self.table.setColumnCount(3)
            self.table.setHorizontalHeaderLabels(["最终化学式", "推断元素 (?)", "计算质量 (g/mol)"])
            for i, solution in enumerate(results):
                formula, calc_mass, matched_elem = solution
                final_formula_str = self._format_final_formula(formula, matched_elem)
                
                self.table.insertRow(i)
                self.table.setItem(i, 0, QTableWidgetItem(final_formula_str))
                self.table.setItem(i, 1, QTableWidgetItem(matched_elem))
                self.table.setItem(i, 2, QTableWidgetItem(f"{calc_mass:.3f}"))

        elif mode == 'general':
            self.table.setColumnCount(1)
            self.table.setHorizontalHeaderLabels(["可能的化学式"])
            for i, formula in enumerate(results):
                 formula_str = " ".join(f"{s}{c if c > 1 else ''}" for s, c in sorted(formula.items()))
                 self.table.insertRow(i)
                 self.table.setItem(i, 0, QTableWidgetItem(formula_str))
        
        self.table.resizeColumnsToContents()
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def _format_final_formula(self, formula, matched_elem):
        """辅助函数，用于构建最终的化学式字符串"""
        final_formula = formula.copy()
        if '?' in final_formula:
            n_unknown = final_formula.pop('?')
            final_formula[matched_elem] = final_formula.get(matched_elem, 0) + n_unknown
        return " ".join(f"{s}{c if c > 1 else ''}" for s, c in sorted(final_formula.items()))

    def show_error(self, message):
        """在表格中显示错误信息"""
        self.clear_results()
        self.table.setColumnCount(1)
        self.table.setHorizontalHeaderLabels(["错误"])
        self.table.insertRow(0)
        self.table.setItem(0, 0, QTableWidgetItem(message))
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)