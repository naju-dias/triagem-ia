import json
import sys
import time

import requests

URL = "http://127.0.0.1:8000/mensagens"
PAUSA = 15            # segundos entre mensagens (limite do nível gratuito)
TENTATIVAS = 3        # quantas vezes repetir uma mensagem que falhar
VERSAO = sys.argv[1] if len(sys.argv) > 1 else "v1"   # ex.: python scripts/rodar_exemplos.py v2

ARQUIVO = sys.argv[2] if len(sys.argv) > 2 else "data/mensagens_exemplo.json"

with open(ARQUIVO, encoding="utf-8") as f:
    exemplos = json.load(f)

acertos, processadas = 0, 0
falhas, erros, resultados = [], [], []

for i, ex in enumerate(exemplos, 1):
    res = None
    for tentativa in range(TENTATIVAS):
        try:
            r = requests.post(URL, json={"texto": ex["texto"]}, timeout=180)
            r.raise_for_status()
            res = r.json()
            break
        except Exception as e:
            print(f"{i:02d} tentativa {tentativa + 1} falhou: {e}")
            time.sleep(30)

    if res is None:
        falhas.append(i)
        continue

    processadas += 1
    ok = res["categoria"] == ex["esperado"]
    acertos += ok
    print(f"{i:02d} {'OK ' if ok else 'XX '} esperado={ex['esperado']:<12} "
          f"obtido={res['categoria']:<12} conf={res['confianca']:.2f}")

    resultados.append({
        "n": i,
        "texto": ex["texto"],
        "esperado": ex["esperado"],
        "obtido": res["categoria"],
        "confianca": res["confianca"],
        "acertou": ok,
    })
    if not ok:
        erros.append((ex["texto"], ex["esperado"], res["categoria"]))

    time.sleep(PAUSA)

print(f"\nProcessadas: {processadas}/{len(exemplos)} | Falhas: {len(falhas)} {falhas}")
if processadas:
    print(f"Acerto (sobre as processadas): {acertos}/{processadas} = {acertos / processadas:.0%}")
for t, e, o in erros:
    print(f"- '{t}': esperado {e}, obtido {o}")

# Guarda o resultado para comparar versões do prompt
with open(f"data/resultado_{VERSAO}.json", "w", encoding="utf-8") as f:
    json.dump(
        {"versao": VERSAO, "processadas": processadas, "falhas": falhas,
         "acertos": acertos, "resultados": resultados},
        f, ensure_ascii=False, indent=2,
    )
print(f"\nSalvo em data/resultado_{VERSAO}.json")