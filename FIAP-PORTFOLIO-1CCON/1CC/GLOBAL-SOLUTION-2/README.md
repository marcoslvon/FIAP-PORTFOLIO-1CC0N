# Neighborhood Action Dashboard

**Global Solution 2026.2 — FIAP | Case CitizenTech**
Painel comunitário para registrar, organizar e acompanhar demandas de melhoria de um bairro.

---

## 1. Identificação

| Marco Silveira | 576740 |

---

## 2. Comunidade simulada, problema e público beneficiado

**Bairro simulado:** Jardim das Acácias — um bairro fictício de porte médio, com praça, parque, quadra esportiva, escola, posto de saúde e um terminal de ônibus. Todos os dados deste projeto são **inventados**; nenhum morador real, endereço exato ou informação pessoal é utilizado.

**O problema:** demandas simples do dia a dia — um poste apagado, uma calçada quebrada, lixo acumulado — costumam ser relatadas por caminhos dispersos (grupos de mensagens, conversas, ligações). O resultado é que ninguém sabe ao certo quantos problemas existem, quais já foram resolvidos e quais estão parados há semanas. A informação existe, mas não está organizada.

**O que o sistema faz:** o Neighborhood Action Dashboard transforma esses relatos em registros padronizados. Ele guarda cada ocorrência com código, categoria, local e situação; organiza a espera por ordem de chegada; guarda o histórico de tudo que mudou; e calcula indicadores que mostram onde estão os problemas mais frequentes e quanto tempo as demandas levam para serem concluídas.

**Público beneficiado:**
- **Moradores**, que passam a consultar a situação de uma demanda pelo código, em vez de perguntar a alguém;
- **Associações de bairro e lideranças comunitárias**, que ganham números concretos para organizar mutirões e embasar conversas com o poder público;
- **Pessoas com deficiência e mobilidade reduzida**, porque acessibilidade é uma categoria própria no sistema e deixa de ficar diluída em "outros".

**Limite importante:** este é um protótipo acadêmico. Ele **não se conecta a prefeituras nem a nenhum serviço público**, e registrar uma ocorrência aqui não gera obrigação de atendimento por parte de ninguém.

---

## 3. Dados simulados e formato do arquivo

Os dados ficam em `dados/ocorrencias.csv`, um arquivo de texto simples. Escolhemos **ponto e vírgula (`;`)** como separador porque as descrições podem conter vírgulas, o que quebraria a separação das colunas.

**Formato de cada linha:**

```
id;categoria;descricao;local;dia_abertura;status;dia_conclusao
OC-001;iluminacao;Poste apagado em frente ao coreto;Praça Central;2;concluida;9
```

**Campos da ocorrência:**

| Campo | Obrigatório | Descrição |
|---|---|---|
| `id` | Sim | Código único no formato OC-000 |
| `categoria` | Sim | Uma das quatro categorias padronizadas |
| `descricao` | Sim | Texto curto explicando o problema |
| `local` | Sim | Localidade **genérica** (praça, rua, parque) — nunca endereço exato |
| `dia_abertura` | Sim | Dia simulado do registro (número de 1 a 30) |
| `status` | Sim | Uma das três situações padronizadas |
| `dia_conclusao` | Não | Dia em que foi concluída; fica vazio enquanto não for |

**Valores padronizados.** Dentro do sistema, categorias e situações são sempre escritas em minúsculas e sem acento (`iluminacao`, `em_analise`). Isso evita que "Iluminação", "iluminacao" e "ILUMINACAO" virem três categorias diferentes. Na tela, os dicionários `NOME_CATEGORIA` e `NOME_SITUACAO` convertem esses códigos para a forma bonita ("Iluminação", "Em análise").

**Categorias:** `iluminacao`, `acessibilidade`, `limpeza`, `conservacao`

**Situações e seus significados:**

| Situação | Significado |
|---|---|
| `aberta` | Registrada pelo morador e ainda não examinada pela equipe |
| `em_analise` | Já passou pela triagem e está sendo avaliada |
| `concluida` | Demanda encerrada no painel da comunidade |

**Conteúdo do pacote de dados:**
- **16 linhas** de ocorrências, sendo **14 válidas** distribuídas entre as quatro categorias;
- **2 registros com problema proposital**, para demonstrar a validação:
  - `OC-015` — **categoria ausente** (campo vazio);
  - `OC-016` — **situação inconsistente** (`finalizada`, que não existe no sistema);
