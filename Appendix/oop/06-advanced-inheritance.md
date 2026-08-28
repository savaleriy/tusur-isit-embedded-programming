# Множественное наследование и абстракции

Типы наследования, проблема ромба, виртуальное наследование, абстрактные классы.

---

### Что такое наследование?

Наследование - один из основополагающих принципов объектно-ориентированного программирования (ООП). Оно позволяет одному классу (подклассу) использовать переменные и методы другого класса (суперкласса). Подкласс наследует характеристики суперкласса, что упрощает структуру и повторное использование кода.

При обычном наследовании класс `Y` наследует все свойства и методы класса `X`. Это позволяет классу `Y` расширять или изменять функциональность, добавляя свои собственные методы или переопределяя унаследованные. Множественное наследование расширяет этот принцип, позволяя классу `Y` наследовать функциональность сразу от нескольких классов (`X`, `Z` и т.д.). При этом класс `Y` получает доступ ко всем свойствам и методам всех своих предков.

Наследование позволяет классу использовать уже существующую функциональность других классов. Это удобно, так как не нужно заново реализовывать уже написанный код. Тем не менее, иногда для достижения схожей цели можно применять композицию, когда один класс содержит экземпляры других классов. Если же необходимая функциональность разбросана по нескольким классам, то множественное наследование становится единственным способом объединить её в одном классе.

> Наследование - это фундаментальный принцип объектно-ориентированного программирования (ООП), однако его следует использовать с осторожностью. Важно помнить, что код, который вы разрабатываете, может изменяться, и его использование может быть не всегда очевидным для других разработчиков.

### Пример простого наследования

```c++
#include <iostream>
using namespace std;

class Device {
public:
    int serial_number = 12345678;

    void turn_on() {
        cout << "Device is on" << endl;
    }
private:
    int pincode = 87654321;
};

class Computer : public Device {};

int main() {
    Computer computer_instance;

    computer_instance.turn_on();
    cout << "Serial number is: " << computer_instance.serial_number << endl;
    // cout << "Pin code is: " << computer_instance.pincode << endl; // ошибка компиляции
    return 0;
}
```

#### Типы наследования

В C++ существуют три типа наследования:

1. **Публичное (public)**: публичные и защищенные данные наследуются без изменения уровня доступа.
2. **Защищенное (protected)**: все унаследованные данные становятся защищенными.
3. **Приватное (private)**: все унаследованные данные становятся приватными.
```c++
#include <iostream>
using namespace std;

class Device {
public:
    int serial_number = 12345678;

    void turn_on() {
        cout << "Device is on" << endl;
    }
};

class Computer : private Device {
public:
    void say_hello() {
        turn_on();
        cout << "Welcome to Windows 95!" << endl;
    }
};

int main() {
    Device device_instance;
    Computer computer_instance;

    cout << "\t Device" << endl;
    cout << "Serial number is: " << device_instance.serial_number << endl;
    device_instance.turn_on();

    // cout << "Serial number is: " << computer_instance.serial_number << endl; // ошибка компиляции
    // computer_instance.turn_on(); // ошибка компиляции

    cout << "\t Computer" << endl;
    computer_instance.say_hello();
    return 0;
}
```

### Конструкторы и деструкторы

Конструкторы и деструкторы в C++ не наследуются, но вызываются иерархически. Сначала вызывается конструктор базового класса, затем - производного, и наоборот для деструкторов.

```c++
#include <iostream>
using namespace std;

class Device {
public:
    Device() {
        cout << "Device constructor called" << endl;
    }
    ~Device() {
        cout << "Device destructor called" << endl;
    }
};

class Computer : public Device {
public:
    Computer() {
        cout << "Computer constructor called" << endl;
    }
    ~Computer() {
        cout << "Computer destructor called" << endl;
    }
};

class Laptop : public Computer {
public:
    Laptop() {
        cout << "Laptop constructor called" << endl;
    }
    ~Laptop() {
        cout << "Laptop destructor called" << endl;
    }
};

int main() {
    cout << "\tConstructors" << endl;
    Laptop laptop_instance;
    cout << "\tDestructors" << endl;
    return 0;
}
```

### Множественное наследование

Множественное наследование - это ситуация, когда подкласс наследует от двух или более суперклассов.

```c++
#include <iostream>
using namespace std;

class Computer {
public:
    void turn_on() {
        cout << "Welcome to Windows 95" << endl;
    }
};

class Monitor {
public:
    void show_image() {
        cout << "Imagine image here" << endl;
    }
};

class Laptop : public Computer, public Monitor {};

int main() {
    Laptop laptop_instance;
    laptop_instance.turn_on();
    laptop_instance.show_image();
    return 0;
}
```

