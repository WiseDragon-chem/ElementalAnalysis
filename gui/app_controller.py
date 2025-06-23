"""
定义 AppController 类，作为应用程序的业务逻辑和流程控制中心。
它与数据和计算核心交互，并通过信号与GUI通信。
"""

from PyQt5.QtCore import QObject, pyqtSignal
import traceback
from data.data_manager import DataManager
from core.calculator import ChemicalCalculator 
from gui.dialogs.add_component_dialog import AddComponentDialog
from gui.dialogs.add_fraction_dialog import AddFractionDialog

class AppController(QObject):

    # 信号
    components_changed = pyqtSignal()    # 当组分列表变化时发射
    fractions_changed = pyqtSignal()    # 当质量分数列表变化时发射
    calculation_finished = pyqtSignal(list, str)   # 当计算完成时发射，携带结果和模式
    error_occurred = pyqtSignal(str)   # 当发生错误时发射


    def __init__(self):
        super().__init__()
        self.data_manager = DataManager()
        self.calculator = ChemicalCalculator()

    def handle_add_component(self, parent_widget):
        """处理添加组分的请求。"""
        # print('IN CONTROLLER ADD COMPONENT')
        if AddComponentDialog.show_dialog(self.data_manager, parent_widget):
            self.components_changed.emit() # 数据已变，发射信号

    def handle_add_fraction(self, parent_widget):
        """处理添加质量分数的请求。"""
        if not self.data_manager.get_component_symbols():
            self.error_occurred.emit("请先至少定义一个化学组分。")
            return
        if AddFractionDialog.show_dialog(self.data_manager, parent_widget):
            self.fractions_changed.emit() # 数据已变，发射信号
    
    def handle_component_edited(self, row, new_formula):
        """处理组分表格编辑。"""
        try:
            self.data_manager.update_component_formula(row, new_formula)
        except ValueError as e:
            self.error_occurred.emit(str(e))
            self.components_changed.emit() # 发射信号以恢复UI为原始数据

    def handle_fraction_edited(self, symbol, new_fraction_str):
        """处理质量分数表格编辑。"""
        try:
            new_fraction = float(new_fraction_str)
            self.data_manager.update_fraction_value(symbol, new_fraction)
        except ValueError as e:
            self.error_occurred.emit(str(e))
            self.fractions_changed.emit() # 发射信号以恢复UI

    def run_calculation(self, params: dict):
        """处理计算请求。"""
        try:
            components = self.data_manager.get_all_components()
            fractions = self.data_manager.get_all_fractions()

            if not components:
                raise ValueError("请至少定义一个化学组分。")
            # print(f'IN CONTROLLER, {components}')
            has_unknown = '?' in [c['symbol'] for c in components]
            # unknown_frac_given = '?' in fractions

            if has_unknown :
                results = self.calculator.solve_for_single_unknown(
                    known_components_data=components,
                    mass_fractions=fractions,
                    n_max=params['n_max'],
                    tolerance=params['mass_tolerance'],
                    unknown_filter=params['unknown_filter']
                )
                self.calculation_finished.emit(results, 'unknown_element')
            else:
                if not fractions:
                    raise ValueError("通用模式下，请至少提供一个质量分数。")
                results = self.calculator.solve_by_brute_force(
                    components_data=components,
                    mass_fractions=fractions,
                    n_max=params['n_max'],
                    tolerance=params['fraction_tolerance']
                )
                self.calculation_finished.emit(results, 'general')
        except Exception as e:
            traceback.print_exc()
            self.error_occurred.emit(f"计算错误: {e}")