- **12 eventos de histórico** simulados (o mínimo exigido era 8), carregados na pilha ao iniciar o programa.

Os dois registros com problema são **recusados na entrada** e aparecem no painel com o motivo da recusa, em vez de serem apagados em silêncio.

---

## 4. Estruturas de dados utilizadas e justificativa

| Estrutura | Onde está no código | Para que serve | Por que essa escolha |
|---|---|---|---|
| **Lista** | `ocorrencias` | Guarda todas as ocorrências válidas | É a estrutura natural para percorrer tudo com um `for`, como nas listagens e nos filtros. Mantém a ordem de registro |
| **Dicionário** | `indice_por_id` | Acha uma ocorrência direto pelo código | Buscar `"OC-003"` na lista exigiria percorrer item por item. No dicionário o acesso é direto, como procurar uma palavra pela letra no dicionário em vez de ler o livro inteiro |
| **Fila (FIFO)** | `fila_analise` | Ocorrências abertas esperando a primeira análise | A fila é justa por natureza: quem registrou primeiro é atendido primeiro. Entra no fim (`append`) e sai do começo (posição 0) |
| **Pilha (LIFO)** | `pilha_historico` | Histórico de todas as mudanças de situação | O que interessa no histórico é "o que mudou por último". A pilha coloca sempre o evento mais recente no topo, então basta ler de trás para frente |
| **Dicionário aninhado (hierarquia)** | `montar_hierarquia()` | Organiza bairro → categoria → ocorrências | Permite enxergar o bairro por partes. Em vez de uma lista solta de 14 itens, o gestor vê quantas demandas existem em cada categoria e quais são elas |
| **Matriz (lista de listas)** | `montar_matriz_categoria_situacao()` | Quantidade por categoria **e** situação | Cruza duas informações ao mesmo tempo: cada **linha** é uma categoria e cada **coluna** é uma situação. É o que mostra, por exemplo, que conservação tem demandas abertas mas nenhuma concluída |

**Como a hierarquia ajuda:** olhando só a lista, "14 ocorrências" é um número sem significado. Na hierarquia, vê-se que Iluminação tem 4 e Conservação tem 3, e quais são elas. A organização por níveis transforma uma lista em um diagnóstico do bairro.

---

## 5. Regras lógicas principais

### 5.1 Expressão booleana da validação

Esta é a expressão que decide se um registro pode entrar no sistema (função `validar_registro`):

```python
registro_valido = ((id_oc != "")
                   and (categoria in CATEGORIAS)
                   and (situacao in SITUACOES)
                   and dia_texto.isdigit()
                   and not (local == "" or descricao == ""))
```

**Como ela funciona:** os `and` exigem que **todas** as condições sejam verdadeiras ao mesmo tempo — basta uma falhar para o registro ser recusado. A última parte usa `or` dentro de um `not`: `(local == "" or descricao == "")` é verdadeiro quando **pelo menos um** dos dois está vazio, e o `not` inverte isso, exigindo que **nenhum** deles esteja vazio.

| Trecho | O que exige |
|---|---|
| `id_oc != ""` | O código não pode estar em branco |
| `categoria in CATEGORIAS` | A categoria precisa ser uma das quatro conhecidas |
| `situacao in SITUACOES` | A situação precisa ser uma das três conhecidas |
| `dia_texto.isdigit()` | O dia de abertura precisa ser um número |
| `not (local == "" or descricao == "")` | Nem o local nem a descrição podem estar vazios |

Quando a expressão dá falso, uma cadeia de `if / elif / else` descobre **qual** condição falhou, para que a mensagem seja específica. É por isso que `OC-015` recebe "categoria ausente" e `OC-016` recebe "situação desconhecida (finalizada)", em vez de um genérico "registro inválido".

### 5.2 Outras condições com operadores lógicos

**AND — filtro combinado** (`filtrar_por_categoria_e_situacao`): a ocorrência só entra no resultado se for da categoria pedida **e** estiver na situação pedida.

```python
if ocorrencia["categoria"] == categoria and ocorrencia["status"] == situacao:
```

**NOT — demandas pendentes** (`listar_pendentes`): pendente é tudo que **não** está concluído, o que inclui as abertas e as em análise de uma só vez.

```python
if not (ocorrencia["status"] == "concluida"):
```