>Когда класс наследуется от класса, в котором присутствуют реализации, важно осознавать, что такая связь создает тесную зависимость между классами. Изменения в родительском классе могут привести к непредвиденному поведению в классах-наследниках. Ошибки могут проявляться в уже протестированном коде, особенно если иерархия классов сложная. Поэтому важно учитывать, что код может изменяться не только тем, кто его написал, и пути наследования, очевидные для одного разработчика, могут быть неучтенными для других.

#### Проблематика множественного наследования

Множественное наследование может привести к неоднозначностям, когда два родительских класса имеют методы с одинаковыми именами.

```c++
#include <iostream>
using namespace std;

class Computer {
private:
    void turn_on() {
        cout << "Computer is on." << endl;
    }
};

class Monitor {
public:
    void turn_on() {
        cout << "Monitor is on." << endl;
    }
};

class Laptop : public Computer, public Monitor {};

int main() {
    Laptop laptop_instance;
    laptop_instance.turn_on();
    return 0;
}
```

#### Определение проблемы ромба


```mermaid
classDiagram
    direction TB
    class Device {
        +int id
        +begin()
    }
    class Sensor {
        +read()
    }
    class Display {
        +show()
    }
    class SmartPanel {
        +update()
    }
    Device <|-- Sensor
    Device <|-- Display
    Sensor <|-- SmartPanel
    Display <|-- SmartPanel
```

`SmartPanel` наследует `Device` дважды - по одному разу через каждого родителя. В объекте оказывается **две копии** поля `id`, и обращение `panel.id` становится неоднозначным: компилятор не знает, какая из копий имеется в виду.

Виртуальное наследование заставляет обе ветви делить одну общую копию `Device`.

**Проблема ромба (Diamond Problem)** - классическая проблема, возникающая в языках, поддерживающих множественное наследование. Она возникает, когда классы B и C наследуют класс A, а класс D наследует как B, так и C.

#### Пример проблемы

Рассмотрим классы A, B и C, которые определяют метод `print_letter()`. Когда класс D пытается вызвать этот метод, возникает неоднозначность: неясно, какой метод должен быть использован - из A, B или C. Разные языки программирования по-разному решают эту проблему. В C++ это оставлено на усмотрение программиста.

#### Способы разрешения проблемы

1. **Вызов метода конкретного суперкласса**.
2. **Обращение к объекту подкласса как к объекту определенного суперкласса**.
3. **Переопределение проблематичного метода в последнем дочернем классе**.
```c++
#include <iostream>
using namespace std;

class Device {
public:
    void turn_on() {
        cout << "Device is on." << endl;
    }
};

class Computer : public Device {};

class Monitor : public Device {};

class Laptop : public Computer, public Monitor {
    /*
    public:
        void turn_on() {
            cout << "Laptop is on." << endl;
        }
    // Раскомментирование этой функции решит проблему ромба
    */
};

int main() {
    Laptop laptop_instance;

    laptop_instance.turn_on(); // вызовет ошибку компиляции, если метод не переопределен

    // Вызов метода конкретного суперкласса
    laptop_instance.Monitor::turn_on();

    // Обращение к экземпляру Laptop как к экземпляру Monitor
    static_cast<Monitor&>(laptop_instance).turn_on();
    return 0;
}
```

Если метод `turn_on()` не переопределен в `Laptop`, вызов `laptop_instance.turn_on()` приведет к ошибке компиляции. Объект `Laptop` имеет два определения метода `turn_on()`, что вызывает неоднозначность.

#### Конструкторы и деструкторы в контексте проблемы ромба

При инициализации объекта дочернего класса вызываются конструкторы всех родительских классов. В результате конструктор базового класса `Device` будет вызван дважды.

```c++
#include <iostream>
using namespace std;

class Device {
public:
    Device() {
        cout << "Device constructor called" << endl;
    }
};

class Computer : public Device {
public:
    Computer() {
        cout << "Computer constructor called" << endl;
    }
};

class Monitor : public Device {
public:
    Monitor() {
        cout << "Monitor constructor called" << endl;
    }
};

class Laptop : public Computer, public Monitor {};

int main() {
    Laptop laptop_instance;
    return 0;
}
```

При создании объекта `Laptop` конструктор `Device` вызовется дважды, что является нежелательным поведением.

#### Виртуальное наследование

**Виртуальное наследование** предотвращает создание нескольких объектов базового класса в иерархии наследования. При этом конструктор базового класса `Device` будет вызван только один раз, и обращение к методу `turn_on()` без его переопределения в дочернем классе не вызовет ошибку компиляции.

```c++
#include <iostream>
using namespace std;

class Device {
public:
    Device() {
        cout << "Device constructor called" << endl;
    }
    void turn_on() {
        cout << "Device is on." << endl;
    }
};

class Computer : virtual public Device {
public:
    Computer() {
        cout << "Computer constructor called" << endl;
    }
};

class Monitor : virtual public Device {
public:
    Monitor() {
        cout << "Monitor constructor called" << endl;
    }
};

class Laptop : public Computer, public Monitor {};

int main() {
    Laptop laptop_instance;
    laptop_instance.turn_on();
    return 0;
}
```

