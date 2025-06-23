from typing import Dict, List, Tuple, TypedDict, Optional, Set
import re,copy
from core import data_modules

def parse_formula(formula_str: str) -> tuple[float, data_modules.Formula]:
    """
    解析一个化学式字符串 (如 'C2H3O2')。
    - 验证字符串中的所有元素是否都存在于原子质量表中。
    - 返回计算出的总摩尔质量和其元素构成字典。
    - 如果解析失败，应抛出ValueError。
    返回：一个元组(质量,data_modules.Formula)
    """
    composition:data_modules.Formula = dict() 
    mass = 0.0
    if formula_str == '?':
        composition['?'] = 1
        return (0,composition)
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
    返回：一个包含元素符号的字符串
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

def check_component(symbol : str, formula : str, existing_symbols : list[str] ):
    """检验用户输入的化学式是否合法"""
    if symbol == '？':  
        symbol = '?'
    # print('IN CHECK',existing_symbols,symbol,formula)
    if symbol in existing_symbols:
        raise ValueError(f'组分{symbol}已经被添加')
    if symbol == '?':
        if formula == '' or '?' or '？':
            return ('?',"?")
        else:
            raise ValueError('不得覆写?的化学组成')
    if symbol == '':
        raise ValueError('请输入元素符号')
    if symbol.strip() in data_modules.ATOMIC_MASSES.keys():
        if formula.strip() == '' or  formula.strip() == symbol.strip():
            return (symbol,symbol)
        else:
            raise ValueError(f'符号{symbol}已在元素周期表中，不得覆写其化学组成')
    ans,_ = parse_formula(formula)
    if ans <= 1e-5:
        raise ValueError(f'符号{symbol}不在元素周期表中，需要给出化学组成')
    return (symbol,formula)

def check_fraction(symbol :str, fraction_str: str, defined_symbols: list[str]):
    if symbol == '?' or symbol == '？':
        if '?' in defined_symbols:
            try:
                fraction_ = float(fraction_str)
            except ValueError:
                raise ValueError('质量分数应为(0,100)范围内的数')
            if fraction_ <= 0 or fraction_>=100:
                raise ValueError('质量分数应为(0,100)范围内的数')
            return ('?', fraction_)
        else:
            raise ValueError('没有定义未知元素')
    if symbol not in data_modules.ATOMIC_MASSES.keys():
        raise ValueError(f'{symbol}不是元素, 请输入正确的元素符号')
    if symbol not in defined_symbols:
        raise ValueError(f'符号{symbol}尚未添加，需要在添加化学组分窗口添加')
    if symbol == '':
        raise ValueError('请输入元素符号')
    # print('BEFORE CHECK STR')
    try: 
        fraction_ = float(fraction_str)
    except ValueError:
        raise ValueError('质量分数应为(0,100)范围内的数')
    if fraction_ <= 0 or fraction_>=100:
        raise ValueError('质量分数应为(0,100)范围内的数')

    return symbol, fraction_

def _vertify_fraction_calculate(
        test_formula : data_modules.Formula,
        mass_fractions: dict[str, float],
        tolerance: float,
        unknow_element: Optional[str] = None) -> bool:
    """
    该函数将在calculator中调用,用于检验化学式是否符合所有质量分数信息。
    输入：test_formula:需要检测的化学式;
    mass_fraction: 保存质量分数的列表;
    tolerance: 容差;
    unknow_element: (可选参数：未知元素)
    """
    total_mass = 0.0
    _test_formula = copy.copy(test_formula)
    _mass_fractions = copy.copy(mass_fractions)   #防止后续修改字典影响了别人
    if unknow_element:
        _mass_fractions[unknow_element] = mass_fractions['?']
        _test_formula[unknow_element] = test_formula['?']
        del _test_formula['?'], _mass_fractions['?']
    # print('IN VERTIFY',_test_formula, _mass_fractions)
    for element, number in _test_formula.items():
        total_mass += data_modules.ATOMIC_MASSES[element] * number
    for element, target_fraction in _mass_fractions.items():
        elem_mass = _test_formula[element] * data_modules.ATOMIC_MASSES[element]
        actual_fraction = (elem_mass / total_mass) * 100.0
        if abs(actual_fraction - target_fraction) > tolerance:
            return False
    return True