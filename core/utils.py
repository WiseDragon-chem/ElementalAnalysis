from typing import Dict, List, Tuple, TypedDict, Optional, Set
import re
import data_modules

def parse_formula(formula_str: str) -> tuple[float, data_modules.Formula]:
    """
    解析一个化学式字符串 (如 'C2H3O2')。
    - 验证字符串中的所有元素是否都存在于原子质量表中。
    - 返回计算出的总摩尔质量和其元素构成字典。
    - 如果解析失败，应抛出ValueError。
    返回：一个元组(质量,data_modules.Formula)
    """
    composition = data_modules.Formula()
    mass = 0.0
    for i in formula_str.strip():
        if not( 'a'<=i<='z' or 'A'<=i<='Z' or '0'<= i <= '9'):
            raise ValueError(f"记号'{i}'非法")
    for element, count_str in re.findall(r'([A-Z][a-z]?)(\d*)', formula_str):
        if element not in data_modules.ATOMIC_MASSES:
            raise ValueError(f"元素 '{element}' 不在原子质量表中。")
        count = int(count_str) if count_str else 1
        mass += data_modules.ATOMIC_MASSES[element] * count
        composition[element] = composition.get(element, 0) + count
    return (mass, composition)


def find_matching_element(mass: float, tolerance: float,
                          element_type: Optional[str] = None) -> str | None:
    """
    在原子质量表中查找与给定质量最匹配的元素。
    输入：tolerance为容差,element_type为
    - 遍历ATOMIC_MASSES。
    - 如果找到一个元素的质量在 `mass ± tolerance` 范围内，返回该元素的符号。
    - 如果没有找到匹配项，返回None。
    """
    best_match = None
    min_diff = float('inf')
    
    for symbol, atomic_mass in data_modules.ATOMIC_MASSES.items():
        diff = abs(mass - atomic_mass)
        
        if element_type == "metal" and symbol not in data_modules.METALS:
            continue
        if element_type == "nonmetal" and symbol not in data_modules.NONMETALS:
            continue
        
        # 寻找最接近的匹配
        if diff <= tolerance and diff < min_diff:
            best_match = symbol
            min_diff = diff
    
    return best_match
