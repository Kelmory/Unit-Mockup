import json
import random
from typing import List
from collections import defaultdict
from functools import reduce


class Unit:
    def __init__(self, code=None, title=None, credit=None, pre=None, prohibit=None) -> None:
        self.code = code
        self.title = title
        self.credit = credit
        self.level = int(list(code)[4]) * 1000
        self.prerequisites = pre
        self.prohibited = prohibit

    def __hash__(self) -> int:
        return hash(self.code)

    def __repr__(self) -> str:
        return f'{self.code}-{self.title}'

    def to_json(self):
        return {
            'code': self.code,
            'title': self.title,
            'credit': self.credit,
            'level': self.level,
            'prerequisites': [unit.code if isinstance(unit, Unit) else tuple(i.code for i in unit) for unit in self.prerequisites],
            'prohibited': [unit.code for unit in self.prohibited]
        }


class UnitFactory:
    level_dict = defaultdict(set)   # dict[level:(1,9)] -> Set(Unit)
    units = dict()        # dict[code] -> Unit
    titles = dict()

    PRE_THRESHOLD = 0.5
    PROHIBIT_THRESHOLD = 0.2
    PRE_DOUBLE = 0.4
    MAX_PRE = 4
    MAX_PROHIBIT = 3

    @classmethod
    def register(cls, title: str, prefix: str = "COMP", level: int = 1, credit: int = 6) -> Unit:
        order = len(cls.level_dict[level]) + 1
        code = f'{prefix}{level:1d}{order:03d}'
        unit = Unit(code, title, credit, set(), set())
        cls.units[code] = unit
        cls.titles[title] = unit
        cls.level_dict[level].add(unit)
        return unit

    @classmethod
    def random_prerequisite(cls, code: str) -> Unit:
        unit = cls.units[code]
        if unit.title.startswith('Advanced'):
            pre_code = ' '.join(unit.title.split()[1:])
            unit.prerequisites.add(cls.titles[pre_code])
        level = int(list(code)[4])
        if level == 1:
            return unit
        alternatives = [cls.level_dict[l]
                        for l in range(max(1, level-1), level)]
        alternatives = set(reduce(lambda x, y: x.union(y), alternatives))
        if unit in alternatives:
            alternatives.remove(unit)
        if random.random() < cls.PRE_THRESHOLD:
            n_pre = max(1, int(pow(random.random(), 1.25) * cls.MAX_PRE))
            choices = random.sample(alternatives, k=n_pre)

            def get_prerequisite(ch: List[Unit]) -> List[Unit]:
                pre1 = ch.pop()
                if random.random() < cls.PRE_DOUBLE and ch:
                    pre2 = ch.pop()
                    return ch, (pre1, pre2)
                else:
                    return ch, pre1
            while choices:
                choices, res = get_prerequisite(choices)
                unit.prerequisites.add(res)
        return unit

    @classmethod
    def random_prohibition(cls, code: str) -> Unit:
        unit = cls.units[code]
        level = int(list(code)[4])
        if level == 1:
            return unit
        alternatives = [cls.level_dict[l] for l in range(level, level+1)]
        alternatives = set(reduce(lambda x, y: x.union(y), alternatives))
        if unit in alternatives:
            alternatives.remove(unit)
        for pre in unit.prerequisites:
            if isinstance(pre, Unit):
                pre = [pre]
            alternatives.difference_update(pre)
        alternatives = [i for i in alternatives if unit not in i.prerequisites]
        if random.random() < cls.PROHIBIT_THRESHOLD:
            n_proh = max(1, int(random.random() * cls.MAX_PROHIBIT))
            choices = random.sample(alternatives, k=n_proh)
            unit.prohibited = unit.prohibited.union(choices)
        return unit


class UnitGenerator:
    topics = [
        "linear algebra", "calculus", "discrete mathematics", "probability theory",
        "data structure", "algorithm", "object oriented programming",
        "computer organization", "compiler theory", "operating system",
        "database theory", "network theory",
        "design patterns", "web application design", "computer graphics",
        "mobile application development", "parallel computing",
        "machine learning", "data mining", "distributed systems",
        "natural language processing", "image and signal processing",
    ]
    MAX_LEVEL = 4

    @staticmethod
    def capitalize(topic: str) -> str:
        return " ".join(t.capitalize() for t in topic.split())

    @classmethod
    def determine_level(cls, order: int, advanced: bool = False) -> int:
        level = order / len(cls.topics) * cls.MAX_LEVEL + 1
        level = level if not advanced else level * 1.25
        if level > cls.MAX_LEVEL:
            level = cls.MAX_LEVEL
        return int(level)

    @classmethod
    def generate(cls) -> List[Unit]:
        units = []
        for i, topic in enumerate(cls.topics):
            def register(i, topic, advanced=False):
                level = UnitGenerator.determine_level(i, advanced)
                topic = UnitGenerator.capitalize(topic)
                unit = UnitFactory.register(topic, level=level)
                return unit

            units.append(register(i, topic))

            units.append(
                register(int(i * 1.25), 'Advanced ' + topic, advanced=True))
        return units


class Degree:
    code_count = 1

    def __init__(self, name: str, year: int) -> None:
        self.name = name
        self.code = self.get_code()
        self.credits = [6 * random.choice([6, 8])] * year

    def to_json(self):
        return {
            'name': self.name,
            'code': self.code,
            'credits': self.credits
        }

    @classmethod
    def get_code(cls) -> int:
        res = f'DEGREE{cls.code_count:02d}'
        cls.code_count += 1
        return res


class DegreeGenerator:
    names = {
        "Bachelor of Information Technology": 3,
        "Bachelor of Computer Science": 3,
        "Hornour Bachelor of Computer Science": 4,
    }

    @classmethod
    def generate(cls):
        degrees = []
        for name, year in cls.names.items():
            degrees.append(Degree(name, year))
        return degrees


if __name__ == "__main__":
    units = UnitGenerator.generate()
    for unit in units:
        unit = UnitFactory.random_prerequisite(unit.code)
        unit = UnitFactory.random_prohibition(unit.code)
    with open('./units.json', 'w') as f:
        json.dump([uni.to_json() for uni in units], f)

    with open('./degrees.json', 'w') as f:
        json.dump([deg.to_json() for deg in DegreeGenerator.generate()], f)