**AND + comparação — tempo de conclusão** (`calcular_tempo_medio_conclusao`): só entra na média a ocorrência que está concluída **e** tem o dia de conclusão preenchido, evitando contas erradas com dados incompletos.

```python
if ocorrencia["status"] == "concluida" and ocorrencia["dia_conclusao"] > 0:
```

### 5.3 Regras da atualização de situação

A função `atualizar_situacao` faz três verificações em ordem, e cada uma gera uma mensagem diferente:

| Verificação | Mensagem quando falha | Por quê |
|---|---|---|
| A ocorrência existe? | `ERRO: não existe nenhuma ocorrência com o código OC-999` | Não é possível alterar o que não foi cadastrado |
| A nova situação é conhecida? | `ERRO: situação desconhecida (finalizada)` | Aceitar qualquer texto quebraria os indicadores e a padronização |
| A situação é diferente da atual? | `AVISO: a ocorrência já está na situação Em análise` | Registrar uma mudança que não mudou nada poluiria o histórico |

Só depois de passar pelas três é que a situação muda, a **fila** é ajustada (a ocorrência sai dela ao deixar de estar aberta) e o evento é empilhado no **histórico**.

---

## 6. Indicadores implementados

| Indicador | Fórmula / regra | Resultado inicial |
|---|---|---|
| Total por categoria | Contagem com laço `for` sobre a lista | Iluminação 4, Limpeza 4, Acessibilidade 3, Conservação 3 |
| Proporção por categoria | `(total da categoria / total geral) × 100` | 28,6% / 28,6% / 21,4% / 21,4% |
| Total por situação | Contagem com laço `for` sobre a lista | Aberta 6, Em análise 4, Concluída 4 |
| Proporção por situação | `(total da situação / total geral) × 100` | 42,9% / 28,6% / 28,6% |
| Matriz categoria × situação | Contagem cruzada com laços aninhados e `and` | Ver tabela abaixo |
| **Tempo médio de conclusão** | `soma dos (dia_conclusao − dia_abertura) / nº de concluídas` | **5,8 dias** |
| Demandas pendentes | Contagem de tudo que `not` está concluído | 10 de 14 (71,4%) |

**Matriz categoria × situação (estado inicial):**

| Categoria | Aberta | Em análise | Concluída | Total |
|---|---|---|---|---|
| Iluminação | 1 | 2 | 1 | 4 |
| Acessibilidade | 1 | 1 | 1 | 3 |
| Limpeza | 2 | 0 | 2 | 4 |
| Conservação | 2 | 1 | 0 | 3 |
| **Total** | **6** | **4** | **4** | **14** |

**Cálculo do tempo médio, passo a passo:**

| Ocorrência | Abertura | Conclusão | Dias |
|---|---|---|---|
| OC-001 | dia 2 | dia 9 | 7 |
| OC-006 | dia 7 | dia 12 | 5 |
| OC-011 | dia 14 | dia 20 | 6 |
| OC-014 | dia 18 | dia 23 | 5 |

`(7 + 5 + 6 + 5) ÷ 4 = 23 ÷ 4 = 5,75` → **5,8 dias**

### Interpretação dos resultados

**O que os números dizem sobre o Jardim das Acácias:**

1. **Iluminação e limpeza concentram mais da metade das demandas** (8 das 14, ou 57,2%). São problemas de manutenção recorrente, o que sugere que a comunidade ganharia mais com uma rotina de verificação periódica do que com chamados isolados.

2. **71,4% das demandas ainda não foram concluídas** e 6 delas sequer passaram pela primeira análise. O gargalo do bairro não é registrar problemas — é dar andamento a eles.

3. **A matriz revela um ponto cego:** conservação tem 2 demandas abertas e 1 em análise, mas **nenhuma concluída**. É a única categoria sem nenhum caso resolvido, o que indica onde a comunidade deveria concentrar o próximo esforço. Esse tipo de conclusão só aparece quando se cruzam as duas informações — olhando só o total por categoria, conservação pareceria apenas "a menor categoria".

4. **As demandas que foram concluídas levaram 5,8 dias em média**, um prazo razoável. O problema, portanto, não é a velocidade de resolução, e sim a quantidade de demandas que nunca chegam a ser analisadas.

---

## 7. Como executar

Não é necessário instalar nada além do Python 3. O projeto não usa bibliotecas externas.

A partir desta pasta (`1CC/GLOBAL-SOLUTION-2`):

