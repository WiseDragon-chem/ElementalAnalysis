import sys,traceback,typing
sys.path.append('..')

from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QMessageBox, QTableWidget, QGroupBox,
                             QTableWidgetItem, QAbstractItemView, QHeaderView,
                             QFormLayout, QLineEdit, QRadioButton, QButtonGroup,
                             QFrame)
from PyQt5.QtGui import QIntValidator, QDoubleValidator
from PyQt5.QtCore import Qt # For Qt.AlignLeft etc.
from PyQt5.QtGui import QIcon # For icons
from PyQt5.QtWidgets import QStyle # For standard icons

from gui.dialogs.add_component_dialog import AddComponentDialog
from gui.dialogs.add_fraction_dialog import AddFractionDialog
from gui.widgets.results_viewer import ResultsViewerWidget

from core.calculator import ChemicalCalculator
import core.data_modules as data_modules

class MainWindow(QMainWindow):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.calculator = ChemicalCalculator() # 使用模拟计算器
        self.setWindowTitle("元素分析计算器 Beta Version")
        self.setGeometry(100, 100, 1500, 600)
        self._setup_ui()

        # 储存数据状态
        self.components_data = []  # 例如: [{'symbol': 'OAc', 'formula': 'C2H3O2'}]
        self.fractions_data = {}   # 例如: {'C': 40.123} 

    def _setup_ui(self):
        # --- 主布局和中心组件 ---
        main_layout = QHBoxLayout()
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        left_layout = self._create_left_column()
        
        center_layout = self._create_center_column()

        self.results_viewer = ResultsViewerWidget()

        main_layout.addLayout(left_layout, 3)      
        main_layout.addLayout(center_layout, 1)    
        main_layout.addWidget(self.results_viewer, 4) 

    def _create_left_column(self):
        """创建并返回左侧列的布局。"""
        layout = QVBoxLayout()
        
        # 组分表格
        comp_group = QGroupBox("1. 组分定义")
        comp_layout = QVBoxLayout(comp_group)
        self.components_table = QTableWidget(0, 3) # Changed to 3 columns
        self.components_table.setHorizontalHeaderLabels(["  ", "符号", "化学式"])
        self.components_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.components_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents) # 操作列宽度自适应
        self.components_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        comp_layout.addWidget(self.components_table)
        self.add_comp_button = QPushButton("添加组分...")
        comp_layout.addWidget(self.add_comp_button)
        layout.addWidget(comp_group)
        
        # 质量分数表格
        frac_group = QGroupBox("2. 质量分数")
        frac_layout = QVBoxLayout(frac_group)
        self.fractions_table = QTableWidget(0, 3) # Changed to 3 columns
        self.fractions_table.setHorizontalHeaderLabels(["  ", "符号", "分数 (%)"])
        self.fractions_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.fractions_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents) # 操作列宽度自适应
        self.fractions_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        frac_layout.addWidget(self.fractions_table)
        self.add_frac_button = QPushButton("添加质量分数...")
        frac_layout.addWidget(self.add_frac_button)
        layout.addWidget(frac_group)

        # 连接信号
        self.add_comp_button.clicked.connect(self._on_add_component)
        self.add_frac_button.clicked.connect(self._on_add_fraction)

        return layout

    def _create_center_column(self):
        """
        创建中间列。过滤器现在位于计算参数组框的下半部分。
        """
        center_vbox_layout = QVBoxLayout()
    
        config_group = QGroupBox("计算参数")
        config_group_layout = QVBoxLayout(config_group) # 主布局变为垂直

        # --- Part 1: 参数输入 ---
        param_form_layout = QFormLayout()
        self.n_max_input = QLineEdit("10")
        self.n_max_input.setValidator(QIntValidator(1, 100))
        self.mass_tol_input = QLineEdit("0.2")
        self.mass_tol_input.setValidator(QDoubleValidator(0.01, 5.0, 2))
        self.frac_tol_input = QLineEdit("0.5")
        self.frac_tol_input.setValidator(QDoubleValidator(0.01, 10.0, 2))
        param_form_layout.addRow("最大原子计数 (n_max):", self.n_max_input)
        param_form_layout.addRow("原子质量公差 (g/mol):", self.mass_tol_input)
        param_form_layout.addRow("质量分数公差 (%):", self.frac_tol_input)
        config_group_layout.addLayout(param_form_layout) # 将表单布局添加到组的主布局中

        # 过滤器 
        # 创建一个容器QWidget
        self.filter_container = QWidget()
        filter_vbox_layout = QVBoxLayout(self.filter_container)
        filter_vbox_layout.setContentsMargins(0, 10, 0, 0) # 添加一点上边距

        # 添加分割线
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        filter_vbox_layout.addWidget(line)

        # 过滤器选项
        filter_hbox_layout = QHBoxLayout()
        self.metal_radio = QRadioButton("金属")
        self.nonmetal_radio = QRadioButton("非金属")
        self.unlimited_radio = QRadioButton("不限")
        self.unlimited_radio.setChecked(True)
        
        self.unknown_type_button_group = QButtonGroup(self)
        self.unknown_type_button_group.addButton(self.metal_radio)
        self.unknown_type_button_group.addButton(self.nonmetal_radio)
        self.unknown_type_button_group.addButton(self.unlimited_radio)
        
        filter_hbox_layout.addWidget(self.metal_radio)
        filter_hbox_layout.addWidget(self.nonmetal_radio)
        filter_hbox_layout.addWidget(self.unlimited_radio)
        filter_vbox_layout.addLayout(filter_hbox_layout)

        # 将过滤器容器添加到组的主布局中
        config_group_layout.addWidget(self.filter_container)
        self.filter_container.hide() # 默认隐藏整个容器

        center_vbox_layout.addWidget(config_group)
        center_vbox_layout.addStretch()
        
        # 计算按钮 
        self.calculate_button = QPushButton("开始推断")
        self.calculate_button.setStyleSheet("font-size: 16px; padding: 10px; background-color: #4CAF50; color: white;")
        center_vbox_layout.addWidget(self.calculate_button)
        
        self.calculate_button.clicked.connect(self._run_calculation)
        
        return center_vbox_layout

    def _on_add_component(self):
        """处理添加组分按钮点击事件"""
        existing_symbols = [c['symbol'] for c in self.components_data]
        # 将当前上下文传递给对话框
        new_comp_data = AddComponentDialog.get_new_component(existing_symbols, self)
        
        if new_comp_data:
            # 1. 更新内部数据状态
            self.components_data.append(new_comp_data)
            # 2. 根据数据状态刷新UI
            self._refresh_components_table()
            # 调节fliter可见性
            self._update_ui_visibility() 

    def _on_add_fraction(self):
        """处理添加质量分数按钮点击事件"""
        defined_symbols = [c['symbol'] for c in self.components_data]
        if not defined_symbols:
            QMessageBox.warning(self, "提示", "请先至少定义一个化学组分。")
            return
            
        # 将当前上下文传递给对话框
        new_frac_data = AddFractionDialog.get_new_fraction(defined_symbols, self)
        
        if new_frac_data:
            symbol, fraction = new_frac_data
            # 1. 更新内部数据状态
            self.fractions_data[symbol] = fraction
            # 2. 根据数据状态刷新UI
            self._refresh_fractions_table()

    def _on_delete_component_row(self, symbol_to_delete):
        """处理删除组分表格行的请求"""
        # 从 self.components_data 移除
        self.components_data = [comp for comp in self.components_data if comp['symbol'] != symbol_to_delete]
        
        # 如果对应的符号也存在于质量分数数据中，一并移除
        if symbol_to_delete in self.fractions_data:
            del self.fractions_data[symbol_to_delete]
            self._refresh_fractions_table() # 如果fractions_data改变了，刷新它
            
        self._refresh_components_table()
        self._update_ui_visibility() # 如果 '?' 被删除，需要更新过滤器可见性

    def _on_delete_fraction_row(self, symbol_to_delete):
        """处理删除质量分数表格行的请求"""
        if symbol_to_delete in self.fractions_data:
            del self.fractions_data[symbol_to_delete]
            self._refresh_fractions_table()

    # --- 新增的UI刷新方法 ---
    def _refresh_components_table(self):
        self.components_table.setRowCount(0) 
        for comp in self.components_data:
            row = self.components_table.rowCount()
            self.components_table.insertRow(row)
            
            # 删除按钮
            delete_button = QPushButton()
            delete_button.setIcon(self.style().standardIcon(QStyle.SP_TrashIcon))
            # 使用 lambda 来捕获当前的 comp['symbol']
            # 需要注意 lambda 捕获变量的问题，确保 s=comp['symbol']
            delete_button.clicked.connect(lambda checked, s=comp['symbol']: self._on_delete_component_row(s))
            self.components_table.setCellWidget(row, 0, delete_button)
            
            self.components_table.setItem(row, 1, QTableWidgetItem(comp['symbol']))
            self.components_table.setItem(row, 2, QTableWidgetItem(comp['formula']))
            
    def _refresh_fractions_table(self):
        self.fractions_table.setRowCount(0) 
        for symbol, fraction in sorted(self.fractions_data.items()):
            row = self.fractions_table.rowCount()
            self.fractions_table.insertRow(row)

            # 删除按钮
            delete_button = QPushButton()
            delete_button.setIcon(self.style().standardIcon(QStyle.SP_TrashIcon))
            # 使用 lambda 来捕获当前的 symbol
            delete_button.clicked.connect(lambda checked, s=symbol: self._on_delete_fraction_row(s))
            self.fractions_table.setCellWidget(row, 0, delete_button)

            self.fractions_table.setItem(row, 1, QTableWidgetItem(symbol))
            self.fractions_table.setItem(row, 2, QTableWidgetItem(str(fraction)))

    def _update_ui_visibility(self):
        """根据'?'是否存在，来显示或隐藏过滤器。"""
        has_unknown = '?' in [c['symbol'] for c in self.components_data]
        self.filter_container.setVisible(has_unknown)

    def _gather_and_prepare_data(self):
        """
        新方法：从self属性收集并准备所有数据，供计算器使用。
        这实现了数据收集与API调用的分离。
        """
        if not self.components_data:
            raise ValueError("请至少定义一个化学组分。")
        
        # 从配置输入框收集参数
        params = {
            "n_max": int(self.n_max_input.text()),
            "mass_tolerance": float(self.mass_tol_input.text()),
            "fraction_tolerance": float(self.frac_tol_input.text())
        }
        
        # 收集过滤器状态
        if self.metal_radio.isChecked():
            params["unknown_filter"] = 'metal'
        elif self.nonmetal_radio.isChecked():
            params["unknown_filter"] = 'nonmetal'
        else:
            params["unknown_filter"] = 'unlimited'

        return self.components_data, self.fractions_data, params

    def _run_calculation(self):
        """现在只负责协调，逻辑更清晰。"""
        try:
            components, fractions, params = self._gather_and_prepare_data()

            # 模式选择
            has_unknown = '?' in [c['symbol'] for c in components]
            unknown_frac_given = '?' in fractions
            
            if has_unknown and unknown_frac_given:
                # print('IN WINDOW',components, fractions)
                results = self.calculator.solve_for_single_unknown(
                    known_components_data=components,
                    unknown_mass_fraction=fractions['?'],
                    mass_fractions=fractions,
                    n_max=params['n_max'],
                    tolerance=params['mass_tolerance'],
                    unknown_filter=params['unknown_filter']
                )
                self.results_viewer.display_results(results, 'unknown_element')
            else:
                if not fractions:
                    raise ValueError("通用模式下，请至少提供一个质量分数。")
                results = self.calculator.solve_by_brute_force(
                    components_data=components,
                    mass_fractions=fractions,
                    n_max=params['n_max'],
                    tolerance=params['fraction_tolerance']
                )
                self.results_viewer.display_results(results, 'general')

        except Exception as e:
            traceback.print_exc()
            QMessageBox.critical(self, "计算错误", str(e))
            self.results_viewer.show_error(str(e))