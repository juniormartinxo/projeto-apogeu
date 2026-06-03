# Protocolo Apogeu

MVP local de preparação para ITA/IME em Química Quantitativa. O jogo roda com Streamlit, persiste progresso em SQLite e usa Ollama local apenas se estiver disponível.

## Como rodar

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

Em Linux/macOS:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Ollama local opcional

Por padrão, o app tenta chamar:

```text
http://localhost:11434/api/chat
```

Modelo padrão:

```text
gpt-oss:20b
```

Para trocar o modelo:

```powershell
$env:OLLAMA_MODEL="llama3.1:8b"
streamlit run app.py
```

Se o Ollama estiver desligado ou inacessível, o jogo continua funcionando com dicas e provocações determinísticas pré-cadastradas.

Para forçar o fallback:

```powershell
$env:APOGEU_DISABLE_OLLAMA="1"
streamlit run app.py
```

## O que está pronto no MVP

- Campanha curta de Química Quantitativa com 3 fases.
- Batalha com HP do jogador, HP de Molock, dano, XP, nível e ELO.
- IA inimiga adaptativa para escolher questões por fraqueza, sequência de acertos ou sequência de erros.
- Mentor Vetor com 5 níveis de ajuda.
- Regra anti-cola: o contexto enviado ao Mentor durante a tentativa não inclui gabarito, alternativa correta, valor final nem explicação completa.
- Caderno de erros persistente com tipo de erro, inimigo gerado, fraqueza e revisão.
- Painel de evolução com acertos por skill, erros por tipo e tentativas recentes.
- Banco SQLite criado automaticamente em `data/apogeu.db`.
- Seed automático com 18 questões originais em `data/seed_questions.json`.

## Testes

```powershell
python -m unittest tests.test_game_logic
```

## Estrutura

```text
app.py
requirements.txt
README.md
data/seed_questions.json
src/db.py
src/game_logic.py
src/ollama_client.py
src/prompts.py
src/ui_components.py
src/seed.py
tests/test_game_logic.py
```
