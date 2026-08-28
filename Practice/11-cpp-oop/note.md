# Занятие 11. C++ и ООП: пишем собственную библиотеку

**Цель занятия:** перейти от процедурного стиля к объектному, научиться проектировать классы для работы с устройствами и оформлять их как переиспользуемые библиотеки; понять, какие возможности C++ применимы на микроконтроллере, а какие - нет.

**Что понадобится:** PlatformIO, Arduino UNO, кнопки, светодиоды, джойстик, светодиодная матрица 8x8 со сдвиговым регистром.

> **Справочники.** По языку: [Приложение C](../../Appendix/c.md) и [Приложение C++](../../Appendix/cpp.md).
> По самому ООП - отдельный [справочник по ООП на C++](../../Appendix/oop/README.md): классы, наследование, отношения между классами, перегрузка операторов, шаблоны, интерфейсы. Занятие даёт минимум, нужный для драйверов устройств; за подробностями по любой конструкции идите туда.

---

## 1. Проблема, которую решает ООП

Вспомним модуль мигания из [занятия 6](../06-platformio/note.md):

```cpp
static uint8_t ledPin = LED_BUILTIN;
static unsigned long period = 500;
static unsigned long lastToggle = 0;
static bool state = false;

void blinkInit(uint8_t pin);
void blinkUpdate();
```

Модуль работает, инкапсуляция есть. Но он умеет управлять **ровно одним** светодиодом. Понадобилось два - и есть три пути, каждый плохой:

**Путь 1: скопировать модуль.**

```cpp
void blink1Init(uint8_t pin);   void blink1Update();
void blink2Init(uint8_t pin);   void blink2Update();
```

Дублирование кода. Исправление ошибки нужно вносить в двух местах, а при пяти светодиодах - в пяти.

**Путь 2: массивы.**

```cpp
static uint8_t ledPin[MAX_LEDS];
static unsigned long period[MAX_LEDS];
static bool state[MAX_LEDS];

void blinkUpdate(uint8_t index);
```

Работает, но появляется индекс, который нужно везде таскать и не перепутать. Данные одного светодиода разбросаны по трём массивам. Количество ограничено константой.

**Путь 3: структура с функциями.**

```cpp
struct Blinker {
    uint8_t pin;
    unsigned long period;
    unsigned long lastToggle;
    bool state;
};

void blinkInit(Blinker *b, uint8_t pin);
void blinkUpdate(Blinker *b);
```

Уже почти хорошо: данные собраны вместе, экземпляров сколько угодно. Именно так пишут на чистом C.

**Класс C++ - это путь 3, доведённый до конца:** функции переезжают внутрь структуры, указатель на неё передаётся неявно, а доступ к внутренним полям можно закрыть.

```cpp
class Blinker {
public:
    Blinker(uint8_t pin, unsigned long period);
    void begin();
    void update();
    void setPeriod(unsigned long ms);
private:
    uint8_t _pin;
    unsigned long _period;
    unsigned long _lastToggle;
    bool _state;
};
```

Использование:

```cpp
Blinker red(5, 250);
Blinker green(6, 1000);

void setup() {
    red.begin();
    green.begin();
}

void loop() {
    red.update();
    green.update();
}
```

Два независимых объекта, каждый со своим состоянием, никаких индексов и дублирования.

---

## 2. Класс: устройство и терминология

```cpp
class Blinker {
public:                       // раздел, доступный извне
    Blinker(uint8_t pin);     // конструктор
    void begin();             // метод
private:                      // раздел, доступный только изнутри класса
    uint8_t _pin;             // поле (член данных)
    bool _state;
};
```

| Термин | Что это |
| --- | --- |
| **Класс** | Описание типа: какие данные и какие операции |
| **Объект (экземпляр)** | Конкретная переменная этого типа |
| **Поле** | Переменная внутри объекта |
| **Метод** | Функция, работающая с полями своего объекта |
| **Конструктор** | Метод, вызываемый при создании объекта |
| **`public`** | Доступно снаружи - это интерфейс класса |
| **`private`** | Доступно только методам самого класса |

