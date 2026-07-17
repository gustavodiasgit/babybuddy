# Padrões e Code Smells

Durante a análise da arquitetura do BabyBuddy, foram identificados três *code smells* na implementação da timeline. Esses problemas afetam a manutenibilidade, legibilidade e evolução do código.

---

# Code Smell 1 – Código duplicado

As funções responsáveis pela criação dos eventos da timeline para **Sleep**, **TummyTime** e **Feeding** repetem grande parte da mesma lógica. Também existe repetição na criação dos eventos de início e fim.

## Problema

Essa duplicação:

- Aumenta o tamanho do arquivo;
- Torna mudanças mais arriscadas;
- Facilita inconsistências;
- Obriga o desenvolvedor a alterar vários trechos para modificar a estrutura de um evento.

Foi exatamente esse tipo de duplicação que contribuiu para o bug da **issue #942**: os eventos de início e fim eram adicionados de forma semelhante, mas sem validação individual consistente.

Esse *code smell* está relacionado ao princípio **DRY (Don't Repeat Yourself)**.

## Possível solução

Extrair uma função responsável pela construção dos eventos, centralizando a lógica comum e reduzindo a duplicação de código.

---

# Code Smell 2 – Função longa e múltiplas responsabilidades

A função `_add_feedings` executa diversas tarefas diferentes:

- Consulta o banco de dados;
- Busca registros do dia anterior;
- Calcula `time_since_prev`;
- Filtra atividades;
- Formata detalhes;
- Cria links;
- Diferencia alimentações pontuais e alimentações com duração;
- Cria eventos de início;
- Cria eventos de término;
- Calcula duração;
- Adiciona os eventos à lista final.

## Problema

Essa função possui baixa coesão e viola o **Single Responsibility Principle (SRP)**.

Uma alteração no cálculo do tempo, na estrutura dos eventos ou na consulta ao banco exige modificar a mesma função.

Isso aumenta:

- Complexidade;
- Dificuldade de leitura;
- Dificuldade de testes;
- Risco de regressões.

## Possível solução

Dividir a implementação em funções menores, deixando uma função principal apenas como coordenadora do fluxo de execução.

Essa abordagem melhora significativamente a legibilidade, manutenção e testabilidade.

---

# Code Smell 3 – Uso excessivo de dicionários não tipados

Os eventos da timeline são representados por dicionários livres (*dict*).

Como consequência, o Python não garante que todos possuam a mesma estrutura.

Isso pode causar problemas como:

- utilização de nomes diferentes para a mesma chave (`event_type` e `type`);
- ausência de campos obrigatórios;
- utilização de tipos incorretos para determinados valores.

Esse *code smell* pode ser classificado como **Primitive Obsession** ou **Data Clump**.

## Possível solução

Utilizar **TypedDict** para definir explicitamente a estrutura esperada dos eventos.

Com isso, torna-se possível:

- definir um contrato para os dicionários;
- facilitar a detecção de erros por ferramentas de análise estática;
- melhorar o suporte oferecido pelos editores de código;
- reduzir inconsistências durante o desenvolvimento.

---

# Padrões de Projeto Aplicados

Como parte da refatoração, foram aplicados dois padrões de projeto para melhorar a organização e a manutenção da implementação da timeline.

## Builder Pattern

O padrão **Builder** foi utilizado para centralizar a criação dos eventos da timeline.

### Benefícios

- Redução da duplicação de código;
- Padronização da estrutura dos eventos;
- Facilidade para manutenção;
- Maior reutilização da lógica de construção.

---

## Strategy Pattern

O padrão **Strategy** foi utilizado para separar a lógica de processamento de cada tipo de evento da timeline.

Cada estratégia passou a encapsular o comportamento específico de um tipo de atividade.

### Benefícios

- Redução das responsabilidades concentradas em uma única função;
- Maior coesão;
- Facilidade para adicionar novos tipos de eventos;
- Melhor aderência ao princípio **Open/Closed**.

---

# Resultado da Refatoração

A aplicação dos padrões Builder e Strategy permitiu:

- reduzir a duplicação de código;
- melhorar a organização da lógica da timeline;
- facilitar testes e manutenção;
- aumentar a legibilidade do código;
- tornar a implementação mais extensível para futuras funcionalidades.
