# Лабораторная работа по АК №3

## Вариант 
####  alg | acc | harv | hw | instr | struct | stream | port | prob2

## Язык программирования

### Синтаксис языка 
Синтаксис языка  в форме Бэкуса — Наура :
``` ebnf
<program> ::= expression
            | statement
expression expression : expression '+' factor
                      | expression '-' factor
                      | expression '/' factor
                      | expression '*' factor
                      | expression '^' factor
                      | expression '%' factor
                      | -expression
                      | factor
factor     : NUM
           | float
           | ( expression )

statement :  let_statement
            | while_statement
            | assign_statement
            | print_statement
            | read_statement
            | line_statement

let_statement::= id ":=" expression ";"
while_statement::=<while> (condition) {stmt} ";"
assign_statement::=<name> "=" <expression> ";"
print_statement::="print" value ";"
read_statement::="read" value ";"
line_statement::="line" value ";"               

```

### Операции

- `+` Функция сложения, суммирует все параметры, возвращает результат
- `-` Функция вычитания, вычитает из первого параметра все остальные, возвращает результат
- `*` Функция умножения, умножает все параметры, возвращает результат
- `/` Функция деления, делит первый параметр на следующий и так далее, возвращает результат
- `%` Данная функция принимает два аргумента, возвращает остаток от деления первого аргумента на второй
- `let` Функция объявления переменной, принимает на вход "имя переменной" "значение"
- `=` Функция изменения значения существующей переменной, принимает на вход "имя переменной" "новое значение"
- `while` цикл while.
- `print` Функция печати в стандартный вывод числа
- `line` Функция печати в стандартный вывод символа
- `read` Функция чтения из стандартного входного потока

## Cистема команд

Особенности процессора:

- Машинное слово -- 32 бита, знаковое.
- Память данных:
    - адресуется через регистр `data_address`, значение может быть загружено только из Control Unit;
    - может быть записана:
        - из аккумулятора `AC`;
        - с порта ввода;
    - может быть прочитана в аккумулятор `AC` или в регистр данных `DR`
- Регистр аккумулятора: `AC`:
    - может быть подан на вывод;
    - используются флаги zero, neg;
- Регистр данных `DR`:
    - Используется для получения операндов из Control Unit, чтения данных из data memory, сохранения результатов ALU
    - Может хранить данные
    - Содержимое передается в ALU
- ALU
    - Производит арифметико - логические операции
    - На вход подаются данные из `DR` и data memory
    - Поддерживаемые операции:
        - add - сложение двух операндов
        - mod - остаток от деления значения левого входа от правого входа
        - less - сравнение двух операндов, значение левого должно быть меньше значения правого
        - more - сравнение двух операндов, значение левого должно быть больше значения правого
    - Результат записывается в `AC` или `DR`
- `program_counter` -- счётчик команд:
    - Может быть перезаписан из Control Unit
    - Может быть инкрементирован
    
### Набор инструкций

| Syntax    | Mnemonic | Arguments        | Тактов | Comment                                                                                                    |
|:----------|:---------|------------------|:------:|------------------------------------------------------------------------------------------------------------|
| `let`     | ld       | addr, value      |   4    | Устанавливает значение $2 по данному адресу $1                                                             |                              |
| `%`       | mod      | addr, value      |   2    | Сохраняет в AC остаток от деления значения по адресу $1 на $2                                              |
| `+`       | add      | addr, addr       |   5    | Сложить значения, лежащие по адресам $1 $2, результат в AC                                                 |
| `-`       | sub      | addr, addr       |   4+   | Вычесть из значения, лежащего по адресу $1 значение в адресе $2, результат в AC                            |
| `while`   | loop     | addr, addr, addr |  5/6   | Пока условие выполняется, исполняем тело функции                                                           |
| `<`       | less     | addr, addr       |   5    | Сравнение значений двух чисел, лежащие по адресам $1 и  $2. Пока значение в DR < значения ACC, flag = TRUE |
| `<`       | more     | addr, addr       |   5    | Сравнение значений двух чисел, лежащие по адресам $1 и  $2. Пока значение в DR > значения ACC, flag = TRUE |
| `save`    | save     | addr             |   3    | Сохраняет значение по адресу                                                                               |
| `read`    | read     | addr             |   3    | Прочитать один символ с потока ввода                                                                       |
| `print`   | print    | addr             |   3    | Вывод числа по адресу $1                                                                                   |
| `println` | printf   | addr             |   3    | Вывод символа по адресу $1                                                                                 |
| `loop`    | loop     | addr             |   2    | Хранит адрес начала цикла                                                                                  |
| `jne`     | jne      | 0                |   2    | Возвращается на начало цикла, пока flag = True                                                             |
|           | halt     | 0                |   0    | остановка                                                                                                  | 

### Кодирование инструкций

- Машинный код сериализуется в список JSON.
- Одна команда функции - одна инструкция.
- Индекс списка -- адрес инструкции. Используется для команд перехода.

Пример:

```json
    {
        "opcode": "add",
        "arg": [
            1,
            2
        ]
    }
```

где:

- `opcode` -- строка с кодом операции;
- `arg` -- список аргументов ;