В этом примере конструктор `Device` будет вызван только один раз, а метод `turn_on()` можно будет вызвать без возникновения ошибок.

**Примечание:** Виртуальное наследование не предотвратит проблемы ромба, если дочерний класс `Laptop` будет наследовать класс `Device` не виртуально.

### Абстрактный класс

В C++ класс считается абстрактным, если в нем присутствует хотя бы один чистый виртуальный метод (pure virtual method). Чистый виртуальный метод объявляется с использованием синтаксиса `= 0`. Если дочерний класс не переопределяет этот метод, то код не скомпилируется. Также в C++ невозможно создать объект абстрактного класса - попытка вызвать конструктор абстрактного класса приведет к ошибке компиляции.

```c++
#include <iostream>
using namespace std;

class Device {
public:
    void turn_on() {
        cout << "Device is on." << endl;
    }
    virtual void say_hello() = 0; // Чистый виртуальный метод
};

class Laptop : public Device {
public:
    void say_hello() override { // Переопределение чистого виртуального метода
        cout << "Hello world!" << endl;
    }
};

int main() {
    Laptop laptop_instance;
    laptop_instance.turn_on();
    laptop_instance.say_hello();

    // Device device_instance; // Ошибка компиляции: нельзя создать объект абстрактного класса
    return 0;
}
```

В этом примере класс `Device` является абстрактным, потому что он содержит чистый виртуальный метод `say_hello()`. Класс `Laptop` переопределяет этот метод, что позволяет создать его экземпляр.

### Интерфейс

В C++, в отличие от некоторых других языков программирования, нет отдельного ключевого слова для объявления интерфейса. Тем не менее, интерфейс может быть реализован с помощью создания чистого абстрактного класса, который содержит только декларации методов. Такие классы часто называют абстрактными базовыми классами (Abstract Base Class - ABC).

```c++
#include <iostream>
using namespace std;

class Device {
public:
    virtual void turn_on() = 0; // Чистый виртуальный метод
};

class Laptop : public Device {
public:
    void turn_on() override { // Переопределение метода интерфейса
        cout << "Device is on." << endl;
    }
};

int main() {
    Laptop laptop_instance;
    laptop_instance.turn_on();

    // Device device_instance; // Ошибка компиляции: нельзя создать объект абстрактного класса
    return 0;
}
```

В этом примере класс `Device` является интерфейсом, так как содержит только чистые виртуальные методы. Класс `Laptop` реализует интерфейс, предоставляя реализацию метода `turn_on()`.

---

## Упражнения

##### Задача 1: Система классов для транспортов

Реализуйте систему классов, моделирующую транспортные средства. У вас должен быть базовый класс `Transport` (метод `move`), и два производных класса: `LandTransport` (метод `drive`) и `WaterTransport` (метод `sail`). Класс `AmphibiousVehicle` должен наследовать от обоих транспортных средств, представляя амфибию, которая может двигаться как по суше, так и по воде. Используйте виртуальное наследование, чтобы избежать проблем с дублированием.

##### Задача 2: Система классов для животных

Реализуйте систему классов, моделирующую животных. У вас должен быть базовый класс `Animal` с методом `speak()`. Создайте два производных класса: `Mammal` (метод `walk()`) и `Bird` (метод `fly()`). Класс `Bat` должен наследовать от обоих классов, представляя летучую мышь, которая может и говорить, и летать. Используйте виртуальное наследование для предотвращения проблем с дублированием.

##### Задача 3: Система классов для музыкальных инструментов

Создайте систему классов для музыкальных инструментов. Базовый класс `Instrument` должен иметь метод `play()`. Реализуйте два производных класса: `StringInstrument` (метод `tune()`) и `PercussionInstrument` (метод `hit()`). Класс `DrumGuitar` должен наследовать от обоих классов, представляя инструмент, который сочетает в себе функции барабана и гитары. Используйте виртуальное наследование для управления общими аспектами.

##### Задача 4: Система классов для сотрудников

Реализуйте систему классов для сотрудников компании. У вас должен быть базовый класс `Employee` с методом `work()`. Создайте два производных класса: `Manager` (метод `delegate()`) и `Developer` (метод `code()`). Класс `TechManager` должен наследовать от обоих классов, представляя менеджера, который также занимается разработкой. Используйте виртуальное наследование для упрощения доступа к общим данным.

##### Задача 5: Система классов для музыкальных исполнителей

Создайте систему классов, моделирующую музыкальных исполнителей. Базовый класс `Performer` должен иметь метод `perform()`. Реализуйте два производных класса: `SoloArtist` (метод `singSolo()`) и `Band` (метод `playTogether()`). Класс `SuperBand` должен наследовать от обоих классов, представляя музыкальную группу, которая может как выступать сольные номера, так и играть вместе. Используйте виртуальное наследование для устранения проблем с дублированием.