### Зачем `private`

Инкапсуляция - не бюрократия, а защита от собственных ошибок. Если поле `_lastToggle` было бы публичным, любой участок программы мог бы его изменить, и поиск причины сбоя занял бы часы.

Публичным делается **минимум необходимого**: то, что действительно является интерфейсом устройства. Всё остальное - `private`.

Соглашение об именовании полей с подчёркиванием (`_pin`) или суффиксом (`pin_`) распространено в embedded-коде: сразу видно, что это поле объекта, а не локальная переменная.

### Разделение на .h и .cpp

`lib/Blinker/Blinker.h`:

```cpp
#pragma once
#include <Arduino.h>

/**
 * Неблокирующее мигание светодиодом.
 *
 * Пример:
 *   Blinker led(13, 500);
 *   void setup() { led.begin(); }
 *   void loop()  { led.update(); }
 */
class Blinker {
public:
    Blinker(uint8_t pin, unsigned long periodMs = 500);

    void begin();                          // настроить вывод
    void update();                         // вызывать в каждой итерации loop()
    void setPeriod(unsigned long ms);
    void on();
    void off();
    bool isOn() const;                     // const: метод не меняет объект

private:
    uint8_t _pin;
    unsigned long _period;
    unsigned long _lastToggle;
    bool _state;
};
```

`lib/Blinker/Blinker.cpp`:

```cpp
#include "Blinker.h"

Blinker::Blinker(uint8_t pin, unsigned long periodMs)
    : _pin(pin), _period(periodMs), _lastToggle(0), _state(false) {
}

void Blinker::begin() {
    pinMode(_pin, OUTPUT);
    digitalWrite(_pin, LOW);
    _lastToggle = millis();
}

void Blinker::update() {
    if (millis() - _lastToggle < _period) return;
    _lastToggle += _period;
    _state = !_state;
    digitalWrite(_pin, _state);
}

void Blinker::setPeriod(unsigned long ms) { _period = ms; }

void Blinker::on()  { _state = true;  digitalWrite(_pin, HIGH); }
void Blinker::off() { _state = false; digitalWrite(_pin, LOW); }

bool Blinker::isOn() const { return _state; }
```

Разберём непривычные конструкции.

**`Blinker::Blinker`** - определение метода вне класса. Слева от `::` имя класса, справа - имя метода.

**Список инициализации** `: _pin(pin), _period(periodMs)` - поля инициализируются **до** входа в тело конструктора. Это эффективнее присваивания в теле и единственный способ инициализировать константные поля и ссылки. Инициализируйте поля именно так.

**`const` после имени метода** - обещание, что метод не меняет объект. Компилятор это проверяет. Помечайте `const` все методы-геттеры: это ловит ошибки и позволяет вызывать метод у константного объекта.

**Значение по умолчанию** `periodMs = 500` указывается **только в объявлении** (в `.h`), не в определении.

### Почему `begin()`, а не всё в конструкторе

Правило, важное именно для микроконтроллеров: **конструкторы глобальных объектов выполняются до `main()`**, то есть до вызова `init()` из ядра Arduino. В этот момент таймеры не настроены, `millis()` не работает, и вызов `pinMode()` может не дать эффекта.

Поэтому в библиотеках Arduino принято разделение:

- **конструктор** - только сохранить параметры в поля;
- **`begin()`** - вся реальная инициализация оборудования, вызывается из `setup()`.

Именно так устроены `Serial.begin()`, `lcd.begin()`, `dht.begin()`, `SPI.begin()`.

---

## 3. Практический пример: класс кнопки

Соберём в класс всё, что мы знаем о кнопках из [занятия 3](../03-digital-io/note.md): подтяжка, подавление дребезга, определение фронта, короткое и длинное нажатие.

`lib/Button/Button.h`:

```cpp
#pragma once
#include <Arduino.h>

class Button {
public:
    Button(uint8_t pin, bool activeLow = true, uint16_t debounceMs = 30);

    void begin();
    void update();                       // вызывать в каждой итерации loop()

    bool isPressed() const;              // текущее состояние (уровень)
    bool wasPressed();                   // фронт нажатия, сбрасывается при чтении
    bool wasReleased();                  // фронт отпускания
    bool wasLongPressed(uint16_t ms = 1000);

    unsigned long pressDuration() const; // длительность текущего нажатия, мс

private:
    uint8_t  _pin;
    bool     _activeLow;
    uint16_t _debounce;

    bool _stable;                        // подтверждённое состояние: true = нажата
    bool _lastReading;
    unsigned long _lastChange;
    unsigned long _pressStart;

    bool _flagPressed;                   // взведённые флаги событий
    bool _flagReleased;
    bool _flagLong;
};
```

`lib/Button/Button.cpp`:

```cpp
#include "Button.h"

Button::Button(uint8_t pin, bool activeLow, uint16_t debounceMs)
    : _pin(pin), _activeLow(activeLow), _debounce(debounceMs),
      _stable(false), _lastReading(false),
      _lastChange(0), _pressStart(0),
      _flagPressed(false), _flagReleased(false), _flagLong(false) {
}

void Button::begin() {
    pinMode(_pin, _activeLow ? INPUT_PULLUP : INPUT);
    _lastReading = _stable = false;
    _lastChange = millis();
}

void Button::update() {
    bool raw = digitalRead(_pin);
    bool pressed = _activeLow ? !raw : raw;     // приводим к "true = нажата"

    if (pressed != _lastReading) {              // сигнал шевельнулся
        _lastReading = pressed;
        _lastChange = millis();
        return;
    }

    if (millis() - _lastChange < _debounce) return;   // ещё не устоялся

    if (pressed != _stable) {                   // состояние подтверждено
        _stable = pressed;
        if (_stable) {
            _pressStart = millis();
            _flagPressed = true;
        } else {
            _flagReleased = true;
            _flagLong = false;
        }
    }
}

bool Button::isPressed() const { return _stable; }

bool Button::wasPressed() {
    if (!_flagPressed) return false;
    _flagPressed = false;                        // флаг одноразовый
    return true;
}

bool Button::wasReleased() {
    if (!_flagReleased) return false;
    _flagReleased = false;
    return true;
}

bool Button::wasLongPressed(uint16_t ms) {
    if (_stable && !_flagLong && (millis() - _pressStart >= ms)) {
        _flagLong = true;                        // срабатывает один раз за нажатие
        return true;
    }
    return false;
}

unsigned long Button::pressDuration() const {
    return _stable ? (millis() - _pressStart) : 0;
}
```

Использование становится декларативным:

```cpp
#include <Arduino.h>
#include <Button.h>
#include <Blinker.h>

Button  up(7), down(8), select(9);
Blinker led(13, 250);

void setup() {
    Serial.begin(9600);
    up.begin(); down.begin(); select.begin();
    led.begin();
}

void loop() {
    up.update(); down.update(); select.update();
    led.update();

    if (up.wasPressed())              Serial.println(F("UP"));
    if (down.wasPressed())            Serial.println(F("DOWN"));
    if (select.wasLongPressed(1500))  Serial.println(F("LONG SELECT"));
}
```

Сравните с тем, что получилось бы без класса: три копии переменных дребезга, три копии логики фронтов, около сотни строк вместо десяти.

---

## 4. Что из C++ применимо на AVR, а что нет

Компилятор avr-gcc поддерживает практически весь C++, но 2 КБ ОЗУ и 16 МГц накладывают ограничения.

### Применяйте свободно

