from typing import Dict, List, Tuple, TypedDict, Optional, Set
from core import data_modules, utils
from itertools import product

class ChemicalCalculator:
    """封装化学式推断算法的计算器类。"""

    def solve_for_single_unknown(self,
                                 known_components_data: list[dict],
                                 mass_fractions: dict[str, float], 
                                 n_max: int,
                                 tolerance: float,
                                 unknown_filter: str) -> list[data_modules.SolutionUnknown]:  
        """
        实现“单一未知元素”模式的计算（新版）。
        利用已知元素的质量分数来反推未知元素的原子质量。
        """
        # 1. 移除 self.__init__()，避免在每次调用时重置整个对象
        # 2. 将状态作为局部变量管理，使方法可重入
        known_components = self._prepare_components(known_components_data)
        solutions = []

        if not mass_fractions:
             raise ValueError("至少提供一个其他元素的质量分数。")

        # 3. 循环和递归调用
        for n_unknown in range(1, n_max + 1):
            # 将所有需要的参数传递给递归函数
            self._find_combinations_recursive(
                # --- 递归函数的参数 ---
                comp_index=0,
                formula={'?': n_unknown},
                known_mass_sum=0.0,
                # --- 不变的上下文参数 ---
                known_components=known_components,
                mass_fractions=mass_fractions,
                n_max=n_max,
                tolerance=tolerance,
                element_type=unknown_filter,
                solutions_list=solutions # 将解决方案列表作为引用传递
            )
        
        # 4. 排序和返回
        solutions.sort(key=lambda x: (len(x[0]), sum(x[0].values())))
        return solutions
    
    def _find_combinations_recursive(self, comp_index: int,
                                     formula: data_modules.Formula, 
                                     known_mass_sum: float,
                                     known_components: list,
                                     mass_fractions : dict[str, float],
                                     n_max: int,
                                     tolerance: float,
                                     element_type: str,
                                     solutions_list: list):
        """递归辅助函数，实现了基于已知元素质量分数的求解和验证逻辑。"""

        # print('IN RECURSIVE',formula, solutions_list)
        if comp_index == len(known_components):        # 当所有已知组分的数量都已确定 
            if known_mass_sum > 1e-6:
                
                base_element = list(mass_fractions.keys())[0]  # a. 选择一个基准元素来计算 A_?
                w_base = mass_fractions[base_element] / 100.0 # 转换为小数
                
                m_base_calculated = self._calculate_elemental_mass_in_formula(formula, known_components, base_element) # b. 计算分子中基准元素的总质量

                n_unknown = formula['?']   # c. 使用新公式求解 A_?
                if w_base < 1e-9 or n_unknown == 0: return  # 防止除零错误
                denominator = w_base * n_unknown
                if abs(denominator) < 1e-9: return
                unknown_atomic_mass = (m_base_calculated - w_base * known_mass_sum) / denominator

                if not (1.0 <= unknown_atomic_mass <= 300.0):   # d. 初步合理性检验
                    return
                
                total_mass_hypothetical = known_mass_sum + n_unknown * unknown_atomic_mass    # e. 验证：用算出的 A_? 检验所有给定的质量分数是否吻合
                if total_mass_hypothetical < 1e-6: return

                for element, target_fraction in mass_fractions.items():
                    m_element_calc = self._calculate_elemental_mass_in_formula(formula, known_components, element)
                    actual_fraction = (m_element_calc / total_mass_hypothetical) * 100.0
                    
                    if abs(actual_fraction - target_fraction) > tolerance:
                        return  # 不吻合，此解无效

                matched_element = utils.find_matching_element(    # f. 最终化学合理性检验：匹配真实元素
                    unknown_atomic_mass, tolerance, element_type
                )
                if matched_element in mass_fractions.keys():
                    return
                if matched_element:
                    solutions_list.append((formula.copy(), unknown_atomic_mass, matched_element))
            return

        comp = known_components[comp_index]   # f. 最终化学合理性检验：匹配真实元素
        # 允许组分数量为0，以处理并非所有组分都存在的情况
        for n in range(0, n_max + 1):
            new_formula = formula.copy()
            if n > 0:
                new_formula[comp['symbol']] = n
            self._find_combinations_recursive(
                comp_index + 1,
                new_formula,
                known_mass_sum + n * comp['mass'],
                known_components, mass_fractions, n_max, tolerance, element_type, solutions_list
            )


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
        # WARNING ========================== ERROR OCCURED WHEN MASS FRACTION HAS NO ?
        components = self._prepare_components(components_data)
        # print(components, mass_fractions)
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
                elem_mass = element_counts.get(element, 0) * data_modules.ATOMIC_MASSES[element]
                actual_fraction = (elem_mass / total_mass) * 100.0
                # print(actual_fraction, target_fraction)
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
            # print('IN PREPARE', item)
            if item['symbol'] == '?':
                continue
            mass_ , formula_ = utils.parse_formula(item['formula'])
            ret.append(data_modules.Component(symbol=item['symbol'],mass= mass_, composition=formula_))
        return ret

    def _calculate_elemental_mass_in_formula(self, formula: dict, known_components: list, target_element: str) -> float:
        """
        (新增的私有辅助函数)
        计算一个假设的化学式中，某个指定元素的总质量。
        """
        total_element_mass = 0.0
        
        # 将 known_components 转换为字典以便快速查找
        comp_map = {comp['symbol']: comp for comp in known_components}

        for symbol, count in formula.items():
            if symbol == '?': continue
            
            component = comp_map[symbol]
            # 获取该组分的元素构成，并查找目标元素的数量
            num_atoms_in_comp = component['composition'].get(target_element, 0)
            
            if num_atoms_in_comp > 0:
                total_element_mass += count * num_atoms_in_comp * data_modules.ATOMIC_MASSES[target_element]
        
        return total_element_mass