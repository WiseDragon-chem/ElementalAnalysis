from typing import Dict, List, Tuple, TypedDict, Optional, Set
from core import data_modules, utils
from itertools import product

class ChemicalCalculator:
    """封装化学式推断算法的计算器类。"""

    def __init__(self):
        """保存迭代过程中的中间变量"""
        self.know_components : list[data_modules.Component] = []
        self.mass_ratio_factor : float = 0
        self.solutions : List[data_modules.SolutionUnknown] = []
        self.n_max : int = 0
        self.tolerance : float = 0.0
        self.element_type = None

    def solve_for_single_unknown(self, 
                                 known_components_data: list[dict],
                                 unknown_mass_fraction: float,
                                 n_max: int,
                                 
                                 tolerance: float) -> list[data_modules.SolutionUnknown]:
        """
        实现“单一未知元素”模式的计算。
        这是该模式下对外的唯一接口。

        内部逻辑:
        1. 调用一个私有方法 (如 _prepare_components) 将输入的原始数据
           (known_components_data) 转换为内部标准的 List[Component] 格式。
        2. 执行之前设计的代数求解与递归搜索算法。
        3. 在每次计算出未知元素的原子质量后，调用 utils.find_matching_element 进行检验。
        4. 收集所有通过检验的、化学合理的解。
        5. 返回一个包含多个SolutionUnknown字典的列表。
        """
        self.__init__()
        self.known_components = self._prepare_components(known_components_data)   # 数据预处理
        self.mass_ratio_factor = unknown_mass_fraction / (1.0 - unknown_mass_fraction)
        self.solutions = []
        self.n_max = n_max
        self.tolerance = tolerance
        # self.element_type = elememt_type

        for n_unknown in range(1, n_max + 1):
            self._find_combinations_recursive(0, {'?': n_unknown}, 0.0)
        
        # 按元素种类数量和总原子数排序
        self.solutions.sort(key=lambda x: (len(x[0]), sum(x[0].values())))
        return self.solutions


    def solve_by_brute_force(self,
                             components_data: list[dict],
                             mass_fractions: dict[str, float],
                             n_max: int,
                             tolerance: float) -> list[data_modules.Formula]:
        """
        实现“通用推断”模式的计算。
        这是通用模式下对外的唯一接口。

        内部逻辑:
        1. 调用私有方法 _prepare_components 将输入的原始数据转换为 List[Component]。
        2. 执行基于 itertools.product 的暴力枚举算法。
        3. 对每一种组合，计算其总质量和各元素的质量分数。
        4. 将计算出的质量分数与用户输入的所有质量分数进行比较（在tolerance范围内）。
        5. 收集所有完全匹配的解。
        6. 返回一个包含多个Formula字典的列表。
        """
        components = self._prepare_components(components_data)
        comp_map = {c['symbol']: c for c in components}
        symbols = list(comp_map.keys())
        p = len(symbols)
        solutions = []

        for counts in product(range(1, n_max + 1), repeat=p):
            total_mass = 0.0
            element_counts: Dict[str, int] = {}

            for i, n in enumerate(counts):
                symbol = symbols[i]
                comp = comp_map[symbol]
                total_mass += n * comp['mass']
                for element, count in comp['composition'].items():
                    element_counts[element] = element_counts.get(element, 0) + n * count
        
            if total_mass < 1e-6: continue

            is_match = True
            for element, target_fraction in mass_fractions.items():
                if element in data_modules.ATOMIC_MASSES:
                    elem_mass = element_counts.get(element, 0) * data_modules.ATOMIC_MASSES[element]
                    actual_fraction = (elem_mass / total_mass) * 100.0
                    if abs(actual_fraction - target_fraction) > tolerance:
                        is_match = False
                        break
        
            if is_match:
                formula = {symbols[i]: n for i, n in enumerate(counts)}
                solutions.append(formula)

        # 按元素种类数量和总原子数排序
        solutions.sort(key=lambda f: (len(f), sum(f.values())))
        return solutions

    def _prepare_components(self, components_data: list[dict]) -> list[data_modules.Component]:
        """
        (私有) 将从GUI接收的原始字典列表转换为内部使用的、
        带有预计算质量的Component对象列表。
        - 对于原子团，会调用 utils.parse_formula。
        """
        ret : list[data_modules.Component] = []
        for item in components_data:
            mass_ , formula_ = utils.parse_formula(item['formula'])
            ret.append(data_modules.Component(symbol=item['symbol'],mass= mass_, composition=formula_))
        return ret


    def _find_combinations_recursive(self, comp_index: int, formula: 
                                     data_modules.Formula, known_mass_sum: float):
        """
        (私有) 'solve_for_single_unknown' 方法中使用的递归辅助函数。
        """
        if comp_index == len(self.known_components):
            if known_mass_sum > 1e-6:
                n_unknown = formula['?']
                unknown_atomic_mass = self.mass_ratio_factor * (known_mass_sum / n_unknown)
                
                # 化学合理性检验，使用指定的元素类型
                matched_element = utils.find_matching_element(unknown_atomic_mass, 
                                                              self.tolerance, self.element_type)
                if matched_element:
                    self.solutions.append((formula.copy(), unknown_atomic_mass, matched_element))
            return

        comp = self.known_components[comp_index]
        for n in range(1, self.n_max + 1):
            formula[comp['symbol']] = n
            self._find_combinations_recursive(comp_index + 1, formula, known_mass_sum + n * comp['mass'])
        del formula[comp['symbol']]