```bash
python src/sistema.py
```

Ao iniciar, o sistema carrega o arquivo CSV, valida os registros e exibe um menu com 11 opções. A **opção 11 roda uma demonstração automática** que executa, em sequência, todas as funcionalidades do sistema — é a forma mais rápida de ver o projeto funcionando por inteiro.

---

## 8. Exemplos de uso

### 8.1 Listagem

```
CÓDIGO   | CATEGORIA      | LOCAL                  | SITUAÇÃO
--------------------------------------------------------------------------
OC-001   | Iluminação     | Praça Central          | Concluída
OC-002   | Limpeza        | Rua das Palmeiras      | Aberta
OC-003   | Acessibilidade | Posto de Saúde         | Em análise
...
Total exibido: 14 ocorrência(s)
```

### 8.2 Consulta por código

```
>> Procurando a ocorrência OC-003:
Código...........: OC-003
Categoria........: Acessibilidade
Descrição........: Rampa de acesso danificada
Local............: Posto de Saúde
Aberta no dia....: 3
Situação.........: Em análise
  (significado)  : Já passou pela triagem e está sendo avaliada
Em acompanhamento há: 22 dias

>> Procurando um código que não existe (OC-999):
Nenhuma ocorrência encontrada com o código OC-999.
```

### 8.3 Cadastro (válido e recusado)

```
>> Cadastro válido:
CADASTRO REALIZADO com o código OC-017

>> Cadastro inválido (categoria em branco):
CADASTRO RECUSADO: categoria ausente
Campos obrigatórios: id, categoria, descricao, local, dia_abertura, status
Categorias aceitas : iluminacao, acessibilidade, limpeza, conservacao
```

### 8.4 Alteração de situação

```
>> Atualização válida (OC-002 passa para em análise):
ATUALIZADO: OC-002 passou de Aberta para Em análise no dia 25

>> Atualização inválida (situação desconhecida):
ERRO: situação desconhecida (finalizada)
Situações válidas: aberta, em_analise, concluida
```

### 8.5 Fila de análise (ordem de chegada)

```
FILA DE ANÁLISE (ordem de chegada - o primeiro a entrar sai primeiro)
1º | OC-004 | Conservação    | aberta no dia 5
2º | OC-007 | Acessibilidade | aberta no dia 8
3º | OC-008 | Conservação    | aberta no dia 10
...
Próxima a ser analisada: OC-004

>> Atendendo a próxima da fila:
Retirando da fila a ocorrência mais antiga: OC-004
ATUALIZADO: OC-004 passou de Aberta para Em análise no dia 25
```

### 8.6 Histórico (pilha — mais recentes primeiro)

```
dia 25 | OC-004 | Aberta -> Em análise
dia 25 | OC-003 | Em análise -> Concluída
dia 25 | OC-002 | Aberta -> Em análise
dia 23 | OC-014 | Em análise -> Concluída
dia 20 | OC-014 | Aberta -> Em análise
...
```

### 8.7 Hierarquia bairro → categoria → ocorrências

```
Jardim das Acácias
   |- Iluminação (4 ocorrências)
   |     OC-001 - Praça Central - Concluída
   |     OC-005 - Avenida Principal - Em análise
   |     OC-009 - Quadra Esportiva - Em análise
   |     OC-013 - Avenida Principal - Aberta
   |- Acessibilidade (3 ocorrências)
   |     OC-003 - Posto de Saúde - Em análise
   ...
```

---

## 9. Acessibilidade, inclusão e privacidade

**Privacidade**
- Todos os dados são **fictícios**. Nenhum morador real foi consultado e nenhum dado pessoal consentido foi utilizado;
- O sistema **não possui campos** para nome, telefone, e-mail, CPF ou endereço residencial — a ausência desses campos é uma decisão de projeto, não um esquecimento: o que importa para resolver um poste apagado é o local do poste, não quem avisou;
- As localidades são **genéricas e públicas** ("Praça Central", "Parque do Bairro"), nunca endereços exatos que permitiriam identificar a casa de alguém;
- Como consequência, não existe risco de exposição de dados sensíveis caso o repositório seja público.