## Транслятор

Интерфейс командной строки: `translator.py <input_file> <target_file>`

Реализовано в модуле: [translator](translator.py)

Этапы трансляции :

1. Трансформирование текста в последовательность значимых термов(токенов); (tokens.py)
2. Формирование абстрактного синтаксического дерева; (nodes.py)
3. Генерация машинного кода; (translate.py)

Правила генерации машинного кода:

- Для учета циклов и других конструкций считается количество открытых и закрытых скобок;
- После открывающийся скобки может идти как функция так и её аргументы;
- Аргументами функций могут быть переменные, числа, другие функции;
- В зависимости от выражения может быть сгенерировано различное количество инструкций;
- В конце генерации автоматически добавляется инструкция halt.

## Модель процессора

Реализовано в модуле: [machine](./machine.py).

### DataPath


Реализован в классе `DataPath`.

- `data_memory` -- однопортовая, поэтому либо читаем, либо пишем.
- `input` -- вызовет остановку процесса моделирования, если буфер входных значений закончился.

Сигналы (обрабатываются за один такт, реализованы в виде методов класса):

- `latch_data_addr` -- защёлкнуть значение в `data_addr`;
- `latch_acc` -- защёлкнуть в аккумулятор значение с ALU;
- `latch_dr` -- защелкнуть в регистр данных выбранное значение
- `output` -- записать текущее значение `data memory` в порт вывода ;
- `wr` -- записать выбранное значение в память:
    - Из регистра `AC`
    - с порта ввода (обработка на python).

Флаги:
- `neg` -- отражает наличие в аккумуляторе отрицательного числа
- `zero` -- отражает наличие нулевого значения в аккумуляторе.

### ControlUnit

Реализован в классе `ControlUnit`.

- Hardwired (реализовано полностью на python).
- Моделирование на уровне инструкций.
- Трансляция инструкции в последовательность (0-6 тактов) сигналов: `decode_and_execute_instruction`.
- `step_counter` необходим для многотактовых команд:
    - в классе `ControlUnit` отсутствует, т.к. моделирование производится на уровне инструкций.

Сигнал:

- `latch_program_counter` -- сигнал для обновления счётчика команд в ControlUnit.

Особенности работы модели:

- Для журнала состояний процессора используется стандартный модуль logging.
- Количество инструкций для моделирования ограничено hardcoded константой.
- Остановка моделирования осуществляется при помощи исключений:
    - `EOFError` -- если нет данных для чтения из порта ввода-вывода;
    - `StopIteration` -- если выполнена инструкция `halt`.
- Управление симуляцией реализовано в функции `simulate`.

## Апробация

В качестве тестов использовано два алгоритма:

1. [hello world](examples/cat.js).
2. [prob2](examples/prob2.js)

Tесты реализованы тут: [integration_test](integration_test.py)

CL:
```yaml
lab3-example:
  stage: test
  image:
    name: python-tools
    entrypoint: [""]
  script:
    - python3-coverage run -m pytest --verbose
    - find . -type f -name "*.py" | xargs -t python3-coverage report
    - find . -type f -name "*.py" | xargs -t pep8 --ignore=E501
    - find . -type f -name "*.py" | xargs -t pylint
```
где:

- `python3-coverage` -- формирование отчёта об уровне покрытия исходного кода.
- `pytest` -- утилита для запуска тестов.
- `pep8` -- утилита для проверки форматирования кода. `E501` (длина строк) отключено.
- `pylint` -- утилита для проверки качества кода. Некоторые правила отключены в отдельных модулях с целью упрощения кода.
- `mypy` -- утилита для проверки корректности статической типизации.
  - `--check-untyped-defs` -- дополнительная проверка.
  - `--explicit-package-bases` и `--namespace-packages` -- помогает правильно искать импортированные модули.

