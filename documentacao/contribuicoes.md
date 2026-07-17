# Issue escolhida: 

https://github.com/babybuddy/babybuddy/issues/942

## Resolução da Issue #942

## Problema observado

Foi identificado um bug relatado por outro usuário no qual, ao cadastrar uma soneca que se iniciava em um dia e terminava no dia seguinte (por exemplo, **13/04/2026 23:50:00** até **14/04/2026 01:20:00**), a timeline exibia apenas a data de início da atividade, dando a impressão de que a criança havia iniciado e finalizado a soneca no mesmo dia.

Esse comportamento fazia com que eventos com duração atravessando a meia-noite fossem apresentados de forma incorreta, comprometendo a visualização cronológica das atividades.

---

![Bug](imagens/bug.png)

## Solução

A solução implementada consistiu em tornar a lógica de consulta e montagem da timeline mais robusta, permitindo tratar corretamente eventos cuja duração abrange mais de um dia.

### Utilização do objeto `Q`

Inicialmente, foi importado o objeto `Q` do Django ORM.

O objeto `Q` permite criar consultas mais complexas utilizando operadores lógicos como:

- **AND (`&`)**
- **OR (`|`)**
- **NOT (`~`)**

Com isso, foi possível modificar as consultas para que retornassem atividades cujo horário de **início** ou **término** estivesse dentro do período correspondente ao dia exibido na timeline.

---

### Função `_is_in_range`

Também foi criada a função auxiliar `_is_in_range`.

Sua responsabilidade é verificar se um determinado horário pertence ao intervalo correspondente ao dia atualmente exibido na timeline.

Por exemplo:

```text
Data exibida:
13/04/2026

min_date = 13/04/2026 00:00:00
max_date = 13/04/2026 23:59:59

start = 13/04/2026 23:50:00
end   = 14/04/2026 01:20:00
```

Nesse cenário:

- `_is_in_range(start)` retorna **True**;
- `_is_in_range(end)` retorna **False**.

Como consequência, apenas o evento de início será exibido na timeline do dia **13/04**, enquanto o evento de término será apresentado na timeline do dia **14/04**.

---

### Função `_duration_instances_for_day`

Outra melhoria foi a criação da função `_duration_instances_for_day`.

Essa função é responsável por organizar cronologicamente os eventos com duração registrados na timeline, ordenando-os por horário e pela criança associada ao registro.

Essa organização facilita a exibição correta dos eventos e evita inconsistências durante a construção da timeline diária.

---

## Alterações na classe `TummyTime`

A lógica da classe **TummyTime** também foi modificada.

Antes da correção, tanto o horário de início quanto o horário de término eram adicionados à timeline sem verificar se cada um realmente pertencia ao dia exibido.

Após a alteração, cada horário é validado individualmente utilizando a função `_is_in_range`.

Assim:

- se apenas o início ocorreu no dia atual, somente ele será exibido;
- se o término ocorrer apenas no dia seguinte, ele aparecerá apenas na timeline desse outro dia.

Essa mudança garante que cada evento seja exibido exatamente no dia em que ocorreu.

---

## Alterações nas classes `Sleep` e `Feeding`

A mesma lógica aplicada em **TummyTime** foi implementada nas classes **Sleep** e **Feeding**.

As consultas passaram a utilizar a função `_is_in_range` para validar individualmente os horários de início e término de cada atividade.

Com isso, eventos que atravessam a meia-noite passaram a ser representados corretamente, eliminando a inconsistência observada na issue #942.

---

# Resultado

Após a implementação das alterações:

- eventos com duração passaram a ser exibidos corretamente na timeline;
- atividades iniciadas em um dia e finalizadas no seguinte deixaram de aparecer integralmente em apenas um dos dias;
- a ordenação cronológica dos eventos tornou-se consistente;
- a visualização da timeline passou a refletir corretamente a ocorrência real das atividades.

A correção resolveu o problema relatado na **issue #942** e tornou a lógica de construção da timeline mais robusta para cenários envolvendo eventos com duração distribuída entre dias diferentes.

![Solução:](imagens/solucao1.png)
![Solução:](imagens/solucao2.png)
![Código:](imagens/codigo.png)