| Возможность | Стоимость |
| --- | --- |
| Классы, методы, конструкторы | Ноль. Метод компилируется в обычную функцию с неявным `this` |
| `private`/`public` | Ноль. Проверка на этапе компиляции |
| Ссылки (`int&`) | Ноль. Тот же указатель, но безопаснее |
| `const` | Ноль, а иногда экономия: константы могут уехать во Flash |
| Перегрузка функций | Ноль. Разрешается при компиляции |
| Значения аргументов по умолчанию | Ноль |
| `enum class` | Ноль, при этом безопаснее обычного `enum` |
| Шаблоны | Ноль во время работы, но раздувают Flash при многих инстанцированиях |
| `inline`-методы в заголовке | Обычно ускорение |

### Применяйте осознанно

**Наследование и виртуальные функции.** Виртуальный метод добавляет в каждый объект указатель на таблицу виртуальных функций (2 байта на AVR) и делает вызов косвенным (примерно вдвое медленнее). Сама таблица занимает Flash.

Это оправдано, когда действительно нужен единый интерфейс для разных устройств:

```cpp
class Display {
public:
    virtual void clear() = 0;                          // чисто виртуальный метод
    virtual void print(const char *text) = 0;
    virtual ~Display() {}
};

class LcdDisplay : public Display {
public:
    void clear() override;
    void print(const char *text) override;
};

class TftDisplay : public Display {
public:
    void clear() override;
    void print(const char *text) override;
};

void showStatus(Display &d) {      // работает с любым дисплеем
    d.clear();
    d.print("OK");
}
```

Но если реализация в программе одна, виртуальность - лишние байты. Правило: **наследование ради общего интерфейса - да, наследование ради переиспользования кода - подумайте дважды**.

### Не применяйте

| Возможность | Почему |
| --- | --- |
| `new` / `delete`, `malloc` | Фрагментация кучи в 2 КБ ОЗУ; отказ выделения обнаружить трудно |
| Класс `String` | Постоянные перевыделения памяти, фрагментация, непредсказуемые зависания. Используйте `char[]` фиксированного размера |
| `std::vector`, `std::map` и прочий STL | Динамическая память, большой объём кода |
| Исключения (`try`/`catch`) | Отключены по умолчанию, дорого по Flash и стеку |
| RTTI (`dynamic_cast`, `typeid`) | Отключено по умолчанию |
| `std::function`, лямбды с захватом | Могут выделять память |
| Множественное наследование | Усложняет раскладку объекта, редко нужно |

Класс `String` заслуживает отдельного упоминания: он присутствует в ядре Arduino, удобен и встречается во всех примерах в интернете. И он же - причина большинства "плата зависает через полчаса" в студенческих проектах. Конкатенация строк многократно выделяет и освобождает память, куча фрагментируется, и в какой-то момент очередное выделение сталкивается со стеком.

Замена:

```cpp
// вместо String
char buffer[32];
snprintf(buffer, sizeof(buffer), "T=%d C H=%d%%", temp, hum);
Serial.println(buffer);
```

Функция `snprintf` ограничена размером буфера и не выделяет память. На AVR она по умолчанию не поддерживает `%f` - для дробных чисел используйте `dtostrf()`.

---

## 5. Полезные приёмы C++ для встраиваемых систем

### `enum class` вместо констант

```cpp
enum class LedState : uint8_t { Off, On, Blinking };

LedState state = LedState::Off;

if (state == LedState::On) { }
// if (state == 1) { }   - ошибка компиляции, и это хорошо
```

Явное указание `: uint8_t` фиксирует размер в один байт. Обычный `enum` неявно приводится к числу, что позволяет случайно сравнить несравнимое.

### Ссылки вместо указателей

```cpp
void configure(Blinker &led) {      // нельзя передать nullptr, синтаксис проще
    led.setPeriod(100);
}
configure(red);
```

Ссылка не может быть "нулевой" и не требует разыменования. Указатель нужен там, где значение может отсутствовать или меняться.

### `constexpr` вместо `#define`

```cpp
constexpr uint8_t LED_PIN = 13;
constexpr unsigned long PERIOD_MS = 500;
```

В отличие от `#define`, здесь есть тип и проверка компилятором, а места в памяти константа не занимает - значение подставляется при компиляции.

