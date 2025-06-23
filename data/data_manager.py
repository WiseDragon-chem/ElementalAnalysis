from core.utils import check_component,check_fraction
from core.data_modules import ATOMIC_MASSES

class DataManager:
    """
    管理所有化学组分和质量分数数据的单一来源。
    包含所有的数据验证和操作逻辑。
    """

    def __init__(self):
        self.components = []   # 例如: [{'symbol': 'OAc', 'formula': 'C2H3O2'}]
        self.fractions = {}   # 例如: {'C': 40.123}

    def add_component(self, symbol: str, formula: str):
        """验证并添加一个新的化学组分。"""
        _symbol_list = self.get_component_symbols()
        symbol, formula = check_component(symbol, formula, _symbol_list)
        self.components.append({'symbol': symbol, 'formula': formula})

    def add_fraction(self, symbol: str, fraction: float):
        """验证并添加一个新的质量分数。"""
        _symbol_list = self.get_component_symbols()
        symbol , fraction_ = check_fraction(symbol, str(fraction), _symbol_list)
        self.fractions[symbol] = fraction_

    def update_component_formula(self, index: int, new_formula: str):
        """验证并更新指定索引的组分的化学式 (用于表格直接编辑)。"""
        if 0 <= index < len(self.components):
            symbol = self.components[index]['symbol']
            _symbol_list = self.get_component_symbols()
            _symbol_list.remove(symbol)
            check_component(symbol, new_formula, _symbol_list)
            self.components[index]['formula'] = new_formula

    def update_fraction_value(self, symbol: str, new_fraction: float):
        """验证并更新指定符号的质量分数 (用于表格直接编辑)。"""
        if symbol in self.fractions:
            _symbol_list = self.get_component_symbols()
            # _symbol_list.remove(symbol)
            check_fraction(symbol, str(new_fraction), _symbol_list)
            self.fractions[symbol] = new_fraction

    def update_component_symbol(self, index: int, new_symbol: str):
        """验证并更新指定索引的组分的符号。"""
        if not (0 <= index < len(self.components)):
            return    # 索引无效，静默失败

        old_symbol = self.components[index]['symbol']
        if old_symbol == new_symbol:
            return    # 没有变化

        # 验证新符号的格式 (使用现有的化学式)
        formula = self.components[index]['formula']
        check_component(new_symbol, formula, self.get_component_symbols())

        # 验证新符号的唯一性 (确保不与除自身外的其他符号冲突)
        other_symbols = [c['symbol'] for i, c in enumerate(self.components) if i != index]
        if new_symbol in other_symbols:
            raise ValueError(f"错误: 符号 '{new_symbol}' 已被其他组分使用。")
        
        # 同步更新质量分数列表
        if old_symbol in self.fractions:
            if new_symbol not in ATOMIC_MASSES.keys():
                raise ValueError(f"旧符号'{old_symbol}'已在质量分数表中, 新符号需要是周期表中元素。")
            fraction_value = self.fractions.pop(old_symbol)     # 移除旧条目
            self.fractions[new_symbol] = fraction_value      # 添加新条目
        
        # 更新组分列表中的符号
        self.components[index]['symbol'] = new_symbol

    def delete_component(self, index: int):
        """根据索引删除一个组分，并同步删除其对应的质量分数。"""
        if not (0 <= index < len(self.components)):
            return

        # 在删除组分前，先获取其符号
        symbol_to_delete = self.components[index]['symbol']
        
        # 从组分列表中删除
        self.components.pop(index)
        
        # 如果这个组分在质量分数字典中也存在，则一并删除
        if symbol_to_delete in self.fractions:
            del self.fractions[symbol_to_delete]

    def delete_fraction(self, symbol: str):
        """
        根据符号删除一个质量分数。
        """
        if symbol in self.fractions:
            del self.fractions[symbol]

    def get_all_components(self) -> list[dict]:
        """返回所有组分数据的深拷贝，防止外部修改。"""
        return [item.copy() for item in self.components]

    def get_all_fractions(self) -> dict[str, float]:
        """返回所有质量分数数据的拷贝。"""
        return self.fractions.copy()

    def get_component_symbols(self) -> list[str]:
        """返回一个包含所有已定义组分符号的列表。"""
        return [c['symbol'] for c in self.components]