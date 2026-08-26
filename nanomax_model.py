"""Core NanoMax asymmetric DNA aptamer inverse-design engine.

This module is adapted from the supplied Google Colab notebook. The original
notebook was RNA-oriented (A/C/G/U). This deployment version is DNA-oriented
(A/C/G/T), replacing A-U pairing with A-T pairing while preserving the same
constraint-guided stochastic design logic.
"""

from __future__ import annotations

from collections import Counter
from math import log2
import random
from typing import Dict, List, Optional, Tuple

import numpy as np


class AsymmetricDNAAptamerDesigner:
    """Constraint-guided stochastic generator for asymmetric DNA aptamers."""

    def __init__(self, seed: Optional[int] = None):
        self.bases = ["A", "C", "G", "T"]
        self.base_colors = {
            "A": "#2E8B57",
            "C": "#2F6BFF",
            "G": "#F59E0B",
            "T": "#E5484D",
        }
        self.base_pairs = {"A": "T", "T": "A", "G": "C", "C": "G"}
        self._py_rng = random.Random(seed)
        self._np_rng = np.random.default_rng(seed)

    def generate_asymmetric_multibranch(
        self, length: int, branches: int, loops: int
    ) -> str:
        """Generate an asymmetric multibranch target structure in dot-bracket form."""
        length = max(100, min(200, int(length)))
        branches = max(2, min(5, int(branches)))
        loops = max(3, min(8, int(loops)))

        structure: List[str] = []

        def create_branch(stem_len: int, has_loop: bool = True) -> List[str]:
            branch: List[str] = []
            left_stem = stem_len
            right_stem = stem_len + self._py_rng.randint(-2, 2)
            right_stem = max(3, min(8, right_stem))
            branch.extend(["("] * left_stem)
            if has_loop:
                loop_len = self._py_rng.randint(3, 7)
                branch.extend(["."] * loop_len)
            branch.extend([")"] * right_stem)
            return branch

        def create_bridge(bridge_length: int, is_paired: bool = True) -> List[str]:
            if is_paired and bridge_length >= 6:
                stem = min(3, bridge_length // 3)
                return ["("] * stem + ["."] * (bridge_length - 2 * stem) + [")"] * stem
            return ["."] * bridge_length

        start_len = self._py_rng.randint(5, 15)
        structure.extend(["."] * start_len)
        current_pos = start_len

        for branch_index in range(branches):
            stem_len = self._py_rng.randint(4, 8)
            has_internal_loop = self._py_rng.random() > 0.7
            branch = create_branch(stem_len, has_internal_loop)

            if branch_index > 0:
                bridge_len = self._py_rng.randint(2, 10)
                structure.extend(
                    create_bridge(bridge_len, self._py_rng.random() > 0.5)
                )
                current_pos += bridge_len

            structure.extend(branch)
            current_pos += len(branch)

        for _ in range(loops):
            if current_pos >= length - 20:
                break

            loop_type = self._py_rng.choice(["hairpin", "bulge", "internal"])
            if loop_type == "hairpin":
                stem = self._py_rng.randint(3, 6)
                loop_len = self._py_rng.randint(4, 8)
                segment = ["("] * stem + ["."] * loop_len + [")"] * stem
            elif loop_type == "bulge":
                segment = ["."] * self._py_rng.randint(1, 4)
            else:
                left_stem = self._py_rng.randint(2, 4)
                loop_len = self._py_rng.randint(2, 5)
                right_stem = self._py_rng.randint(2, 4)
                segment = ["("] * left_stem + ["."] * loop_len + [")"] * right_stem

            structure.extend(segment)
            current_pos += len(segment)

        remaining = length - current_pos
        if remaining > 10:
            terminal_patterns = [
                "(" * 3 + "." * 4 + "(" * 2 + "." * 3 + ")" * 2 + "." * 3 + ")" * 3,
                "." * 5 + "(" * 4 + "." * 6 + ")" * 4 + "." * 3,
                "(" * 2 + "." * 2 + "(" * 3 + "." * 4 + ")" * 3 + "." * 2 + ")" * 2,
            ]
            terminal = self._py_rng.choice(terminal_patterns)[:remaining]
            structure.extend(list(terminal))
            current_pos += len(terminal)

        if current_pos < length:
            structure.extend(["."] * (length - current_pos))
        elif current_pos > length:
            structure = structure[:length]

        return self._balance_structure("".join(structure))

    @staticmethod
    def _balance_structure(structure: str) -> str:
        """Ensure dot-bracket parentheses are balanced."""
        result: List[str] = []
        stack: List[int] = []

        for char in structure:
            if char == "(":
                stack.append(len(result))
                result.append("(")
            elif char == ")":
                if stack:
                    stack.pop()
                    result.append(")")
                else:
                    result.append(".")
            else:
                result.append(char)

        for idx in stack:
            result[idx] = "."
        return "".join(result)

    def generate_sequence(self, structure: str, gc_target: float = 0.60) -> str:
        """Generate a DNA sequence compatible with a target dot-bracket structure."""
        gc_target = min(0.80, max(0.40, float(gc_target)))
        base_probs = {
            "A": (1 - gc_target) * 0.5,
            "T": (1 - gc_target) * 0.5,
            "G": gc_target * 0.5,
            "C": gc_target * 0.5,
        }

        stack: List[int] = []
        paired_positions: List[Tuple[int, int]] = []
        for i, char in enumerate(structure):
            if char == "(":
                stack.append(i)
            elif char == ")" and stack:
                paired_positions.append((stack.pop(), i))

        bases = list(base_probs.keys())
        probs = list(base_probs.values())
        sequence = list(self._np_rng.choice(bases, size=len(structure), p=probs))

        # Preserve the notebook's strong-pair preference: 70% GC, 30% AT.
        for i, j in paired_positions:
            if self._py_rng.random() < 0.70:
                pair = ("G", "C") if self._py_rng.random() < 0.5 else ("C", "G")
            else:
                pair = ("A", "T") if self._py_rng.random() < 0.5 else ("T", "A")
            sequence[i], sequence[j] = pair

        counts = Counter(sequence)
        missing_bases = [base for base in self.bases if counts.get(base, 0) < 3]
        for base in missing_bases:
            for _ in range(20):
                pos = self._py_rng.randint(0, len(sequence) - 1)
                if structure[pos] == ".":
                    sequence[pos] = base
                    break

        return "".join(sequence)

    def analyze_aptamer(self, structure: str, sequence: str) -> Dict[str, float]:
        """Calculate sequence and structural descriptors."""
        analysis: Dict[str, float] = {}
        analysis["length"] = len(sequence)
        analysis["gc_content"] = (
            (sequence.count("G") + sequence.count("C")) / len(sequence) * 100
        )

        for base in self.bases:
            count = sequence.count(base)
            analysis[f"{base}_count"] = count
            analysis[f"{base}_percent"] = count / len(sequence) * 100

        analysis["paired_bases"] = structure.count("(") + structure.count(")")
        analysis["unpaired_bases"] = structure.count(".")
        analysis["pairing_percent"] = analysis["paired_bases"] / len(structure) * 100
        analysis["hairpins"] = self._count_hairpins(structure)
        analysis["bulges"] = self._count_bulges(structure)
        analysis["internal_loops"] = self._count_internal_loops(structure)
        analysis["branches"] = self._count_branches(structure)
        analysis["asymmetry_score"] = self._calculate_asymmetry(structure)
        analysis["sequence_complexity"] = self._calculate_complexity(sequence)
        analysis["purine_pyrimidine_ratio"] = self._calculate_purine_pyrimidine_ratio(sequence)

        stability, gc_pairs, at_pairs, total_pairs = self._estimate_stability(structure, sequence)
        analysis["stability_score"] = stability
        analysis["gc_pairs"] = gc_pairs
        analysis["at_pairs"] = at_pairs
        analysis["total_pairs"] = total_pairs
        return analysis

    @staticmethod
    def _count_hairpins(structure: str) -> int:
        count = 0
        i = 0
        while i < len(structure):
            if structure[i] == "(":
                depth = 1
                j = i + 1
                while j < len(structure) and depth > 0:
                    if structure[j] == "(":
                        depth += 1
                    elif structure[j] == ")":
                        depth -= 1
                        if depth == 0:
                            inside = structure[i + 1 : j]
                            if inside and all(c == "." for c in inside):
                                count += 1
                            i = j
                            break
                    j += 1
            i += 1
        return count

    @staticmethod
    def _count_bulges(structure: str) -> int:
        return sum(
            1
            for i in range(len(structure) - 2)
            if structure[i] == "(" and structure[i + 1] == "." and structure[i + 2] == ")"
        )

    @staticmethod
    def _count_internal_loops(structure: str) -> int:
        count = 0
        for i in range(len(structure) - 4):
            if structure[i] == "(" and structure[i + 1] == "." and ")" in structure[i + 2 : i + 6]:
                count += 1
        return count

    @staticmethod
    def _count_branches(structure: str) -> int:
        count = 0
        depth = 0
        for i in range(1, len(structure) - 1):
            if (
                structure[i] == "."
                and depth > 0
                and structure[i - 1] == ")"
                and structure[i + 1] == "("
            ):
                count += 1
            if structure[i] == "(":
                depth += 1
            elif structure[i] == ")":
                depth -= 1
        return count

    @staticmethod
    def _calculate_asymmetry(structure: str) -> float:
        mid = len(structure) // 2
        left = structure[:mid]
        right_rev = structure[mid:][::-1]
        denominator = min(len(left), len(right_rev))
        if denominator == 0:
            return 0.0
        matches = sum(a == b for a, b in zip(left, right_rev))
        return round(100 - matches / denominator * 100, 1)

    @staticmethod
    def _calculate_complexity(sequence: str) -> float:
        counts = Counter(sequence)
        length = len(sequence)
        entropy = -sum((count / length) * log2(count / length) for count in counts.values())
        return round(entropy, 3)

    @staticmethod
    def _calculate_purine_pyrimidine_ratio(sequence: str) -> float:
        purines = sequence.count("A") + sequence.count("G")
        pyrimidines = sequence.count("C") + sequence.count("T")
        return round(purines / (pyrimidines + 1e-10), 2)

    @staticmethod
    def _estimate_stability(structure: str, sequence: str) -> Tuple[float, int, int, int]:
        """Heuristic pair-weight stability score; it is not a thermodynamic ΔG calculation."""
        gc_pairs = 0
        at_pairs = 0
        stack: List[int] = []

        for i, char in enumerate(structure):
            if char == "(":
                stack.append(i)
            elif char == ")" and stack:
                j = stack.pop()
                pair = (sequence[j], sequence[i])
                if pair in (("G", "C"), ("C", "G")):
                    gc_pairs += 1
                elif pair in (("A", "T"), ("T", "A")):
                    at_pairs += 1

        total_pairs = gc_pairs + at_pairs
        score = -(gc_pairs * 3.0 + at_pairs * 2.0)
        return round(score, 1), gc_pairs, at_pairs, total_pairs

    def create_analysis_report(self, structure: str, sequence: str, analysis: Dict[str, float]) -> str:
        return f"""# NanoMax Asymmetric DNA Aptamer Analysis

## Sequence
- DNA sequence: {sequence}
- Length: {int(analysis['length'])} nucleotides
- Dot-bracket structure: {structure}

## Composition
- GC content: {analysis['gc_content']:.1f}%
- A: {analysis['A_percent']:.1f}%
- C: {analysis['C_percent']:.1f}%
- G: {analysis['G_percent']:.1f}%
- T: {analysis['T_percent']:.1f}%

## Structural descriptors
- Paired bases: {int(analysis['paired_bases'])} ({analysis['pairing_percent']:.1f}%)
- Unpaired bases: {int(analysis['unpaired_bases'])}
- Hairpin loops: {int(analysis['hairpins'])}
- Bulges: {int(analysis['bulges'])}
- Internal loops: {int(analysis['internal_loops'])}
- Branch points: {int(analysis['branches'])}
- Asymmetry score: {analysis['asymmetry_score']:.1f}%

## Sequence descriptors
- Shannon entropy: {analysis['sequence_complexity']:.3f}
- Purine:pyrimidine ratio: {analysis['purine_pyrimidine_ratio']:.2f}
- GC pairs: {int(analysis['gc_pairs'])}
- AT pairs: {int(analysis['at_pairs'])}
- Heuristic stability score: {analysis['stability_score']:.1f}

> Note: the stability score is a heuristic pair-weight score, not a predicted thermodynamic free energy (ΔG). Experimental and/or validated folding-tool confirmation is required before biological conclusions.
"""
