import sys,traceback
sys.path.append('..')

from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QMessageBox, QTableWidget, QGroupBox,
                             QTableWidgetItem, QAbstractItemView, QHeaderView,
                             QFormLayout, QLineEdit)
from PyQt5.QtGui import QIntValidator, QDoubleValidator

from gui.dialogs.add_component_dialog import AddComponentDialog
from gui.dialogs.add_fraction_dialog import AddFractionDialog
from gui.widgets.results_viewer import ResultsViewerWidget
from core.calculator import ChemicalCalculator

class MainWindow(QMainWindow):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.calculator = ChemicalCalculator() # 使用模拟计算器
        self.setWindowTitle("智能化学式推断程序 v3.0")
        self.setGeometry(100, 100, 1000, 600)
        self._setup_ui()

    def _setup_ui(self):
        # --- 主布局和中心组件 ---
        main_layout = QHBoxLayout()
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # --- 1. 左侧列 ---
        left_layout = self._create_left_column()
        
        # --- 2. 中间列 ---
        center_layout = self._create_center_column()

        # --- 3. 右侧列 ---
        self.results_viewer = ResultsViewerWidget()

        # --- 组合三列 ---
        main_layout.addLayout(left_layout, 3)      
        main_layout.addLayout(center_layout, 1)    
        main_layout.addWidget(self.results_viewer, 3) 

    def _create_left_column(self):
        """创建并返回左侧列的布局。"""
        layout = QVBoxLayout()
        
        # 组分表格
        comp_group = QGroupBox("1. 组分定义")
        comp_layout = QVBoxLayout(comp_group)
        self.components_table = QTableWidget(0, 2)
        self.components_table.setHorizontalHeaderLabels(["符号", "化学式"])
        self.components_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.components_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        comp_layout.addWidget(self.components_table)
        self.add_comp_button = QPushButton("添加组分...")
        comp_layout.addWidget(self.add_comp_button)
        layout.addWidget(comp_group)
        
        # 质量分数表格
        frac_group = QGroupBox("2. 质量分数")
        frac_layout = QVBoxLayout(frac_group)
        self.fractions_table = QTableWidget(0, 2)
        self.fractions_table.setHorizontalHeaderLabels(["符号", "分数 (%)"])
        self.fractions_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
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
        """创建并返回中间列的布局。"""
        layout = QVBoxLayout()
        
        config_group = QGroupBox("计算参数")
        config_layout = QFormLayout(config_group)
        
        self.n_max_input = QLineEdit("10")
        self.n_max_input.setValidator(QIntValidator(1, 100))
        
        self.mass_tol_input = QLineEdit("0.2")
        self.mass_tol_input.setValidator(QDoubleValidator(0.01, 5.0, 2))

        self.frac_tol_input = QLineEdit("0.5")
        self.frac_tol_input.setValidator(QDoubleValidator(0.01, 10.0, 2))
        
        config_layout.addRow("最大原子计数 (n_max):", self.n_max_input)
        config_layout.addRow("原子质量公差 (g/mol):", self.mass_tol_input)
        config_layout.addRow("质量分数公差 (%):", self.frac_tol_input)
        
        self.calculate_button = QPushButton("开始推断")
        self.calculate_button.setStyleSheet("font-size: 16px; padding: 10px; background-color: #4CAF50; color: white;")
        
        layout.addWidget(config_group)
        layout.addStretch() # 添加伸缩因子，将按钮推到底部
        layout.addWidget(self.calculate_button)
        
        self.calculate_button.clicked.connect(self._run_calculation)
        
        return layout

    def _on_add_component(self):
        """处理添加组分按钮点击事件"""
        data = AddComponentDialog.get_new_component(self)
        if data:
            row = self.components_table.rowCount()
            self.components_table.insertRow(row)
            self.components_table.setItem(row, 0, QTableWidgetItem(data['symbol']))
            self.components_table.setItem(row, 1, QTableWidgetItem(data['formula']))

    def _on_add_fraction(self):
        """处理添加质量分数按钮点击事件"""
        data = AddFractionDialog.get_new_fraction(self)
        if data:
            symbol, fraction = data
            row = self.fractions_table.rowCount()
            self.fractions_table.insertRow(row)
            self.fractions_table.setItem(row, 0, QTableWidgetItem(symbol))
            self.fractions_table.setItem(row, 1, QTableWidgetItem(str(fraction)))

    def _run_calculation(self):
        """核心协调方法：收集数据，调用后端，显示结果。"""
        try:
            # --- 1. 从UI收集数据 ---
            # 从组分表格收集
            components_data = []
            for row in range(self.components_table.rowCount()):
                symbol = self.components_table.item(row, 0).text()
                formula = self.components_table.item(row, 1).text()
                components_data.append({'symbol': symbol, 'formula': formula})

            # 从质量分数表格收集
            mass_fractions_data = {}
            for row in range(self.fractions_table.rowCount()):
                symbol = self.fractions_table.item(row, 0).text()
                fraction = float(self.fractions_table.item(row, 1).text())
                mass_fractions_data[symbol] = fraction

            # 从配置输入框收集
            n_max = int(self.n_max_input.text())
            mass_tol = float(self.mass_tol_input.text())
            frac_tol = float(self.frac_tol_input.text())

            if not components_data:
                raise ValueError("请至少定义一个化学组分。")

            # --- 2. 智能模式选择 ---
            has_unknown_comp = any(c['symbol'] == '?' for c in components_data)
            unknown_fraction_provided = '?' in mass_fractions_data

            # 3. 调用后端（此处为模拟调用）
            print(components_data)
            print(mass_fractions_data)
            if has_unknown_comp and unknown_fraction_provided:
                results = self.calculator.solve_for_single_unknown(
                    # 此处应有数据转换逻辑，将UI数据转为core模块的格式
                    known_components_data=components_data, 
                    unknown_mass_fraction=mass_fractions_data['?'],
                    n_max=n_max, 
                    tolerance=mass_tol
                )
                self.results_viewer.display_results(results, 'unknown_element')
            else:
                if not mass_fractions_data:
                    raise ValueError("通用模式下，请至少提供一个质量分数。")
                results = self.calculator.solve_by_brute_force(
                    components_data=components_data,
                    mass_fractions=mass_fractions_data,
                    n_max=n_max,
                    tolerance=frac_tol
                )
                self.results_viewer.display_results(results, 'general')

        except Exception as e:
            traceback.print_exc()
            QMessageBox.critical(self, "错误", str(e))
            self.results_viewer.show_error(str(e))