### Массив объектов

```cpp
Button buttons[3] = { Button(7), Button(8), Button(9) };

void setup() {
    for (auto &b : buttons) b.begin();      // цикл по диапазону
}

void loop() {
    for (auto &b : buttons) b.update();

    for (uint8_t i = 0; i < 3; i++) {
        if (buttons[i].wasPressed()) {
            Serial.print(F("Нажата кнопка "));
            Serial.println(i);
        }
    }
}
```

Обратите внимание на `auto &b` - именно ссылка. Без амперсанда объект копировался бы на каждой итерации, и `update()` работал бы с копией, а не с оригиналом. Это частая и труднонаходимая ошибка.

### Шаблоны для буферов

```cpp
template <typename T, uint8_t SIZE>
class RingBuffer {
public:
    void push(T value) {
        _data[_head] = value;
        _head = (_head + 1) % SIZE;
        if (_count < SIZE) _count++;
    }

    T get(uint8_t index) const { return _data[(_head + SIZE - _count + index) % SIZE]; }
    uint8_t size() const { return _count; }

private:
    T _data[SIZE];
    uint8_t _head = 0;
    uint8_t _count = 0;
};

RingBuffer<uint16_t, 32> samples;     // 32 отсчёта АЦП
RingBuffer<uint8_t, 8>   events;      // 8 событий
```

Размер известен на этапе компиляции, динамической памяти нет, а код пишется один раз для любых типов. Помните только: каждая новая комбинация параметров порождает **отдельную копию кода** во Flash.

---

## 6. Оформление библиотеки для PlatformIO

Библиотека - это папка внутри `lib/` со стандартной структурой:

```
lib/
  Joystick/
    library.json          - метаданные (необязательно, но желательно)
    README.md             - описание, схема подключения, пример
    keywords.txt          - подсветка синтаксиса в Arduino IDE
    src/
      Joystick.h
      Joystick.cpp
    examples/
      Basic/
        Basic.cpp
```

PlatformIO находит библиотеку автоматически: достаточно написать `#include <Joystick.h>` в `main.cpp`.

`library.json`:

```json
{
  "name": "Joystick",
  "version": "1.0.0",
  "description": "Драйвер двухосевого джойстика KY-023 с калибровкой и мёртвой зоной",
  "keywords": "joystick, ky-023, analog",
  "authors": [{ "name": "Иванов И. И." }],
  "frameworks": "arduino",
  "platforms": "atmelavr"
}
```

### Что делает библиотеку хорошей

1. **Заголовок читается без реализации.** Открыв `.h`, можно понять, что умеет библиотека и как ей пользоваться. Комментарий с примером обязателен.
2. **Ничего лишнего в `public`.** Всё, что не является интерфейсом устройства, - `private`.
3. **Нет привязки к конкретным выводам.** Номера передаются в конструктор, а не задаются `#define` внутри библиотеки.
4. **Нет вывода в Serial.** Библиотека не должна ничего печатать: пользователь может использовать порт иначе или не использовать вовсе. Ошибки возвращаются кодом или флагом.
5. **Нет блокирующих задержек.** `delay()` внутри библиотеки лишает пользователя возможности писать неблокирующие программы. Если нужно ждать - предоставьте метод `isReady()` или `update()`.
6. **Разумные значения по умолчанию.** Библиотека должна работать сразу после конструктора с минимумом параметров.
7. **Экономность.** Никакого `String`, никакого динамического выделения памяти, буферы фиксированного размера.
8. **Есть рабочий пример** в `examples/`.

### Антипримеры

```cpp
class BadSensor {
public:
    int value;                            // 1. публичное поле - кто угодно испортит

    void read() {
        digitalWrite(2, HIGH);            // 2. вывод жёстко зашит
        delay(50);                        // 3. блокирующая задержка
        value = analogRead(A0);
        Serial.println(value);            // 4. библиотека печатает в порт
        if (value > 1000) {
            Serial.println("Error!");     // 5. ошибка сообщается печатью
        }
    }
};
```

