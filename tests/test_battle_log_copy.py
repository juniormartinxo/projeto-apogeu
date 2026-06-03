import unittest

from app import format_accuracy_log, format_error_log, format_hint_log
from src.ui_components import _skill_label


class BattleLogCopyTest(unittest.TestCase):
    def test_hint_log_uses_human_copy_instead_of_raw_skill_tag(self):
        question = {"id": "Q001", "skill_tag": "massa_para_mol", "topic": "Mol e massa molar"}

        text = format_hint_log(question, 1)

        self.assertEqual(text, "Vetor entrou no canal: foco em conversão de massa para mol.")
        self.assertNotIn("massa_para_mol", text)
        self.assertNotIn("Dica nivel", text)

    def test_question_skill_label_is_human_readable(self):
        self.assertEqual(_skill_label("massa_para_mol"), "conversão de massa para mol")
        self.assertEqual(_skill_label("reagente_limitante"), "reagente limitante")

    def test_accuracy_and_error_logs_read_like_combat_events(self):
        question = {"id": "Q007", "skill_tag": "reagente_limitante", "topic": "Estequiometria"}

        hit = format_accuracy_log(question, damage_done=34, xp_gain=25)
        miss = format_error_log(question, damage_taken=20)

        self.assertEqual(hit, "Ataque confirmado em Q007: 34 de dano aplicado, 25 XP recuperados.")
        self.assertEqual(miss, "Molock contra-atacou em Q007: 20 de dano recebido. Falha provável em reagente limitante.")
        self.assertNotIn("reagente_limitante", miss)


if __name__ == "__main__":
    unittest.main()

