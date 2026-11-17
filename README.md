# CROMMA ATELIER SYSTEM — MVP acadêmico

Projeto de Software (UNIFRAN). Aplicação demonstrativa em Flask + SQLite. **Não contém dados reais da CROMMA ATELIER e não é um sistema de produção.**

## Como executar (Windows / PowerShell)

1. Baixe o ZIP deste repositório no botão **Code > Download ZIP** e extraia em uma pasta.
2. Abra o PowerShell nessa pasta.
3. Execute:

```powershell
py -m pip install -r requirements.txt
py app.py
```

4. Abra **http://127.0.0.1:5000/** no navegador.

Se o comando `py` não funcionar, instale o Python 3.12 ou substitua `py` por `python`.

## Demonstração para a faculdade

A tela cria automaticamente dois registros **fictícios**, na primeira abertura:

- Quadro Decorativo Abstrato 90 × 60 cm, SKU **DEMO-QD001**, saldo inicial **15 unidades**;
- Moldura preta 60 × 40 cm, SKU **DEMO-MAT001**, saldo inicial **8 unidades**.

Para demonstrar um fluxo: selecione DEMO-QD001, escolha **Saída**, digite **3**, confirme. A interface mostra **“Saída registrada com sucesso!”**, o novo saldo **12** e a tabela atualizada. Tire a captura **do navegador com a aplicação realmente em execução**. Se o banco já existir, os saldos serão preservados e podem não começar em 15.

Para voltar aos saldos fictícios iniciais: interrompa o servidor e exclua apenas o arquivo local `mvp.sqlite3`; na próxima execução, os dados demonstrativos serão criados novamente.

## Acessibilidade demonstrativa

- Navegação por teclado e foco visível;
- Rótulos associados aos campos;
- Mensagens textuais de sucesso/erro com `role="alert"`, além das cores;
- Layout adaptável para celular;
- Botões e opções com áreas de toque amplas.

Esses recursos apoiam o **ODS 8, meta 8.3**, por facilitar o acesso de pequenos empreendimentos a ferramentas digitais. A aplicação ainda **não implementa autenticação e autorização**, portanto deve ser executada somente localmente, para fins acadêmicos.

## Testes

```powershell
py -m unittest discover -s tests -v
```

O GitHub Actions executa testes e cobertura automaticamente em alterações na branch principal.