**Acessibilidade**
- A interface é **puramente textual**, o que a torna compatível com leitores de tela, que leem o terminal linha a linha sem depender de elementos visuais;
- Nenhuma informação é transmitida **apenas por cor ou símbolo**: a situação de cada ocorrência aparece escrita por extenso ("Aberta", "Em análise", "Concluída");
- As mensagens de erro explicam **o que fazer** e não apenas o que deu errado — ao recusar um cadastro, o sistema lista os campos obrigatórios e as categorias aceitas;
- Os textos usam linguagem simples, sem jargão técnico, para que qualquer morador consiga entender a saída.

**Inclusão**
- **Acessibilidade é uma categoria própria** do sistema, no mesmo nível de iluminação e limpeza. Essa escolha é deliberada: quando esse tipo de demanda fica diluído em "outros", ela some das estatísticas e deixa de ser priorizada. Separada, é possível medir quantas barreiras existem no bairro e cobrar a resolução;
- A **fila por ordem de chegada** garante tratamento igual: a demanda de qualquer morador espera o mesmo tanto, sem privilégio de quem tem mais contato ou influência.

---

## 10. Vídeo de apresentação

🔗 **Link do vídeo (YouTube, não listado):** https://youtu.be/n-YXIlLqrBo

---

## 11. Conclusões, limitações e aprendizados

### Conclusões

O protótipo mostra que fundamentos simples de programação já resolvem um problema real de organização comunitária. Com listas, dicionários, filas, pilhas e matrizes, foi possível transformar 16 linhas de texto solto em um diagnóstico do bairro que responde perguntas concretas: qual categoria tem mais problemas, quantas demandas estão paradas, quanto tempo leva uma conclusão e qual categoria nunca teve um caso resolvido.

O ponto mais interessante do resultado foi perceber que **cada estrutura de dados responde a uma pergunta diferente**. A lista responde "quais são todas as ocorrências"; o dicionário responde "como está a OC-003"; a fila responde "quem é o próximo"; a pilha responde "o que mudou por último"; a hierarquia responde "como o bairro está dividido"; e a matriz responde "onde o atendimento está travado". Escolher a estrutura certa não é detalhe técnico — é o que permite extrair cada uma dessas respostas sem complicar o código.

### Limitações

- **Os dados são simulados.** As conclusões valem para o cenário fictício criado e não descrevem nenhum bairro real;
- **O sistema não se integra a órgãos públicos.** Registrar uma ocorrência aqui não aciona nenhuma prefeitura nem gera qualquer promessa de atendimento;
- **Os dados não são salvos.** Cadastros e alterações feitos durante a execução existem apenas na memória: ao fechar o programa, o sistema volta ao conteúdo original do CSV. Gravar as alterações de volta no arquivo seria o próximo passo natural;
- **O tempo é simulado em dias de 1 a 30**, sem meses ou anos, o que simplifica os cálculos mas não serviria para uso real;
- **A busca por categoria e situação é linear**, percorrendo toda a lista. Com 14 registros isso é instantâneo; com dezenas de milhares, seria preciso indexar também por esses campos, como já é feito com o código.

### Aprendizados

- **Validar a entrada é tão importante quanto processar os dados.** Os dois registros defeituosos mostram que, sem validação, uma categoria vazia ou uma situação inventada entrariam no sistema e contaminariam todos os indicadores em silêncio. Recusar o registro **e explicar o motivo** é melhor do que aceitar ou simplesmente descartar;
- **Padronizar valores evita problemas difíceis de achar depois.** Guardar `em_analise` internamente e mostrar "Em análise" na tela separa o dado da aparência, e foi o que permitiu comparar situações com segurança;
- **Cruzar dois dados revela o que cada um sozinho esconde.** A descoberta de que conservação não tem nenhuma demanda concluída só apareceu na matriz;
- **Dividir o programa em funções pequenas facilitou os testes.** Como cadastrar, validar, filtrar e calcular estão em funções separadas, foi possível testar cada parte isoladamente e encontrar erros rapidamente.

---

## 12. Estrutura dos arquivos

Esta entrega fica na pasta `1CC/GLOBAL-SOLUTION-2` do portfólio, seguindo o modelo de organização da coordenação:

```
FIAP-PORTFOLIO-1CCON
└── 1CC
    └── GLOBAL-SOLUTION-2
        ├── README.md                 ← este documento
        ├── src
        │   └── sistema.py            ← o sistema completo
        ├── dados
        │   └── ocorrencias.csv       ← os 16 registros simulados
        └── docs
            └── uso_ia.md             ← documentação do uso de IA
```
