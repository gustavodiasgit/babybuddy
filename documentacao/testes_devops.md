# Testes de Aceitação com Cypress

Como parte do trabalho, foram desenvolvidos testes de aceitação utilizando o **Cypress**.

Esses testes simulam ações realizadas por um usuário real no navegador, verificando se as principais funcionalidades da interface estão disponíveis e funcionando corretamente.

Diferentemente de testes unitários, que analisam funções ou classes isoladamente, os testes de aceitação validam o comportamento completo da aplicação, incluindo a interação entre páginas, formulários, botões, rotas e banco de dados.

---

# Objetivo

O objetivo dos testes foi validar três fluxos importantes do BabyBuddy:

- autenticação do usuário pela tela de login;
- acesso à funcionalidade de adicionar uma soneca;
- acesso à funcionalidade de adicionar uma alimentação.

Esses cenários foram escolhidos porque representam operações essenciais para o uso da aplicação.

---

# Testes Implementados

## Teste 1 – Funcionamento da tela de login

O primeiro teste verifica se o usuário consegue utilizar corretamente a tela de login do BabyBuddy.

O Cypress acessa a página de autenticação, localiza os campos do formulário, preenche as credenciais necessárias e realiza o envio.

Esse teste serve para validar:

- se a página de login pode ser acessada;
- se os campos do formulário estão disponíveis;
- se o usuário consegue preencher suas credenciais;
- se o botão de login executa a ação esperada;
- se, após uma autenticação válida, o usuário é direcionado para uma área autenticada da aplicação.

Esse cenário é importante porque a autenticação é o ponto de entrada para as funcionalidades protegidas do sistema. Caso o login deixe de funcionar, o usuário não conseguirá acessar os registros e recursos do BabyBuddy.

O teste também ajuda a detectar regressões relacionadas a alterações em:

- rotas de autenticação;
- nomes e identificadores dos campos;
- estrutura HTML do formulário;
- redirecionamento após o login;
- configuração de sessão.

---

## Teste 2 – Funcionamento do botão de adicionar soneca

O segundo teste verifica se o botão utilizado para adicionar uma soneca está disponível e conduz o usuário ao fluxo correto.

Após realizar o login e acessar a área correspondente, o Cypress localiza o botão de adicionar soneca e executa o clique.

Esse teste serve para validar:

- se o botão de adicionar soneca está visível para o usuário;
- se o elemento pode ser clicado;
- se o clique abre a página ou o formulário esperado;
- se a rota relacionada ao registro de sono está funcionando;
- se a funcionalidade está acessível pela interface.

O registro de sonecas é uma das funcionalidades centrais do BabyBuddy. Por isso, é importante garantir que o usuário consiga iniciar esse fluxo sem precisar acessar diretamente uma URL ou utilizar métodos alternativos.

Esse teste pode detectar regressões causadas por mudanças em:

- menus e botões de acesso rápido;
- links e rotas;
- permissões;
- templates;
- identificadores utilizados pelos elementos da interface;
- comportamento de navegação.

---

## Teste 3 – Funcionamento do botão de adicionar alimentação

O terceiro teste verifica se o botão utilizado para adicionar uma alimentação está disponível e executa corretamente a navegação esperada.

Após acessar a aplicação como um usuário autenticado, o Cypress identifica o botão de alimentação e realiza o clique.

Esse teste serve para validar:

- se o botão de adicionar alimentação é exibido;
- se o botão está habilitado e pode ser utilizado;
- se o clique direciona o usuário para a página ou formulário correto;
- se a rota de criação de uma alimentação está funcionando;
- se o fluxo de registro de alimentação pode ser iniciado pela interface.

O registro de alimentação também é uma funcionalidade essencial do BabyBuddy. Uma falha nesse botão poderia impedir o usuário de registrar mamadas, refeições ou outras informações relacionadas à alimentação da criança.

O teste ajuda a identificar problemas relacionados a:

- alterações na navegação;
- mudanças nos templates;
- links incorretos;
- rotas quebradas;
- elementos removidos ou renomeados;
- restrições de acesso inesperadas.

---

# Estrutura Geral dos Testes

Os testes seguem um fluxo semelhante ao comportamento de um usuário real:

1. O Cypress abre a aplicação no navegador;
2. O usuário é autenticado;
3. A página principal ou área protegida é acessada;
4. O Cypress procura o elemento que representa a funcionalidade;
5. Uma ação de clique ou preenchimento é executada;
6. O resultado da ação é verificado.

Para os testes de soneca e alimentação, o login funciona como uma etapa de preparação, pois essas funcionalidades só podem ser acessadas por usuários autenticados.

---

# Benefícios

A utilização do Cypress nesses cenários oferece os seguintes benefícios:

- validação automática das principais ações da interface;
- simulação do comportamento real do usuário;
- identificação de problemas em botões, links e formulários;
- detecção de regressões após mudanças nos templates;
- verificação da integração entre autenticação, navegação e rotas;
- redução da necessidade de repetir testes manuais;
- maior segurança durante refatorações.

---

# Resultado

Os testes implementados confirmam que o usuário consegue:

- acessar e utilizar a tela de login;
- iniciar o fluxo de adição de uma soneca;
- iniciar o fluxo de adição de uma alimentação.

Dessa forma, os testes verificam três pontos fundamentais da experiência de uso do BabyBuddy: autenticação, registro de sono e registro de alimentação.

Além de validar o comportamento atual, esses testes passam a funcionar como uma proteção contra regressões. Caso uma alteração futura quebre algum desses fluxos, o Cypress poderá identificar o problema antes que a mudança seja integrada ao projeto.
