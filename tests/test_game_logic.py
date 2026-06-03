import unittest

from src.game_logic import (
    build_mentor_context,
    calculate_boss_damage,
    calculate_player_damage,
    calculate_question_elo,
    calculate_xp_gain,
    choose_next_question,
    derive_level,
)


class GameLogicTest(unittest.TestCase):
    def test_player_damage_respects_formula_and_minimum(self):
        damage = calculate_player_damage(
            difficulty=3,
            streak=2,
            answered_seconds=45,
            hint_level=1,
            wrong_attempts=1,
        )

        self.assertEqual(damage, 38)
        self.assertEqual(
            calculate_player_damage(
                difficulty=1,
                streak=0,
                answered_seconds=120,
                hint_level=5,
                wrong_attempts=5,
            ),
            5,
        )

    def test_boss_damage_uses_repeated_error_penalty(self):
        self.assertEqual(
            calculate_boss_damage(difficulty=2, previous_skill_errors=0),
            20,
        )
        self.assertEqual(
            calculate_boss_damage(difficulty=2, previous_skill_errors=1),
            25,
        )
        self.assertEqual(
            calculate_boss_damage(difficulty=2, previous_skill_errors=3),
            30,
        )

    def test_xp_gain_applies_first_try_no_hint_and_hint_penalties(self):
        self.assertEqual(
            calculate_xp_gain(difficulty=2, first_try=True, hint_level=0, phase_bonus=0),
            50,
        )
        self.assertEqual(
            calculate_xp_gain(difficulty=2, first_try=False, hint_level=3, phase_bonus=30),
            35,
        )
        self.assertEqual(
            calculate_xp_gain(difficulty=1, first_try=False, hint_level=5, phase_bonus=0),
            0,
        )

    def test_elo_changes_by_question_rating(self):
        won = calculate_question_elo(player_elo=1000, difficulty=3, is_correct=True)
        lost = calculate_question_elo(player_elo=1000, difficulty=3, is_correct=False)

        self.assertGreater(won, 1000)
        self.assertLess(lost, 1000)
        self.assertEqual(calculate_question_elo(1000, 3, True), 1018)
        self.assertEqual(calculate_question_elo(1000, 3, False), 994)

    def test_level_is_based_on_total_xp(self):
        self.assertEqual(derive_level(0), 1)
        self.assertEqual(derive_level(249), 1)
        self.assertEqual(derive_level(250), 2)
        self.assertEqual(derive_level(625), 3)

    def test_choose_next_question_prioritizes_repeated_weak_skill(self):
        questions = [
            {"id": "A", "skill_tag": "massa_para_mol", "difficulty": 1},
            {"id": "B", "skill_tag": "reagente_limitante", "difficulty": 2},
            {"id": "C", "skill_tag": "reagente_limitante", "difficulty": 3},
        ]

        chosen = choose_next_question(
            questions=questions,
            asked_question_ids=[],
            recent_errors=[{"skill_tag": "reagente_limitante"}, {"skill_tag": "reagente_limitante"}],
            correct_streak=0,
            wrong_streak=0,
            current_difficulty=2,
        )

        self.assertEqual(chosen["skill_tag"], "reagente_limitante")
        self.assertEqual(chosen["difficulty"], 2)

    def test_choose_next_question_raises_difficulty_after_three_correct(self):
        questions = [
            {"id": "A", "skill_tag": "massa_para_mol", "difficulty": 2},
            {"id": "B", "skill_tag": "massa_para_mol", "difficulty": 3},
        ]

        chosen = choose_next_question(
            questions=questions,
            asked_question_ids=[],
            recent_errors=[],
            correct_streak=3,
            wrong_streak=0,
            current_difficulty=2,
        )

        self.assertEqual(chosen["difficulty"], 3)

    def test_mentor_context_never_contains_answer_or_explanation(self):
        question = {
            "id": "QX",
            "topic": "Estequiometria",
            "skill_tag": "reagente_limitante",
            "difficulty": 3,
            "stem": "Texto da questao",
            "correct_option": "D",
            "explanation": "Resolucao completa",
            "options": {"A": "1", "D": "4"},
            "hints": {"2": "Compare em mol."},
        }

        context = build_mentor_context(
            question=question,
            selected_option="A",
            error_type="proporção",
            hint_level=2,
            skill_error_count=2,
        )

        self.assertEqual(context["allowed_hint"], "Compare em mol.")
        forbidden = str(context)
        self.assertNotIn("correct_option", forbidden)
        self.assertNotIn("Resolucao completa", forbidden)
        self.assertNotIn("'D'", forbidden)


if __name__ == "__main__":
    unittest.main()