Пример использования и журнал работы процессора на примере `hello_world`:
```sh
$ cat examples/input.txt

$ cat examples/hello_world.js
let a = "h";
let b = "e";
let c = "l";
let d = "l";
let e = "o";
let f = " ";
let g = "w";
let h = "o";
let i = "r";
let j = "l";
let k = "d";
println(a);
println(b);
println(c);
println(d);
println(e);
println(f);
println(g);
println(h);
println(i);
println(j);
println(k);
$ python translator.py examples/hello_world.js out.txt
source LoC: 56 code instr: 33

$ cat out.txt
 [
    {
        "opcode": "ld",
        "arg": [
            0,
            "h"
        ]
    },
    {
        "opcode": "ld",
        "arg": [
            1,
            "e"
        ]
    },
    {
        "opcode": "ld",
        "arg": [
            2,
            "l"
        ]
    },
    {
        "opcode": "ld",
        "arg": [
            3,
            "l"
        ]
    },
    {
        "opcode": "ld",
        "arg": [
            4,
            "o"
        ]
    },
    {
        "opcode": "ld",
        "arg": [
            5,
            " "
        ]
    },
    {
        "opcode": "ld",
        "arg": [
            6,
            "w"
        ]
    },
    {
        "opcode": "ld",
        "arg": [
            7,
            "o"
        ]
    },
    {
        "opcode": "ld",
        "arg": [
            8,
            "r"
        ]
    },
    {
        "opcode": "ld",
        "arg": [
            9,
            "l"
        ]
    },
    {
        "opcode": "ld",
        "arg": [
            10,
            "d"
        ]
    },
    {
        "opcode": "print",
        "arg": [
            0
        ]
    },
    {
        "opcode": "print",
        "arg": [
            1
        ]
    },
    {
        "opcode": "print",
        "arg": [
            2
        ]
    },
    {
        "opcode": "print",
        "arg": [
            3
        ]
    },
    {
        "opcode": "print",
        "arg": [
            4
        ]
    },
    {
        "opcode": "print",
        "arg": [
            5
        ]
    },
    {
        "opcode": "print",
        "arg": [
            6
        ]
    },
    {
        "opcode": "print",
        "arg": [
            7
        ]
    },
    {
        "opcode": "print",
        "arg": [
            8
        ]
    },
    {
        "opcode": "print",
        "arg": [
            9
        ]
    },
    {
        "opcode": "print",
        "arg": [
            10
        ]
    },
    {
        "opcode": "halt"
    }
]

$ python3 machine.py examples/out.txt examples/input.txt
DEBUG:root:{TICK: 0, PC: 0, ADDR: 0, OUT: 0, AC: 0, DR: 0} ld [0, 'h']
  DEBUG:root:{TICK: 4, PC: 1, ADDR: 0, OUT: 104, AC: 104, DR: 104} ld [1, 'e']
  DEBUG:root:{TICK: 8, PC: 2, ADDR: 1, OUT: 101, AC: 101, DR: 101} ld [2, 'l']
  DEBUG:root:{TICK: 12, PC: 3, ADDR: 2, OUT: 108, AC: 108, DR: 108} ld [3, 'l']
  DEBUG:root:{TICK: 16, PC: 4, ADDR: 3, OUT: 108, AC: 108, DR: 108} ld [4, 'o']
  DEBUG:root:{TICK: 20, PC: 5, ADDR: 4, OUT: 111, AC: 111, DR: 111} ld [5, ' ']
  DEBUG:root:{TICK: 24, PC: 6, ADDR: 5, OUT: 32, AC: 32, DR: 32} ld [6, 'w']
  DEBUG:root:{TICK: 28, PC: 7, ADDR: 6, OUT: 119, AC: 119, DR: 119} ld [7, 'o']
  DEBUG:root:{TICK: 32, PC: 8, ADDR: 7, OUT: 111, AC: 111, DR: 111} ld [8, 'r']
  DEBUG:root:{TICK: 36, PC: 9, ADDR: 8, OUT: 114, AC: 114, DR: 114} ld [9, 'l']
  DEBUG:root:{TICK: 40, PC: 10, ADDR: 9, OUT: 108, AC: 108, DR: 108} ld [10, 'd']
  DEBUG:root:{TICK: 44, PC: 11, ADDR: 10, OUT: 100, AC: 100, DR: 100} print [0]
  DEBUG:root:output: 'h'
  DEBUG:root:{TICK: 47, PC: 12, ADDR: 0, OUT: 104, AC: 100, DR: 100} print [1]
  DEBUG:root:output: 'he'
  DEBUG:root:{TICK: 50, PC: 13, ADDR: 1, OUT: 101, AC: 100, DR: 100} print [2]
  DEBUG:root:output: 'hel'
  DEBUG:root:{TICK: 53, PC: 14, ADDR: 2, OUT: 108, AC: 100, DR: 100} print [3]
  DEBUG:root:output: 'hell'
  DEBUG:root:{TICK: 56, PC: 15, ADDR: 3, OUT: 108, AC: 100, DR: 100} print [4]
  DEBUG:root:output: 'hello'
  DEBUG:root:{TICK: 59, PC: 16, ADDR: 4, OUT: 111, AC: 100, DR: 100} print [5]
  DEBUG:root:output: 'hello '
  DEBUG:root:{TICK: 62, PC: 17, ADDR: 5, OUT: 32, AC: 100, DR: 100} print [6]
  DEBUG:root:output: 'hello w'
  DEBUG:root:{TICK: 65, PC: 18, ADDR: 6, OUT: 119, AC: 100, DR: 100} print [7]
  DEBUG:root:output: 'hello wo'
  DEBUG:root:{TICK: 68, PC: 19, ADDR: 7, OUT: 111, AC: 100, DR: 100} print [8]
  DEBUG:root:output: 'hello wor'
  DEBUG:root:{TICK: 71, PC: 20, ADDR: 8, OUT: 114, AC: 100, DR: 100} print [9]
  DEBUG:root:output: 'hello worl'
  DEBUG:root:{TICK: 74, PC: 21, ADDR: 9, OUT: 108, AC: 100, DR: 100} print [10]
  DEBUG:root:output: 'hello world'
  DEBUG:root:{TICK: 77, PC: 22, ADDR: 10, OUT: 100, AC: 100, DR: 100} halt 
  INFO:root:output_buffer: hello world

instr_counter:  22 ticks: 77

```