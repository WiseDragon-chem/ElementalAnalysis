from typing import Dict, List, Tuple, TypedDict, Optional, Set

# 周期表数据
METALS: Set[str] = {
    'Li', 'Be', 'Na', 'Mg', 'Al', 'K', 'Ca', 'Sc', 'Ti', 'V', 'Cr', 'Mn', 'Fe', 'Co', 'Ni', 'Cu', 'Zn',
    'Ga', 'Rb', 'Sr', 'Y', 'Zr', 'Nb', 'Mo', 'Ru', 'Rh', 'Pd', 'Ag', 'Cd', 'In', 'Sn', 'Sb', 'Cs', 'Ba',
    'La', 'Ce', 'W', 'Pt', 'Au', 'Hg', 'Pb', 'Bi'
}

NONMETALS: Set[str] = {
    'H', 'He', 'B', 'C', 'N', 'O', 'F', 'Ne', 'Si', 'P', 'S', 'Cl', 'Ar', 'As', 'Se', 'Br', 'Kr', 'Te', 'I', 'Xe'
}

ATOMIC_MASSES: Dict[str, float] = {
    'H': 1.008, 'He': 4.003, 'Li': 6.94, 'Be': 9.012, 'B': 10.81, 'C': 12.011,
    'N': 14.007, 'O': 15.999, 'F': 18.998, 'Ne': 20.180, 'Na': 22.990,
    'Mg': 24.305, 'Al': 26.982, 'Si': 28.085, 'P': 30.974, 'S': 32.06,
    'Cl': 35.45, 'Ar': 39.948, 'K': 39.098, 'Ca': 40.078, 'Sc': 44.956,
    'Ti': 47.867, 'V': 50.942, 'Cr': 51.996, 'Mn': 54.938, 'Fe': 55.845,
    'Co': 58.933, 'Ni': 58.693, 'Cu': 63.546, 'Zn': 65.38, 'Ga': 69.723,
    'Ge': 72.63, 'As': 74.922, 'Se': 78.971, 'Br': 79.904, 'Kr': 83.798,
    'Rb': 85.468, 'Sr': 87.62, 'Y': 88.906, 'Zr': 91.224, 'Nb': 92.906,
    'Mo': 95.96, 'Ru': 101.07, 'Rh': 102.906, 'Pd': 106.42, 'Ag': 107.868,
    'Cd': 112.41, 'In': 114.818, 'Sn': 118.71, 'Sb': 121.760, 'Te': 127.60,
    'I': 126.904, 'Xe': 131.29, 'Cs': 132.905, 'Ba': 137.327, 'La': 138.905,
    'Ce': 140.116, 'W': 183.84, 'Pt': 195.084, 'Au': 196.967, 'Hg': 200.59,
    'Pb': 207.2, 'Bi': 208.980
}

Formula = Dict[str, int]   #封装化学式的构成

class Component(TypedDict):
    """封装元素或原子团的数据"""
    symbol: str
    mass: float
    composition: Formula

class SolutionUnknown(TypedDict):
    """封装推测位置元素模式解的结构"""
    ans : Formula
    unknow_mass : float   #'?'元素的相对质量
    unknow_element :str   #'?'元素的符号