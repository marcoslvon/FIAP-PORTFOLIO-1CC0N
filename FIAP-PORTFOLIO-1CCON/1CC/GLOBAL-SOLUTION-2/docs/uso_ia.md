# Uso de Inteligência Artificial no projeto

Conforme permitido pelo enunciado da Global Solution 2026.2, ferramentas de Inteligência Artificial foram utilizadas como apoio ao desenvolvimento deste projeto. Este documento registra **como** a IA foi usada e **como os resultados foram verificados**.

## Ferramenta utilizada

- **Claude (Anthropic)** — apoio em pesquisa, organização de ideias, geração de dados fictícios e revisão da documentação.

## Em que a IA apoiou

| Etapa | Como a IA apoiou | Como o resultado foi verificado |
|---|---|---|
| Definição do cenário | Sugestão do bairro fictício, das localidades genéricas e dos tipos de problema de cada categoria | O cenário foi conferido contra os requisitos do enunciado: quatro categorias obrigatórias, localidades genéricas e ausência de dados pessoais |
| Geração dos dados simulados | Criação das 16 ocorrências do arquivo CSV, incluindo os dois registros com problema proposital | Conferi manualmente a distribuição: 14 registros válidos, as quatro categorias presentes, as três situações presentes e os dois registros defeituosos sendo recusados pela validação ao rodar o sistema |
| Estruturação do código | Discussão de qual estrutura de dados usar em cada necessidade (lista, fila, pilha, dicionário, hierarquia e matriz) | Cada estrutura foi testada em execução: a fila foi conferida retirando o primeiro elemento, a pilha conferindo se a última alteração aparece no topo e a matriz somando linhas e colunas |
| Revisão da documentação | Organização do README nos tópicos pedidos e revisão de texto | Todos os números citados no README foram comparados com a saída real do programa |
| Conferência dos cálculos | Explicação das fórmulas de percentual e de tempo médio | Os cálculos foram refeitos à mão: `(7 + 5 + 6 + 5) ÷ 4 = 5,75`, arredondado para 5,8 dias, resultado idêntico ao exibido pelo sistema |

## Verificação dos resultados

Todo o sistema foi executado antes da entrega e as seguintes verificações foram feitas:

1. **Execução completa sem erros**, tanto pelo menu quanto pela demonstração automática (opção 11);
2. **Validação funcionando**: os registros `OC-015` (categoria ausente) e `OC-016` (situação `finalizada`, inexistente) são recusados e aparecem no painel com o motivo;
3. **Cadastro recusando entradas inválidas**: testado com categoria em branco e com categoria inexistente (`transito`);
4. **Atualização recusando situação desconhecida e código inexistente**, com mensagens diferentes para cada caso;
5. **Conferência aritmética dos indicadores**: a matriz categoria × situação fecha nas linhas (4+3+4+3 = 14) e nas colunas (6+4+4 = 14), e o tempo médio foi recalculado manualmente;
6. **Execução a partir de pastas diferentes** (raiz do projeto e pasta `src/`), para garantir que o arquivo de dados é encontrado nos dois casos.

## Decisões que foram tomadas pela equipe

As escolhas abaixo foram definidas e justificadas no README, não copiadas de uma sugestão automática:

- Quais estruturas de dados usar para cada finalidade e por quê;
- Quais campos são obrigatórios e qual expressão booleana valida um registro;
- O critério de padronizar categorias e situações sem acento internamente, exibindo nomes formatados na tela;
- A decisão de **não ter campos de dados pessoais** no sistema, por privacidade;
- A decisão de tratar **acessibilidade como categoria própria**, para que esse tipo de demanda não desapareça nas estatísticas;
- A interpretação dos indicadores, incluindo a observação de que conservação é a única categoria sem nenhuma demanda concluída.