Исправленный вариант:

```cpp
class GoodSensor {
public:
    GoodSensor(uint8_t powerPin, uint8_t signalPin);

    void begin();
    void startMeasurement();              // запустить, не блокируя
    bool isReady() const;                 // готово ли
    uint16_t value() const;               // забрать результат
    bool hasError() const;                // сообщить об ошибке флагом

private:
    uint8_t _powerPin, _signalPin;
    uint16_t _value;
    unsigned long _startTime;
    bool _measuring, _error;
};
```

---

## 7. Когда ООП не нужно

Объектный подход - инструмент, а не самоцель. Оборачивать в класс имеет смысл сущность, у которой есть **состояние** и которая может существовать **в нескольких экземплярах**.

Не нужен класс для:

- набора несвязанных вспомогательных функций - хватит модуля из `.h` и `.cpp`;
- сущности, которая заведомо в единственном экземпляре и не имеет состояния;
- обработчиков прерываний - метод класса нельзя напрямую передать в `attachInterrupt()` (нужен статический метод-переходник и указатель на экземпляр);
- простого преобразования данных - это функция.

Признак избыточности: класс без полей, состоящий из одного метода. Это функция, которую зачем-то завернули в класс.

---

## Контрольные вопросы

1. Какую конкретную проблему модуля на `static`-переменных решает класс?
2. Почему инициализацию оборудования выносят в `begin()`, а не выполняют в конструкторе?
3. Что такое список инициализации конструктора и чем он лучше присваивания в теле?
4. Что означает `const` после имени метода и что проверяет компилятор?
5. Сколько байт добавляет к объекту первый виртуальный метод и почему?
6. Почему `String` не следует использовать на Arduino UNO? Чем его заменить?
7. В чём разница между `for (auto b : buttons)` и `for (auto &b : buttons)`? Какая из записей ошибочна в примере из конспекта?
8. Почему шаблоны не стоят ничего во время работы, но могут раздуть Flash?
9. Перечислите пять признаков хорошо спроектированной библиотеки.
10. Почему библиотека не должна ничего выводить в Serial?

## Что читать дальше

Занятие охватывает тот минимум ООП, который нужен для драйверов устройств. Полное изложение - в [справочнике по ООП на C++](../../Appendix/oop/README.md):

| Если нужно | Раздел справочника |
| --- | --- |
| Разобраться с конструкторами, деструкторами и порядком инициализации полей | [Классы и объекты](../../Appendix/oop/01-classes.md) |
| Понять, когда наследование, а когда композиция | [Наследование и композиция](../../Appendix/oop/02-inheritance.md) |
| Отличить композицию от агрегации и ассоциации, разобраться с копированием | [Отношения между классами](../../Appendix/oop/03-relations.md) |
| Написать оператор присваивания, сравнения или вывода | [Перегрузка функций и операторов](../../Appendix/oop/04-overloading.md) |
| Сделать драйвер, работающий с разными типами данных | [Шаблоны](../../Appendix/oop/05-templates.md) |
| Понять проблему ромба и виртуальное наследование | [Множественное наследование](../../Appendix/oop/06-advanced-inheritance.md) |
| Спроектировать общий интерфейс для нескольких дисплеев или датчиков | [Интерфейсные классы](../../Appendix/oop/07-interfaces.md) |

> Примеры в справочнике написаны для настольного C++ и используют `std::cout`, `std::string` и `new`. На плате их применять нельзя - разметка по применимости приведена в [обзорном разделе справочника](../../Appendix/oop/README.md#что-применимо-на-arduino-uno).

## Задание

Задачи занятия - в [task.md](task.md). Основная работа - **разработка собственной библиотеки**.

Библиотека из задачи 11.3 - заготовка. Доведением её до состояния, пригодного для чужого проекта, занята [лабораторная работа 2](../../Labs/lab2-sensor-library/lab.md): там к ней добавляются документация, примеры, тесты и проверка чужими руками.
