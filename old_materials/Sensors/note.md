# Датчики и Сенсоры в Arduino

В этой теме студенты будут изучать различные типы датчиков и сенсоров, а также научатся подключать и программировать их с использованием Arduino. Они узнают, как считывать данные с датчиков, анализировать их и использовать полученные значения для управления другими устройствами.

Доступные сенсоры в [wokwi](https://docs.wokwi.com/getting-started/supported-hardware#sensors)
### Сенсоры
|Название|Описание|
|-|-|
|[HC-SR04](https://docs.wokwi.com/parts/wokwi-hc-sr04)|HC-SR04 Ультразвуковой датчик расстояния|
|[DHT22](https://docs.wokwi.com/parts/wokwi-dht22)|Цифровой датчик влажности и температуры|
|[DS1307 RTC](https://docs.wokwi.com/parts/wokwi-ds1307)|Модуль RTC (часы реального времени) с интерфейсом I2C и 56 байтами NV SRAM|
|[PIR Motion Sensor](https://docs.wokwi.com/parts/wokwi-pir-motion-sensor)|Пассивный инфракрасный (PIR) датчик движения|
|[Аналоговый датчик температуры (NTC)](https://docs.wokwi.com/parts/wokwi-ntc-temperature-sensor)|Аналоговый датчик температуры: NTC (отрицательный температурный коэффициент) термистор|
|DS18B20 Датчик температуры|Однопроводной цифровой датчик температуры|
|[MPU6050](https://docs.wokwi.com/parts/wokwi-mpu6050)|Интегрированный датчик с 3-осевым акселерометром, 3-осевым гироскопом и датчиком температуры с интерфейсом I2C|
|[Фоторезистор](https://docs.wokwi.com/parts/wokwi-photoresistor-sensor)|Фоторезисторный (LDR) датчик|
|[Тензодатчик HX711](https://docs.wokwi.com/parts/wokwi-hx711)|Усилитель тензодатчика HX711 с тензодатчиком 5 кг/50 кг/габариты|

#### Примеры
##### [HC-SR04](https://docs.wokwi.com/parts/wokwi-hc-sr04)
![HC-SR04](https://encrypted-tbn3.gstatic.com/images?q=tbn:ANd9GcR9l6aV2Ed3ywhdZRAaHAXhm8bgE441AUXwvvOgX7RbBLTkrUGv)
```c++
#include <SevSeg.h>

#define TRIG_PIN A3
#define ECHO_PIN A4

SevSeg sevseg;

void setup()
{
  uint8_t numDigits     = 4;
  uint8_t digitPins[]   = {2, 3, 4, 5};
  uint8_t segmentPins[] = {6, 7, 8, 9, 10, 11, 12, 13};
  uint8_t displayType   = COMMON_ANODE; // (Общий анод или общий катод)

  bool resistorsOnSegments = false;
  bool updateWithDelays    = false;
  bool leadingZeros        = false;
  bool disableDecPoint     = false;

  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);

  sevseg.begin(displayType, numDigits, digitPins, segmentPins, resistorsOnSegments,
               updateWithDelays, leadingZeros, disableDecPoint);
  sevseg.setBrightness(90);
}

void loop()
{
  static uint32_t interval = 0;
  static uint16_t duration = 0;
  static float distance    = 0;

  if ((millis() - interval) >= 100) {
    interval = millis();

    digitalWrite(TRIG_PIN, LOW);
    delayMicroseconds(5);
    digitalWrite(TRIG_PIN, HIGH);
    delayMicroseconds(10);
    digitalWrite(TRIG_PIN, LOW);

    // Чтение времени сигналов на пинах TRIG и ECHO
    duration = pulseIn(ECHO_PIN, HIGH);

    // Расчет расстояния
    distance = (duration / 2) / 29;

    sevseg.setNumber(distance);
  }
  sevseg.refreshDisplay();
}
```
-   Библиотека  `SevSeg`  используется для управления 7-сегментным дисплеем.
-   Пины  `TRIG_PIN`  и  `ECHO_PIN`  определены для подключения датчика расстояния HC-SR04.
-   В функции  `setup()`  настраиваются пины и параметры дисплея.
-   В функции  `loop()`  происходит измерение расстояния и его отображение на дисплее.
-   Переменные  `interval`,  `duration`  и  `distance`  объявлены как статические, чтобы сохранять их значения между итерациями цикла  `loop()`.
##### [DHT22](https://docs.wokwi.com/parts/wokwi-dht22)
![enter image description here](https://encrypted-tbn2.gstatic.com/images?q=tbn:ANd9GcS5AjBLD0XCzH943Tq1-cZEJSXWezCbXI0liaQ889dxi4IcThHU)
```c++
#include <dht.h>

dht DHT;

#define DHT22_PIN 5

struct {
  uint32_t total;
  uint32_t ok;
  uint32_t crc_error;
  uint32_t time_out;
  uint32_t connect;
  uint32_t ack_l;
  uint32_t ack_h;
  uint32_t unknown;
} stat = { 0, 0, 0, 0, 0, 0, 0, 0};

void setup() {
  Serial.begin(115200);
  Serial.println("dht22_test.ino");
  Serial.print("ВЕРСИЯ БИБЛИОТЕКИ: ");
  Serial.println(DHT_LIB_VERSION);
  Serial.println();
  Serial.println("Тип,\tСтатус,\tВлажность (%),\tТемпература (C)\tВремя (мкс)");
}

void loop() {
  readSensorData();
  displayData();
  delay(2000);
}

void readSensorData() {
  Serial.print("DHT22, \t");

  uint32_t start = micros();
  int chk = DHT.read22(DHT22_PIN);
  uint32_t stop = micros();

  stat.total++;
  switch (chk)
  {
    case DHTLIB_OK:
      stat.ok++;
      Serial.print("OK,\t");
      break;
    case DHTLIB_ERROR_CHECKSUM:
      stat.crc_error++;
      Serial.print("Ошибка контрольной суммы,\t");
      break;
    case DHTLIB_ERROR_TIMEOUT:
      stat.time_out++;
      Serial.print("Ошибка тайм-аута,\t");
      break;
    case DHTLIB_ERROR_CONNECT:
      stat.connect++;
      Serial.print("Ошибка подключения,\t");
      break;
    case DHTLIB_ERROR_ACK_L:
      stat.ack_l++;
      Serial.print("Ошибка ACK Low,\t");
      break;
    case DHTLIB_ERROR_ACK_H:
      stat.ack_h++;
      Serial.print("Ошибка ACK High,\t");
      break;
    default:
      stat.unknown++;
      Serial.print("Неизвестная ошибка,\t");
      break;
  }
}

void displayData() {
  Serial.print(DHT.humidity, 1);
  Serial.print(",\t");
  Serial.print(DHT.temperature, 1);
  Serial.print(",\t");
  Serial.print(stop - start);
  Serial.println();

  if (stat.total % 20 == 0)
  {
    Serial.println("\nВСЕГО\tOK\tCRC\tTO\tCON\tACK_L\tACK_H\tUNK");
    Serial.print(stat.total);
    Serial.print("\t");
    Serial.print(stat.ok);
    Serial.print("\t");
    Serial.print(stat.crc_error);
    Serial.print("\t");
    Serial.print(stat.time_out);
    Serial.print("\t");
    Serial.print(stat.connect);
    Serial.print("\t");
    Serial.print(stat.ack_l);
    Serial.print("\t");
    Serial.print(stat.ack_h);
    Serial.print("\t");
    Serial.print(stat.unknown);
    Serial.println("\n");
  }
}
```

- В данном коде используется библиотека `dht.h` для работы с датчиком `DHT22`. Код считывает данные с датчика и выводит их на последовательный порт. 
- В функции `setup()` происходит инициализация последовательного порта и вывод информации о версии библиотеки.
- В функции `loop()` происходит считывание данных с датчика и их вывод на последовательный порт. Также в функции происходит обновление статистики и вывод ее значений каждые 20 итераций.
- В функции `readSensorData()`  происходит считывание данных с датчика
- В функции `displayData()` происходит вывод данных на последовательный порт.

##### [DS1307 RTC](https://docs.wokwi.com/parts/wokwi-ds1307)

![enter image description here](https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTrW511SSmGj71ItfmHCHws_KUdEE33Urp0TYJaXj3_Q-w_Mbzw)
[Пример](https://wokwi.com/projects/376383354533106689)
```c++
#include "RTClib.h"

RTC_DS1307 rtc;

enum DaysOfTheWeek {
  Sunday,
  Monday,
  Tuesday,
  Wednesday,
  Thursday,
  Friday,
  Saturday
};

void setup() {
  Serial.begin(115200);

  if (!rtc.begin()) {
    Serial.println("Failed to find RTC");
    Serial.flush();
    abort();
  }
}

void loop() {
  DateTime now = rtc.now();

  printCurrentTime(now);

  Serial.println();
  delay(3000);
}

void printCurrentTime(DateTime now) {
  Serial.print("Current time: ");
  Serial.print(now.year(), DEC);
  Serial.print('/');
  Serial.print(now.month(), DEC);
  Serial.print('/');
  Serial.print(now.day(), DEC);
  Serial.print(" (");
  Serial.print(getDayOfWeekString(now.dayOfTheWeek()));
  Serial.print(") ");
  Serial.print(now.hour(), DEC);
  Serial.print(':');
  Serial.print(now.minute(), DEC);
  Serial.print(':');
  Serial.print(now.second(), DEC);
  Serial.println();
}

String getDayOfWeekString(int dayOfWeek) {
  switch (dayOfWeek) {
    case Sunday:
      return "Sunday";
    case Monday:
      return "Monday";
    case Tuesday:
      return "Tuesday";
    case Wednesday:
      return "Wednesday";
    case Thursday:
      return "Thursday";
    case Friday:
      return "Friday";
    case Saturday:
      return "Saturday";
    default:
      return "Invalid day";
  }
}
```
В данном коде мы используем библиотеку `RTClib` для работы с модулем `RTC (Real-Time Clock)`. Мы объявляем объект `rtc` типа `RTC_DS1307`, который представляет собой модуль `RTC DS1307`.

Функция `printCurrentTime` для печати текущего времени.

Создана отдельная функция `getDayOfWeekString` для преобразования целого числа дня недели в строковое представление.

После вывода текущего времени мы добавляем пустую строку и задержку в `3` секунды с помощью функции `delay(3000)`.

`Enums` (перечисления) используются в программировании для определения набора именованных значений. Они предоставляют способ представления фиксированного числа возможных значений переменной. В предоставленном коде перечисление `DaysOfTheWeek` используется для представления дней недели.

>Использование `enum` имеет несколько преимуществ:
>- Читабельность: перечисления делают код более читабельным и понятным. Вместо использования произвольных чисел или строк для представления значений перечисления предоставляют осмысленные имена, передающие назначение переменной.
>- Безопасность типов. Перечисления обеспечивают безопасность типов, ограничивая возможные значения, которые может принимать переменная. В случае `DaysOfTheWeek` переменная может иметь только одно из семи предопределенных значений, что предотвращает случайное присвоение недопустимых значений.
>- Ясность кода. Перечисления улучшают ясность кода, предоставляя четкий и краткий способ определения набора связанных значений. Они делают код более удобным в сопровождении и понятным для других разработчиков.
>- Согласованность кода. Перечисления помогают поддерживать согласованность во всей кодовой базе. При использовании перечислений все экземпляры определенной переменной будут иметь одинаковый набор возможных значений, что обеспечивает согласованность и снижает вероятность ошибок.

Таким образом, перечисления используются для улучшения читаемости кода, безопасности типов, ясности кода и его согласованности. Они предоставляют удобный способ определения набора связанных значений и делают код более удобным в сопровождении и понятным.

##### [PIR Motion Sensor](https://docs.wokwi.com/parts/wokwi-pir-motion-sensor)
![enter image description here](https://encrypted-tbn3.gstatic.com/images?q=tbn:ANd9GcQcilC9ybxtujejn8qcJ18-HTjwfLw8UG-wsHaF2OeFQwY1vdRi)

```c++
// Pin assignments
const int ledPin = 13;         // Pin for the LED
const int inputPin = 2;        // Pin for the PIR sensor

// Variables
int pirState = LOW;            // Assume no motion detected initially

void setup() {
  pinMode(ledPin, OUTPUT);     // Set LED pin as output
  pinMode(inputPin, INPUT);    // Set PIR sensor pin as input

  Serial.begin(9600);          // Initialize serial communication
}

void loop() {
  int val = digitalRead(inputPin);  // Read input value from PIR sensor

  if (val == HIGH) {                 // Check if motion is detected
    digitalWrite(ledPin, HIGH);      // Turn on the LED

    if (pirState == LOW) {
      // Motion has just been detected
      Serial.println("Motion detected!");
      pirState = HIGH;
    }
  } else {
    digitalWrite(ledPin, LOW);       // Turn off the LED

    if (pirState == HIGH) {
      // Motion has just ended
      Serial.println("Motion ended!");
      pirState = LOW;
    }
  }
}
```
Предоставленный код представляет собой простой тестер датчика `PIR` (пассивного инфракрасного излучения). Он использует `PIR`-датчик для обнаружения движения и включает светодиод при обнаружении движения.

- Назначение контактов выполнено для светодиода и `PIR`-датчика.
- Функция `setup()` вызывается один раз в начале программы. Он устанавливает контакт светодиода как выход, а контакт `PIR`-датчика как вход. Он также инициализирует последовательную связь.
- Функция `loop()` вызывается неоднократно. Он считывает входное значение с `PIR`-датчика с помощью функции `digitalRead()`.
- Если обнаружено движение (входное значение `HIGH`), светодиод включается с помощью функции `digitalWrite()`. 
- - Если переменная `pirState` имеет значение `LOW`, это означает, что движение только что было обнаружено. В этом случае появится сообщение `«Обнаружено движение!»` выводится на последовательный монитор с помощью функции `Serial.println()`, а переменная `pirState` обновляется до `HIGH`.
- Если движение не обнаружено (входное значение `LOW`), светодиод выключается. 
- - Если переменная `pirState` имеет значение `HIGH`, это означает, что движение только что закончилось. В этом случае появится сообщение «Движение окончено!» выводится на последовательный монитор, а переменная `pirState` обновляется до `LOW`.

> Этот код позволяет вам проверить функциональность PIR-датчика, наблюдая за включением и выключением светодиода при обнаружении движения.

##### [Analog Temperature Sensor (NTC)](https://docs.wokwi.com/parts/wokwi-ntc-temperature-sensor)
![enter image description here](https://encrypted-tbn1.gstatic.com/images?q=tbn:ANd9GcSS52ak31zk8tfxUCX-otlFVeWYrInveESPScd7Pj7vDHTNSaq5)
[Пример](https://wokwi.com/projects/376383375187961857)
```c++
/**
  Basic NTC Thermistor demo
  https://wokwi.com/arduino/projects/299330254810382858

  Assumes a 10K@25℃ NTC thermistor connected in series with a 10K resistor.

  Copyright (C) 2021, Uri Shaked
*/

const float BETA = 3950; // should match the Beta Coefficient of the thermistor

void setup() {
  Serial.begin(9600);
}

void loop() {
  int analogValue = analogRead(A0);
  float celsius = calculateTemperature(analogValue);
  printTemperature(celsius);
  delay(1000);
}

float calculateTemperature(int analogValue) {
  float resistance = 1023.0 / analogValue - 1;
  resistance = 10000.0 / resistance;
  float steinhart;
  steinhart = resistance / 10000.0; // (R/Ro)
  steinhart = log(steinhart); // ln(R/Ro)
  steinhart /= BETA; // 1/B * ln(R/Ro)
  steinhart += 1.0 / 298.15; // + (1/To)
  steinhart = 1.0 / steinhart; // Invert
  steinhart -= 273.15; // Convert to Celsius
  return steinhart;
}

void printTemperature(float celsius) {
  Serial.print("Temperature: ");
  Serial.print(celsius);
  Serial.println(" ℃");
}
```
- Код считывает аналоговое значение с контакта `A0`, который подключен к термистору `NTC`. Термистор `NTC` — это тип резистора, сопротивление которого меняется в зависимости от температуры. Измерив сопротивление термистора, мы можем рассчитать температуру.

- Код предполагает, что термистор `NTC`  имеет значение 10K при 25℃ подключен последовательно с резистором 10K. Значение константы `beta` должно соответствовать коэффициенту бета используемого термистора.

- В функции настройки код инициализирует последовательную связь со скоростью `9600` бод.

- В функции цикла код считывает аналоговое значение с контакта `A0`, используя функцию `AnalogRead`. Затем он вызывает функцию `CalculTemperature` для преобразования аналогового значения в температуру в градусах Цельсия. Рассчитанная температура затем передается в функцию `printTemperature`, которая выводит ее на последовательный монитор.

- Затем код ждет 1 секунду, используя функцию задержки, прежде чем повторить процесс.

В целом, этот код демонстрирует базовую реализацию измерения температуры с использованием термистора `NTC` и `Arduino`. Его можно использовать в качестве отправной точки для более продвинутых проектов по измерению температуры.
##### DS18B20 Temperature Sensor
![enter image description here](data:image/jpeg;base64,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)

[Пример](https://wokwi.com/projects/376383156031357953)
```c++
#include <OneWire.h>
#include <DallasTemperature.h>

// Data wire is connected to the Arduino digital pin 4
#define ONE_WIRE_BUS 4

// Setup a oneWire instance to communicate with any OneWire devices
OneWire oneWire(ONE_WIRE_BUS);

// Pass our oneWire reference to the Dallas Temperature sensor 
DallasTemperature sensors(&oneWire);

void setup(void)
{
  // Start serial communication for debugging purposes
  Serial.begin(9600);
  
  // Start up the library
  sensors.begin();
}

void loop(void)
{ 
  // Call sensors.requestTemperatures() to issue a global temperature request to all devices on the bus
  sensors.requestTemperatures(); 
  
  Serial.print("Celsius temperature: ");
  // Why "byIndex"? You can have more than one IC on the same bus. 0 refers to the first IC on the wire
  Serial.print(sensors.getTempCByIndex(0)); 
  Serial.print(" - Fahrenheit temperature: ");
  Serial.println(sensors.getTempFByIndex(0));
  
  delay(1000);
}
```
Этот код используется для считывания данных о температуре с датчика температуры Далласа, подключенного к плате Arduino. Вот как это работает:

- В код включены необходимые библиотеки: `OneWire` и `DallasTemperature`.
- Провод данных датчика подключен к цифровому контакту `4` `Arduino` (`#define ONE_WIRE_BUS 4`).
- Создается экземпляр класса `OneWire`, которому в качестве параметра передается вывод провода передачи данных.
- Создается экземпляр класса `DallasTemperature`, которому передается экземпляр `OneWire` в качестве параметра.
- В функции `setup()` для целей отладки запускается последовательная связь со скоростью 9600 бод. Также инициализируется библиотека `DallasTemperature`.
- В функции `loop()` вызывается функция `Sensors.requestTemperatures()` для выдачи глобального запроса температуры всем устройствам на шине.
- Температура в градусах Цельсия получается с помощью` Sensors.getTempCByIndex(0)` и выводится на последовательный монитор.
- Температура в градусах Фаренгейта получается с помощью `Sensors.getTempFByIndex(0)` и выводится на последовательный монитор.
- Затем программа ждет 1 секунду, прежде чем повторить процесс.

Этот код позволяет считывать данные о температуре с датчика температуры Далласа и отображать их на последовательном мониторе.

##### [MPU6050](https://docs.wokwi.com/parts/wokwi-mpu6050)
![enter image description here](https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcS2lL3TZJwQo8TY5aQGAQrxbPAFCUidBkYQO7_kZYLUGN2T18XU)

[Пример](https://wokwi.com/projects/376383475393036289)
```c++
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <Wire.h>

Adafruit_MPU6050 mpu;

void setup() {
  Serial.begin(115200);

  if (!mpu.begin()) {
    Serial.println("Failed to find MPU6050 chip");
    while (1) {
      delay(10);
    }
  }

  mpu.setAccelerometerRange(MPU6050_RANGE_16_G);
  mpu.setGyroRange(MPU6050_RANGE_250_DEG);
  mpu.setFilterBandwidth(MPU6050_BAND_21_HZ);

  Serial.println("");
  delay(100);
}

void loop() {
  sensors_event_t a, g, temp;
  mpu.getEvent(&a, &g, &temp);

  Serial.print(a.acceleration.x);
  Serial.print(",");
  Serial.print(a.acceleration.y);
  Serial.print(",");
  Serial.print(a.acceleration.z);
  Serial.print(", ");
  Serial.print(g.gyro.x);
  Serial.print(",");
  Serial.print(g.gyro.y);
  Serial.print(",");
  Serial.print(g.gyro.z);
  Serial.println("");

  delay(10);
}
```
Этот код используется для взаимодействия с датчиком `MPU6050` и считывания значений его акселерометра и гироскопа. `MPU6050` — широко используемый датчик для измерения движения и ориентации.

- Необходимые библиотеки включены в начале кода. Эти библиотеки предоставляют функции и определения для работы с датчиком `MPU6050` и связью `I2C`.

- Функция `setup()` вызывается один раз в начале программы. Он инициализирует последовательную связь со скоростью `115200` бод и проверяет, обнаружен ли чип `MPU6050`. Если чип не найден, на последовательный монитор выводится сообщение об ошибке.

- Диапазоны датчиков и полоса пропускания фильтра устанавливаются с помощью функций `mpu.setAccelerometerRange()`, `mpu.setGyroRange()` и `mpu.setFilterBandwidth()`. Эти функции настраивают датчик для измерения движения в определенных диапазонах и фильтрации шума.

- Функция `loop()` вызывается повторно после функции `setup()`. Он считывает значения акселерометра и гироскопа с датчика `MPU6050` с помощью функции `mpu.getEvent()`. Значения датчика хранятся в переменных `a (акселерометр)`, `g (гироскоп)` и `temp (температура)`.

- Значения акселерометра и гироскопа выводятся на последовательный монитор с помощью функций `Serial.print()` и `Serial.println()`. Значения разделяются запятыми, чтобы их было легче читать и анализировать.

- Задержка в `10` миллисекунд добавляется с помощью функции `delay()` для управления скоростью, с которой данные датчика считываются и распечатываются. Эта задержка гарантирует, что программа не перегружает последовательный монитор данными.

Запустив этот код на плате `Arduino`, подключенной к датчику `MPU6050`, вы сможете увидеть значения акселерометра и гироскопа в реальном времени в последовательном мониторе. Это может быть полезно для мониторинга движения и ориентации в различных приложениях, таких как робототехника, дроны и системы отслеживания движения.

##### [Photoresistor](https://docs.wokwi.com/parts/wokwi-photoresistor-sensor)
![enter image description here](https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSP_Z8s3g1Rp1p_hN763JlyuxQFaKRmeaGUWgr_qHqjUr6cyRpv)
```c++
// Include the LiquidCrystal_I2C library
#include <LiquidCrystal_I2C.h>

// Define the pin for the Light Dependent Resistor (LDR)
#define LDR_PIN 2

// Create an instance of the LiquidCrystal_I2C class
LiquidCrystal_I2C lcd(0x27, 20, 4);

// Setup function runs once at the start of the program
void setup() {
  // Set the LDR pin as an input
  pinMode(LDR_PIN, INPUT);
  
  // Initialize the LCD
  lcd.init();
  
  // Turn on the backlight of the LCD
  lcd.backlight();
}

// Loop function runs repeatedly after the setup function
void loop() {
  // Set the cursor position on the LCD
  lcd.setCursor(2, 0);
  
  // Print the label for the light level
  lcd.print("Room: ");
  
  // Check the light level using the LDR pin
  if (digitalRead(LDR_PIN) == LOW) {
    // If the light level is low, print "Light!"
    lcd.print("Light!");
  } else {
    // If the light level is high, print "Dark"
    lcd.print("Dark  ");
  }
  
  // Delay for a short period of time
  delay(100);
}
```
Код использует библиотеку `LiquidCrystal_I2C` для управления ЖК-экраном, подключенным к плате Arduino. ЖК-экран представляет собой дисплей размером `20х4` символа.

- В функции `setup()` код устанавливает вывод `LDR` в качестве входа и инициализирует ЖК-экран. Также включается подсветка ЖК-дисплея.

- В функции `loop()` код постоянно проверяет уровень освещенности, используя вывод `LDR`. Если уровень освещенности низкий (темная комната), печатается `«Свет!»` на ЖК-экране. Если уровень освещенности высокий (яркая комната), на ЖК-экране отображается надпись `«Темно»`. Позиция курсора устанавливается на `(2, 0)` для отображения текста во втором столбце первой строки.

- Функция `delay (100)` используется для введения небольшой задержки в `100` миллисекунд между каждой итерацией цикла. Это предотвращает слишком быстрое обновление ЖК-экрана и обеспечивает более читаемое изображение.

В целом, код позволяет контролировать уровень освещенности в комнате с помощью `LDR` и отображать результат на ЖК-экране.

##### [HX711 Load Cell](https://docs.wokwi.com/parts/wokwi-hx711)
![enter image description here](https://encrypted-tbn3.gstatic.com/images?q=tbn:ANd9GcRbqLJ5-56A3p_uWIiPhuxqFJo3OvTvlITXmm1OsDAfymLsx2l6)
[Пример](https://wokwi.com/projects/344192176616374868)
```c++
#include "HX711.h"

HX711 scale;

void setup() {
  Serial.begin(9600);
  Serial.println("HX710B Demo with HX711 Library");
  Serial.println("Initializing the scale");

  scale.begin(A1, A0);

  Serial.println("Before setting up the scale:");
  Serial.print("read: \t\t");
  Serial.println(scale.read());
  Serial.print("read average: \t\t");
  Serial.println(scale.read_average(20));
  Serial.print("get value: \t\t");
  Serial.println(scale.get_value(5));
  Serial.print("get units: \t\t");
  Serial.println(scale.get_units(5), 1);

  scale.set_scale(2280.f);
  scale.tare();

  Serial.println("After setting up the scale:");
  Serial.print("read: \t\t");
  Serial.println(scale.read());
  Serial.print("read average: \t\t");
  Serial.println(scale.read_average(20));
  Serial.print("get value: \t\t");
  Serial.println(scale.get_value(5));
  Serial.print("get units: \t\t");
  Serial.println(scale.get_units(5), 1);

  Serial.println("Readings:");
}

void loop() {
  Serial.print("one reading:\t");
  Serial.print(scale.get_units(), 1);
  Serial.print("\t| average:\t");
  Serial.println(scale.get_units(10), 1);
  scale.power_down();
  delay(5000);
  scale.power_up();
}
```
Приведенный код является примером использования библиотеки HX711 с платой Arduino для считывания данных с датчика давления. Код инициализирует весы, устанавливает необходимые контакты и выполняет различные операции по чтению и отображению данных датчика.

- Подключите необходимую библиотеку:
`#include "HX711.h"`

Создайте экземпляр класса HX711:
`HX711 scale;`

Настройте плату Arduino:
```c++
void setup() {
  Serial.begin(9600);
  Serial.println("HX710B Demo with HX711 Library");
  Serial.println("Initializing the scale");

  scale.begin(A1, A0);
}
```

Перед настройкой весов выполните операции:
```c++
  Serial.println("Before setting up the scale:");
  Serial.print("read: \t\t");
  Serial.println(scale.read());
  Serial.print("read average: \t\t");
  Serial.println(scale.read_average(20));
  Serial.print("get value: \t\t");
  Serial.println(scale.get_value(5));
  Serial.print("get units: \t\t");
  Serial.println(scale.get_units(5), 1);

```
Установите весы и тарируйте вес:
```c++
  scale.set_scale(2280.f);
  scale.tare();
```
Выполните операции после настройки весов:
```c++
  Serial.println("After setting up the scale:");
  Serial.print("read: \t\t");
  Serial.println(scale.read());
  Serial.print("read average: \t\t");
  Serial.println(scale.read_average(20));
  Serial.print("get value: \t\t");
  Serial.println(scale.get_value(5));
  Serial.print("get units: \t\t");
  Serial.println(scale.get_units(5), 1);

```

Чтение и отображение данных датчика в цикле:
```c++
void loop() {
  Serial.print("one reading:\t");
  Serial.print(scale.get_units(), 1);
  Serial.print("\t| average:\t");
  Serial.println(scale.get_units(10), 1);
  scale.power_down();
  delay(5000);
  scale.power_up();
}
```

В цикле код непрерывно считывает данные датчика и выводит их на последовательный монитор. Он также переводит АЦП в спящий режим на 5 секунд, а затем снова его пробуждает.

## Устройства ввода
|Название|Описание|
|-|-|
|[Кнопка](https://docs.wokwi.com/parts/wokwi-pushbutton)|12 мм Тактильная кнопка-переключатель (кратковременная кнопка)|
|[Ползунковый переключатель](https://docs.wokwi.com/parts/wokwi-slide-switch)|Стандартный однополюсный двухпозиционный (SPDT) ползунковый переключатель|
|[DIP-переключатель 8](https://docs.wokwi.com/parts/wokwi-dip-switch-8)|Набор из 8 электрических переключателей в одном корпусе|
|[Клавиатура](https://docs.wokwi.com/parts/wokwi-membrane-keypad)|Стандартная клавиатура 4х4 (для ввода цифр)|
|[Аналоговый джойстик](https://docs.wokwi.com/parts/wokwi-analog-joystick)|Аналоговый джойстик с двумя осями (горизонтальная/вертикальная) и встроенной кнопкой|
|[Потенциометр](https://docs.wokwi.com/parts/wokwi-potentiometer)|Переменный резистор с ручкой управления (линейный потенциометр)|
|[Ползунковый потенциометр](https://docs.wokwi.com/parts/wokwi-slide-potentiometer)| Ползунковый переменный резистор (линейный потенциометр)|
|[Поворотный энкодер (KY-040)](https://docs.wokwi.com/parts/wokwi-ky-040)|Модуль поворотного энкодера KY-040 с 20 шагами на оборот.|
#### Примеры
![enter image description here](https://encrypted-tbn1.gstatic.com/images?q=tbn:ANd9GcQs0VDZtizxO2zW3vW1qJc3X-JhV3rBbxLp5O2C28xo_MZbz3PL)
##### [Кнопка](https://docs.wokwi.com/parts/wokwi-pushbutton)
[Пример](https://wokwi.com/projects/376384296063241217)
```c++
// Button Bounce counter
// 
// Red button has bouncing simulation enabled,
// Blue button has bouncing simulation disabled.

#define BUTTON_PIN 4

void setup() {
  Serial.begin(115200);
  pinMode(BUTTON_PIN, INPUT_PULLUP);
}

int lastState = HIGH;
void loop() {
  int value = digitalRead(BUTTON_PIN);
  if (lastState != value) {
    lastState = value;
    if (value == HIGH) {
      Serial.println("Button released");
    }
    if (value == LOW) {
      Serial.println("Button pressed");
    }
  }
}

```

Предоставленный код представляет собой простой пример устранения дребезга кнопок в `Arduino` с использованием `C++`. Устранение дребезга кнопок — это метод, используемый для устранения ложных показаний, вызванных механическими переключателями или кнопками, которые могут вызывать множественные быстрые переходы между состояниями `HIGH` и `LOW` при нажатии или отпускании.

В этом коде у нас есть кнопка, подключенная к контакту `4` платы `Arduino`. Кнопка настроена как `INPUT_PULLUP`, что означает, что, когда кнопка не нажата, вывод внутренне переводится в состояние `HIGH`. Когда кнопка нажата, штифт переводится в `LOW` состояние.

Переменная `LastState` используется для отслеживания предыдущего состояния кнопки. В функции `loop()` мы читаем текущее состояние кнопки с помощью функции `digitalRead()`. Если текущее состояние отличается от предыдущего, это означает, что кнопка была нажата или отпущена.

Если текущее состояние `HIGH`, это означает, что кнопка отпущена, и мы печатаем «Кнопка отпущена» на последовательном мониторе. Если текущее состояние `LOW`, это означает, что кнопка была нажата, и мы печатаем `«Кнопка нажата»` на последовательном мониторе.

##### [Ползунковый переключатель](https://docs.wokwi.com/parts/wokwi-slide-switch)
![enter image description here](https://encrypted-tbn3.gstatic.com/images?q=tbn:ANd9GcRrmwV4eB3MNaF1jrjMEwc6lIK7BUcerNS8KPrcKPlaP9oIWD3f)
Использование полузнкового переключателя для включения и выключения светодиода.
[Пример](https://wokwi.com/projects/376384660866004993)
```c++
// Define the pin numbers
const int LED_PIN = LED_BUILTIN;
const int SWITCH_PIN = 5;

void setup() {
  // Set the LED pin as an output
  pinMode(LED_PIN, OUTPUT);
  
  // Set the switch pin as an input with pull-up resistor enabled
  pinMode(SWITCH_PIN, INPUT_PULLUP);
}

void loop() {
  // Read the state of the switch
  int switchState = digitalRead(SWITCH_PIN);
  
  // Turn on the LED if the switch is pressed (LOW state)
  if (switchState == LOW) {
    digitalWrite(LED_PIN, HIGH);
  } else {
    digitalWrite(LED_PIN, LOW);
  }
}
```
Код представляет собой простую демонстрацию ползункового переключателя на плате `Arduino`. Он управляет светодиодом в зависимости от состояния переключателя. Вот как это работает:

В функции настройки код устанавливает вывод светодиода (`LED_PIN`) как выход, а контакт переключателя (`SWITCH_PIN`) как вход с включенным подтягивающим резистором. Эта конфигурация подготавливает контакты для считывания состояния переключателя и управления светодиодом.

В функции цикла код считывает состояние переключателя с помощью функции `digitalRead` и сохраняет его в переменной `switchState`.

Если переключатель нажат (состояние `LOW`), код устанавливает вывод светодиода в `HIGH` уровень с помощью функции `digitalWrite`. Это включит светодиод.

Если переключатель не нажат (состояние `HIGH`), код устанавливает вывод светодиода в состояние `LOW` с помощью функции `digitalWrite`. Это выключит светодиод.

 Использование одного полузункового переключателя для управления состоянием двух свтодиодов
 [Пример](https://wokwi.com/projects/376384674535243777)
```c++
const int LED_PIN = LED_BUILTIN;
const int SWITCH_PIN_1 = 5;
const int SWITCH_PIN_2 = 6;

void setup() {
  pinMode(LED_PIN, OUTPUT);
  pinMode(SWITCH_PIN_1, INPUT_PULLUP);
  pinMode(SWITCH_PIN_2, INPUT_PULLUP);
}

void loop() {
  digitalWrite(LED_PIN, digitalRead(SWITCH_PIN_1));
  digitalWrite(SWITCH_PIN_2, digitalRead(SWITCH_PIN_2));
}
```
`const int LED_PIN = LED_BUILTIN;` : эта строка создает постоянную переменную `LED_PIN` и назначает ее встроенному выводу светодиода на плате `Arduino`.

`const int SWITCH_PIN_1 = 5;` : Эта строка создает постоянную переменную `SWITCH_PIN_1` и присваивает ей значение 5.

`const int SWITCH_PIN_2 = 6;`: Эта строка создает постоянную переменную `SWITCH_PIN_2` и присваивает ей значение 6.

`void setup() { ... }` : это специальная функция в `Arduino`, которая автоматически вызывается один раз в начале программы. Он устанавливает режим вывода для `LED_PIN`, `SWITCH_PIN_1` и `SWITCH_PIN_2`. `pinMode` используется для указания того, будет ли вывод использоваться в качестве ввода или вывода.

`pinMode(LED_PIN, OUTPUT);`: В функции `setup()` эта строка устанавливает `LED_PIN` в качестве выходного контакта. Это означает, что `Arduino` может отправлять сигналы (высокие или низкие) для включения или выключения светодиода с помощью этого контакта.

`pinMode(SWITCH_PIN_1, INPUT_PULLUP);`: В функции `setup()` эта строка устанавливает `SWITCH_PIN_1` в качестве входного контакта с режимом подтягивающего резистора. Это означает, что Arduino будет считывать состояние переключателя, подключенного к этому выводу. Когда переключатель нажат, контакт будет подключен к земле.

`pinMode(SWITCH_PIN_2, INPUT_PULLUP);` : В функции `setup()` эта строка устанавливает `SWITCH_PIN_2` в качестве входного контакта с режимом подтягивающего резистора. Подобно `SWITCH_PIN_1`, он будет использоваться для чтения состояния другого коммутатора.

`void Loop() { ... }` : это еще одна специальная функция в `Arduino`, которая автоматически вызывается после `setup()`. Он запускается повторно, пока `Arduino` включен.

`digitalWrite(LED_PIN, digitalRead(SWITCH_PIN_1));` : В функции `loop()` эта строка считывает состояние `SWITCH_PIN_1` и устанавливает состояние `LED_PIN` в это значение. Это означает, что когда `SWITCH_PIN_1` подключен к земле (переключатель нажат), светодиод на `LED_PIN` загорится.

`digitalWrite(SWITCH_PIN_2, digitalRead(SWITCH_PIN_2));`: В функции `loop()` эта строка считывает состояние `SWITCH_PIN_2` и устанавливает состояние `SWITCH_PIN_2` в это значение. Кажется, в этой строке есть ошибка, так как она должна быть `digitalWrite(LED_PIN, digitalRead(SWITCH_PIN_2));` если намерение состоит в том, чтобы управлять светодиодом с помощью `SWITCH_PIN_2`.


Один свич два светодиода 
[Пример](https://wokwi.com/projects/376384692587531265)
```c++
// the setup function runs once when you press reset or power the board
void setup() {
  // initialize digital pin LED_BUILTIN as an output.
  pinMode(LED_BUILTIN, OUTPUT);
}

// the loop function runs over and over again forever
void loop() {
  digitalWrite(LED_BUILTIN, HIGH);   // turn the LED on (HIGH is the voltage level)
  delay(1000);                       // wait for a second
  digitalWrite(LED_BUILTIN, LOW);    // turn the LED off by making the voltage LOW
  delay(1000);                       // wait for a second
}
```
В функции `setup()` мы инициализируем вывод `LED_BUILTIN` как выходной, используя функцию `pinMode()`. Это устанавливает режим вывода на ВЫХОД, что позволяет нам управлять светодиодом, подключенным к этому выводу.

В функции `loop()` мы используем функцию `digitalWrite()` для включения светодиода, установив уровень напряжения на выводе `LED_BUILTIN` на `HIGH`. Затем мы используем функцию `delay()`, чтобы приостановить программу на 1 секунду.

После задержки мы снова используем `digitalWrite()`, чтобы выключить светодиод, установив уровень напряжения на выводе `LED_BUILTIN` на `LOW`. Затем у нас есть еще одна задержка в 1 секунду, прежде чем цикл повторится, в результате чего светодиод будет постоянно мигать.

Этот код можно использовать в качестве отправной точки для более сложных проектов `Arduino`, которые включают управление светодиодами или другими цифровыми выходами.

##### [DIP-переключатель 8](https://docs.wokwi.com/parts/wokwi-dip-switch-8)
![enter image description here](https://encrypted-tbn2.gstatic.com/images?q=tbn:ANd9GcTDSbZTGCxULgm23vqg1mIs5ztrpHx5d_BJm_ZDXjRBBhnYdX9j)
DIP-переключатель 8 это механическое устройство, позволяющее установить одно из восьми возможных положений контактов. Это полезное устройство для управления различными функциями в проектах с Arduino.

DIP-переключатель 8 имеет восемь контактов, которые могут быть подключены к цифровым пинам Arduino. Каждый контакт может быть подключен либо к питанию (HIGH) для активации, либо к земле (LOW) для деактивации.

Для подключения DIP-переключателя 8 к Arduino выполните следующие шаги:

1.  Определите цифровые пины Arduino, к которым будут подключены контакты DIP-переключателя. Например, пины 2-9.
2.  Подключите первый контакт DIP-переключателя к пину 2, второй контакт к пину 3 и так далее.
3.  Подключите другой конец каждого контакта на DIP-переключателе к питанию (VCC) или земле (GND) на Arduino в зависимости от того, какое положение вы хотите установить.
4.  При необходимости, установите внутренние подтягивающие резисторы для каждого пина в режиме INPUT_PULLUP с помощью функции  `pinMode(pin, INPUT_PULLUP)`  в функции  `setup()`.
[Пример](https://wokwi.com/projects/376384858008800257)
```c++
#include <LiquidCrystal_I2C.h>

LiquidCrystal_I2C lcd(0x27, 16, 2);

void setup() {
  lcd.init();
  lcd.backlight();
  lcd.println("PIND value:");
  
  for (int i = 0; i < 8; i++) {
    pinMode(i, INPUT_PULLUP);
  }
}

int previousValue = -1;

void loop() {
  int currentValue = PIND;
  
  if (currentValue != previousValue) {
    lcd.setCursor(6, 1);
    lcd.print(currentValue);
    lcd.print("   ");
    previousValue = currentValue;
  }
}
```

Пример использования DIP-8 для арифметических опреаций над цифрами в бинарном виде
```c++
// Required Libraries
#include <ShiftPWM.h>

// Pin Definitions
#define NUMBER1_PIN 2
#define NUMBER2_PIN 3
#define SHIFT_REGISTER_DATA_PIN 4
#define SHIFT_REGISTER_CLOCK_PIN 5
#define SHIFT_REGISTER_LATCH_PIN 6

// Variables
int number1;
int number2;
int result;

// ShiftPWM Object
ShiftPWM pwm;

void setup() {
  // Configure Arduino pins
  pinMode(NUMBER1_PIN, INPUT);
  pinMode(NUMBER2_PIN, INPUT);
  pinMode(SHIFT_REGISTER_DATA_PIN, OUTPUT);
  pinMode(SHIFT_REGISTER_CLOCK_PIN, OUTPUT);
  pinMode(SHIFT_REGISTER_LATCH_PIN, OUTPUT);

  // Initialize ShiftPWM
  pwm.Start(16);
}

void loop() {
  // Read the values of number1 and number2
  number1 = digitalRead(NUMBER1_PIN);
  number2 = digitalRead(NUMBER2_PIN);

  // Perform addition, subtraction, multiplication, and division operations
  result = number1 + number2;
  // result = number1 - number2;
  // result = number1 * number2;
  // result = number1 / number2;

  // Output the result to the serial monitor
  Serial.begin(9600);
  Serial.print("Result: ");
  Serial.println(result);

  // Display the result on the LEDs using the shift register
  pwm.SetOne(0, result & 0x01);
  pwm.SetOne(1, (result >> 1) & 0x01);
  pwm.SetOne(2, (result >> 2) & 0x01);
  pwm.SetOne(3, (result >> 3) & 0x01);
  pwm.SetOne(4, (result >> 4) & 0x01);
  pwm.SetOne(5, (result >> 5) & 0x01);
  pwm.SetOne(6, (result >> 6) & 0x01);
  pwm.SetOne(7, (result >> 7) & 0x01);

  // Update the shift register
  digitalWrite(SHIFT_REGISTER_LATCH_PIN, LOW);
  shiftOut(SHIFT_REGISTER_DATA_PIN, SHIFT_REGISTER_CLOCK_PIN, MSBFIRST, pwm.GetRegister());
  digitalWrite(SHIFT_REGISTER_LATCH_PIN, HIGH);
}
```
Чтобы выполнить операции сложения, вычитания, умножения и деления, вы можете раскомментировать соответствующие строки кода и закомментировать другие операции. Обязательно отрегулируйте номера контактов и другие переменные в соответствии с соединениями вашей схемы.

Для работы со сдвиговыми регистрами вы можете использовать библиотеку `ShiftPWM` или любую другую подобную библиотеку по вашему выбору. Обязательно установите библиотеку и включите ее в свой код.

Для работы с последовательным монитором вы можете настроить скорость передачи данных с помощью функции `Serial.begin()` и распечатать результаты операции с помощью функций `Serial.print()` или `Serial.println()`.

##### [Клавиатура](https://docs.wokwi.com/parts/wokwi-membrane-keypad)
Клавиатура является входным устройством, которое позволяет вводить данные в микроконтроллер Arduino. Использование клавиатуры с Arduino позволяет создать интерактивные проекты, такие как управление роботами, игры, парольные замки и другие системы с вводом данных.
![enter image description here](https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTbv3l9l1SHqALTr4817u12cAYZ1DUA2--AWaBur2EfMB0hAOfi)
###### Подключение клавиатуры

Клавиатура подключается к Arduino с использованием протокола PS/2 или USB. В случае протокола PS/2, вам понадобится адаптер для подключения клавиатуры к Arduino.

Для подключения клавиатуры с использованием протокола PS/2, выполните следующие шаги:

1.  Подключите клавиатуру к адаптеру PS/2.
2.  Подключите адаптер PS/2 к Arduino используя цифровые пины.
3.  Подключите VCC клавиатуры к 5V на Arduino.
4.  Подключите GND клавиатуры к GND на Arduino.

Для подключения клавиатуры с использованием протокола USB, выполните следующие шаги:

1.  Подключите USB кабель клавиатуры к USB-порту на Arduino.
2.  Если ваша клавиатура имеет дополнительные разъемы, проверьте документацию к вашей клавиатуре для необходимых подключений.
###### Использование клавиатуры

После успешного подключения клавиатуры к Arduino, вы можете использовать ее для считывания ввода и реагирования на нажатия клавиш.

Подключите клавиатуру к Arduino и выполните следующие шаги:

1.  Включите библиотеку Keyboard в верхней части кода:

```cpp
#include <Keyboard.h>

```

2.  В функции  `setup()`, вызовите функцию  `Keyboard.begin()`  для инициализации клавиатуры:

```cpp
void setup() {
  Keyboard.begin();
}

```

3.  В функции  `loop()`, используйте функцию  `Keyboard.write()`  для отправки символов на компьютер:

```cpp
void loop() {
  char character = 'A'; // Пример символа для отправки
  Keyboard.write(character);
}

```

4.  Загрузите код на Arduino и откройте программу, которая будет принимать ввод от клавиатуры. Вы должны видеть, что символ 'A' появляется в поле ввода программы.

###### Обработка нажатий клавиш

Помимо отправки символов на компьютер, вы также можете обрабатывать нажатия клавиш на Arduino и выполнить соответствующие действия.

1.  В функции  `loop()`, используйте функцию  `Keyboard.available()`  для проверки, есть ли доступные символы:

```cpp
void loop() {
  if (Keyboard.available()) {
    char character = Keyboard.read();
    // Обрабатывайте символ
  }
}

```

2.  Внутри блока кода, обрабатывайте символы в соответствии с вашей логикой:

```cpp
void loop() {
  if (Keyboard.available()) {
    char character = Keyboard.read();
    // Обрабатывайте символ
    if (character == 'A') {
      // Выполните действия для символа 'A'
    } else if (character == 'B') {
      // Выполните действия для символа 'B'
    }
  }
}

```

3.  Загрузите код на Arduino и проверьте, что ваша логика обрабатывает нажатия клавиш правильно.
[Пример](https://wokwi.com/projects/376450450215521281)
```c++
#include <Keypad.h>

const uint8_t ROWS = 4;
const uint8_t COLS = 4;
char keys[ROWS][COLS] = {
  { '1', '2', '3', 'A' },
  { '4', '5', '6', 'B' },
  { '7', '8', '9', 'C' },
  { '*', '0', '#', 'D' }
};

uint8_t colPins[COLS] = { 5, 4, 3, 2 }; // Pins connected to C1, C2, C3, C4
uint8_t rowPins[ROWS] = { 9, 8, 7, 6 }; // Pins connected to R1, R2, R3, R4

Keypad keypad = Keypad(makeKeymap(keys), rowPins, colPins, ROWS, COLS);

void setup() {
  Serial.begin(9600);
}

void loop() {
  char key = keypad.getKey();

  if (key != NO_KEY) {
    Serial.println(key);
  }
}
```
Этот код генерирует программу `Arduino`, которая использует библиотеку клавиатуры для считывания ввода с матричной клавиатуры `4x4`. Клавиатура состоит из `16` клавиш, расположенных в сетке `4х4`. Каждая клавиша представлена символом в массиве ключей.

Массив `colPins` определяет контакты `Arduino`, подключенные к столбцам клавиатуры, а массив `rowPins` определяет контакты, подключенные к строкам. Эти конфигурации контактов позволяют Arduino сканировать клавиатуру и определять, какая клавиша нажата.

В функции `setup()` программа инициализирует последовательную связь со скоростью `9600` бод. Это позволяет Arduino взаимодействовать с компьютером через последовательный порт.

Функция `loop()` постоянно проверяет нажатия клавиш, используя функцию `getKey()` из библиотеки клавиатуры. Если клавиша нажата, ее значение сохраняется в ключевой переменной. Затем программа проверяет, не равна ли ключевая переменная `NO_KEY`, что указывает на то, что произошло правильное нажатие клавиши. Если обнаружено правильное нажатие клавиши, программа печатает значение ключа на последовательном мониторе с помощью функции `Serial.println()`.

##### [Аналоговый джойстик](https://docs.wokwi.com/parts/wokwi-analog-joystick)
Джойстик - это устройство ввода, которое позволяет контролировать движение объектов в проектах с Arduino. Использование джойстика позволяет создавать интерактивные проекты, такие как игры, роботы и другие устройства, которые требуют точного управления.

###### Подключение джойстика

Джойстик обычно имеет 3 оси (X, Y, Z) и кнопку. Для подключения джойстика к Arduino, выполните следующие шаги:

1.  Подключите ось X джойстика к аналоговому пину на Arduino (например, A0).
2.  Подключите ось Y джойстика к аналоговому пину на Arduino (например, A1).
3.  Подключите кнопку джойстика к цифровому пину на Arduino (например, 2).
4.  Подключите GND джойстика к GND на Arduino.
5.  Подключите VCC (+5V) джойстика к 5V на Arduino.

![enter image description here](https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSdwMGuXkHSsBY8YSohsoBdPvup0lSkjOK3kkBgCqZ8S3MLrIOR)

###### Использование джойстика

После успешного подключения джойстика к Arduino, вы можете считывать его оси и состояние кнопки для контроля движения объектов в вашем проекте.

1.  В функции  `setup()`, установите режим кнопки джойстика как входной с подтягивающим резистором:

```cpp
void setup() {
  pinMode(2, INPUT_PULLUP);
}

```

2.  В функции  `loop()`, считывайте значения осей X и Y джойстика с помощью функции  `analogRead(pin)`:

```cpp
void loop() {
  int xValue = analogRead(A0);
  int yValue = analogRead(A1);
  // ...
}

```

3.  Обработайте значения осей X и Y с вашей логикой. Например, вы можете использовать их для управления движением робота или перемещения объекта на экране.
    
4.  Считывайте состояние кнопки джойстика с помощью функции  `digitalRead(pin)`:
    

```cpp
void loop() {
  int xValue = analogRead(A0);
  int yValue = analogRead(A1);
  int buttonState = digitalRead(2);
  // ...
}

```

5.  Обработайте состояние кнопки с вашей логикой. Например, вы можете использовать ее для выполнения определенных действий при нажатии кнопки.

[Пример](https://wokwi.com/projects/376460792695326721)
```c++
#define VERT_PIN A0
#define HORZ_PIN A1
#define SEL_PIN 2
 

void  setup()  {
	pinMode(VERT_PIN,  INPUT);
	pinMode(HORZ_PIN,  INPUT);
	pinMode(SEL_PIN,  INPUT_PULLUP);
	Serial.begin(115200);
}

void  loop()  {
	int vert =  analogRead(VERT_PIN);
	int horz =  analogRead(HORZ_PIN);
	bool selPressed =  digitalRead(SEL_PIN)  ==  LOW;
	Serial.print("Vertical: ");
	Serial.print(vert);
	Serial.print(" Horizontal: ");
	Serial.print(horz);
	Serial.print(" Pressed: ");
	Serial.println(selPressed);
	delay(1000);
}
```
Код определяет максимальное количество светодиодных модулей (MAX_DEVICES) и на основе этого значения вычисляет максимальные координаты X и Y светодиодной матрицы. Он также назначает номера контактов для контактов часов, данных и выбора микросхемы.

В функции setup() код инициализирует матрицу светодиодов, устанавливает яркость светодиодов на половину максимальной интенсивности и очищает матрицу.

Функция цикла() непрерывно считывает аналоговые входы с потенциометров, подключенных к вертикальным и горизонтальным выводам (VERT_PIN и HORZ_PIN). На основе считанных значений он соответственно обновляет текущие координаты X и Y (x и y).

Если значение по вертикали меньше 300, координата Y увеличивается на 1, но ограничивается максимальной координатой Y. Если значение по вертикали превышает 700, координата Y уменьшается на 1, но ограничивается 0. Аналогично, если значение по горизонтали превышает 700, координата X увеличивается на 1, но ограничивается максимальной координатой X. Если горизонтальное значение ниже 300, координата X уменьшается на 1, но ограничивается 0.

Если кнопка, подключенная к контакту выбора (SEL_PIN), нажата (LOW), светодиодная матрица очищается.

Наконец, код устанавливает светодиод в текущих координатах X и Y для включения (истина), обновляет матрицу светодиодов и добавляет задержку в 100 миллисекунд перед повторением цикла.

##### [Ползунковый потенциометр](https://docs.wokwi.com/parts/wokwi-slide-potentiometer)
Потенциометр - это электронный компонент, который позволяет регулировать напряжение или сопротивление. Использование потенциометра с Arduino позволяет создавать проекты, в которых можно регулировать параметры, такие как яркость светодиодов, скорость двигателей, частота звуков и т.д.

###### Подключение потенциометра

Потенциометр имеет 3 вывода: верхний вывод (VCC), средний вывод (связанный с перемещением регулятора потенциометра) и нижний вывод (GND). Для подключения потенциометра к Arduino, выполните следующие шаги:

1.  Подключите верхний вывод потенциометра (VCC) к 5V на Arduino.
2.  Подключите средний вывод потенциометра к аналоговому пину на Arduino (например, A0).
3.  Подключите нижний вывод потенциометра (GND) к GND на Arduino.

##### Использование потенциометра

После успешного подключения потенциометра к Arduino, вы можете считывать значение его положения и использовать его для регулировки параметров в вашем проекте.

1.  В функции  `setup()`, установите режим среднего вывода потенциометра как входной:

```cpp
void setup() {
  pinMode(A0, INPUT);
}

```

2.  В функции  `loop()`, считывайте значение положения потенциометра с помощью функции  `analogRead(pin)`:

```cpp
void loop() {
  int potValue = analogRead(A0);
  // ...
}

```

3.  Используйте значение положения потенциометра с вашей логикой. Например, вы можете использовать его для регулировки яркости светодиода:

```cpp
void loop() {
  int potValue = analogRead(A0);
  int brightness = map(potValue, 0, 1023, 0, 255); // Преобразование значения положения в диапазон яркости (0-255)
  analogWrite(LED_PIN, brightness); // Установка яркости светодиода
}

```

4.  Загрузите код на Arduino и проверьте, что ваша логика регулирует параметры в соответствии с положением потенциометра.

Управление двигателем.
```c++
#include <Servo.h>

Servo myservo;  // create servo object to control a servo

int potpin = 0;  // analog pin used to connect the potentiometer
int val;    // variable to read the value from the analog pin

void setup() {
  myservo.attach(9);  // attaches the servo on pin 9 to the servo object
}

void loop() {
  val = analogRead(potpin);            // reads the value of the potentiometer (value between 0 and 1023)
  val = map(val, 0, 1023, 0, 180);     // scale it to use it with the servo (value between 0 and 180)
  myservo.write(val);                  // sets the servo position according to the scaled value
  delay(15);                           // waits for the servo to get there
}
```
Во-первых, мы включаем библиотеку `Servo`, которая предоставляет функции для управления серводвигателем. Мы создаем экземпляр класса `Servo` под названием `myservo` для управления сервоприводом.

Далее мы определяем переменную `potpin` для хранения номера аналогового контакта, к которому подключен потенциометр. Мы также объявляем переменную `val` для хранения значения, считываемого с потенциометра.

В функции `setup()` мы подключаем серводвигатель к контакту `9` с помощью функции `Attach()`.

В функции `loop()` мы считываем значение с потенциометра с помощью функции `AnalogRead()`. Эта функция возвращает значение `от 0 до 1023`, представляющее уровень напряжения на аналоговом выводе. Затем мы используем функцию `map()` для масштабирования этого значения в диапазоне `от 0 до 180`, который представляет собой диапазон положений, в которые может перемещаться серводвигатель. Наконец, мы используем функцию `write()`, чтобы установить положение сервопривода в соответствии с масштабированным значением.

Мы добавляем небольшую задержку в 15 миллисекунд, используя функцию `delay()`, чтобы позволить серводвигателю достичь желаемого положения перед считыванием следующего значения с потенциометра.

##### [Поворотный энкодер (KY-040)](https://docs.wokwi.com/parts/wokwi-ky-040)
Поворотный энкодер - это устройство, которое преобразует механическое вращение в электрический сигнал. Он обычно используется для измерения угла поворота или смещения. Поворотный энкодер состоит из двух основных компонентов: вала, который вращается с физическим объектом, и оборудования, которое генерирует электрический сигнал в зависимости от положения вала.

![enter image description here](https://encrypted-tbn1.gstatic.com/images?q=tbn:ANd9GcREfhRYbkR78FBw64YP_g0UfdW9IujmLW_SxRwLj5hOOaqL_sZC)

Arduino позволяет подключать и использовать поворотные энкодеры для измерения и управления угловым положением объектов. В этом конспекте мы рассмотрим базовые шаги по подключению и использованию поворотного энкодера с Arduino.

###### Подключение поворотного энкодера

Поворотные энкодеры имеют обычно три вывода: две линии энкодера (A и B) и общий вывод (GND). Для подключения поворотного энкодера к Arduino, выполните следующие шаги:

1.  Подключите линию энкодера A к цифровому пину Arduino.
2.  Подключите линию энкодера B к другому цифровому пину Arduino.
3.  Подключите общий вывод (GND) поворотного энкодера к GND на Arduino.

###### Использование поворотного энкодера

После подключения поворотного энкодера к Arduino, вы можете использовать библиотеку  `RotaryEncoder`  для работы с ним. Вот пример кода для получения угла поворота энкодера с помощью этой библиотеки:Copy

```c++
#include <RotaryEncoder.h>

// Подключение линии энкодера A к пину 2
// Подключение линии энкодера B к пину 3
RotaryEncoder encoder(2, 3);

void setup() {
  Serial.begin(9600);
}

void loop() {
  // Получение значения угла поворота энкодера
  int angle = encoder.read();
  
  // Вывод значения угла в монитор порта
  Serial.println(angle);
  
  delay(100);
}

```

В этом примере мы подключаем линию энкодера `A` к пину `2` и линию энкодера `B` к пину `3`. Затем мы создаем экземпляр класса  `RotaryEncoder`  и используем метод  `read()`  для получения значения угла поворота энкодера. Значение угла выводится в монитор порта каждые 100 миллисекунд.

```c++
#define ENCODER_CLK 2
#define ENCODER_DT  3

void setup() {
  Serial.begin(115200);
  pinMode(ENCODER_CLK, INPUT);
  pinMode(ENCODER_DT, INPUT);
}

int lastClk = HIGH;

void loop() {
  int newClk = digitalRead(ENCODER_CLK);
  if (newClk != lastClk) {
    // There was a change on the CLK pin
    lastClk = newClk;
    int dtValue = digitalRead(ENCODER_DT);
    if (newClk == LOW && dtValue == HIGH) {
      Serial.println("Rotated clockwise ⏩");
    }
    if (newClk == LOW && dtValue == LOW) {
      Serial.println("Rotated counterclockwise ⏪");
    }
  }
}
```

## Двигатели
Управление двигателями является важной частью многих проектов, которые используют `Arduino`. Возможность управлять двигателями позволяет создавать различные виды проектов, включая роботов, автоматические системы и другие устройства, требующие движения.

`Arduino` имеет несколько способов управления двигателями, включая использование цифровых и аналоговых пинов, а также использование специализированных модулей. Каждый из этих способов имеет свои преимущества и подходит для разных видов двигателей и требуемой функциональности.

В этом конспекте мы рассмотрим основные методы управления двигателями с использованием Arduino. Мы покажем, как подключить и настроить двигатели, а также приведем примеры кода для различных сценариев управления двигателями.

Управление двигателями с Arduino открывает широкие возможности для создания интересных и уникальных проектов. Если вы интересуетесь робототехникой, автоматизацией или просто хотите научиться управлять двигателями, этот конспект будет полезным введением в тему. Далее мы рассмотрим базовые шаги и код для старта вашего проекта управления двигателями с `Arduino`.
Arduino позволяет управлять двигателями различных типов, от простых DC-моторов до шаговых и сервоприводов. Управление двигателями с помощью Arduino открывает широкие возможности для создания различных проектов, включая роботику, автоматизацию и многое другое. В этом конспекте мы рассмотрим основные методы управления различными типами двигателей с помощью Arduino.

### Управление DC-моторами

DC-моторы - самые простые и распространенные типы двигателей. Они имеют два вывода: один для питания (обычно 5-12 В) и другой для управления направлением вращения. Для управления DC-моторами с помощью Arduino, вы можете использовать модуль моторного контроллера или создать свою собственную схему, используя транзисторы и резисторы. В любом случае, подключение и управление DC-моторами осуществляется с использованием цифровых пинов Arduino.

1.  Подключите DC-мотор к модулю моторного контроллера или к своей схеме управления.
2.  Подключите питание модуля моторного контроллера (обычно 5-12 В) к внешнему источнику питания.
3.  Подключите сигнальные пины модуля моторного контроллера к цифровым пинам Arduino.
4.  В программе Arduino, используйте функции  `pinMode()`  и  `digitalWrite()`  для управления пинами модуля моторного контроллера и контроля направления и скорости вращения DC-мотора.

### Управление шаговыми двигателями

Шаговые двигатели обладают отличными характеристиками, идеально подходящими для управления точными движениями. Они имеют несколько выводов, каждый из которых управляет определенным шагом двигателя. Для управления шаговыми двигателями с использованием Arduino, вы можете использовать специальные драйверы шаговых двигателей, такие как A4988 или DRV8825.

1.  Подключите шаговой двигатель к драйверу шагового двигателя.
2.  Подключите питание драйвера шагового двигателя (обычно 5-12 В) к внешнему источнику питания.
3.  Подключите сигнальные пины драйвера шагового двигателя к цифровым пинам Arduino.
4.  В программе Arduino, используйте библиотеку  `Stepper`  и создайте экземпляр класса  `Stepper`, указав количество шагов и пины управления.
5.  Используйте методы  `setSpeed()`  и  `step()`  для установки скорости двигателя и выполнения шагов.

### Управление сервоприводами

Сервоприводы - это компактные устройства, обеспечивающие точное позиционирование. Они имеют три вывода: питание (обычно 5 В), общий GND и пин управления. Для управления сервоприводами с использованием Arduino, вы можете использовать библиотеку  `Servo`, которая предоставляет простой интерфейс для работы с сервоприводами.

1.  Подключите сервопривод к Arduino, подключив питание к 5 В, GND к GND и пин управления к цифровому пину.
2.  В программе Arduino, подключите библиотеку  `Servo`  и создайте экземпляр класса  `Servo`.
3.  Используйте метод  `attach()`  для привязки сервопривода к цифровому пину.
4.  Используйте методы  `write()`  или  `writeMicroseconds()`  для установки угла поворота сервопривода.


### Моторы

|Название|Описание|
|-|-|
|[Микросервомотор](https://docs.wokwi.com/parts/wokwi-servo)|Стандартный микросервомотор|
|[Биполярный шаговый двигатель](https://docs.wokwi.com/parts/wokwi-stepper-motor)|Биполярный шаговый двигатель|
|[A4988](https://docs.wokwi.com/parts/wokwi-a4988)|Драйвер шагового двигателя A4988|
|[Двухосный шаговый двигатель](https://docs.wokwi.com/parts/wokwi-biaxial-stepper)|Концентрический двухосный шаговый двигатель, содержащий два шаговых двигателя, упакованных в один корпус|

#### Примеры
##### [Микросервомотор](https://docs.wokwi.com/parts/wokwi-servo)

![enter image description here](https://encrypted-tbn1.gstatic.com/images?q=tbn:ANd9GcRfVio-zyWbUxaPK3Un5wKqbV-_Dq1bAtQFjt_vdznrHd36l8f7)

```c++
#include <Servo.h>

Servo myservo;  // create servo object to control a servo
// twelve servo objects can be created on most boards

int pos = 0;    // variable to store the servo position

void setup() {
  myservo.attach(9);  // attaches the servo on pin 9 to the servo object
}

void loop() {
  sweepServo(0, 180, 1); // sweep from 0 to 180 degrees
  sweepServo(180, 0, -1); // sweep from 180 to 0 degrees
}

void sweepServo(int start, int end, int step) {
  for (pos = start; pos != end; pos += step) {
    myservo.write(pos); // tell servo to go to position in variable 'pos'
    delay(15); // waits 15ms for the servo to reach the position
  }
}
```

- Приведенный код является примером управления серводвигателем с помощью платы `Arduino`. Он использует библиотеку `Servo` для создания сервообъекта и управления его положением.

- В функции настройки сервообъект прикрепляется к контакту `9` платы `Arduino` с помощью метода `Attach`.

- В функции `loop` функция `SweepServo` вызывается дважды. Первый вызов меняет сервопривод от 0 до 180 градусов с шагом 1, а второй вызов меняет сервопривод от 180 до 0 градусов с шагом -1.

Функция `SweepServo` делает код более модульным и простым для понимания. Он выделяет логику развертки сервопривода в отдельную функцию, делая код более читабельным и удобным в сопровождении.

##### [Биполярный шаговый двигатель](https://docs.wokwi.com/parts/wokwi-stepper-motor)
Двухфазный шаговый двигатель (Bipolar Stepper Motor) - это тип двигателя, который может выполнять точные пошаговые движения. Он состоит из двух фаз, каждая из которых имеет свою намотку, что позволяет управлять точным положением и скоростью вращения. Arduino позволяет управлять двухфазным шаговым двигателем, подключая его к соответствующему драйверу и используя специальную библиотеку.

![enter image description here](https://encrypted-tbn3.gstatic.com/images?q=tbn:ANd9GcQiNBKF0m1Rb46Wb4m-q0_Z8nAMHU3itSPaGbLSdxyC6whDMwXs)

###### Подключение двухфазного шагового двигателя к Arduino

Для подключения двухфазного шагового двигателя к Arduino, выполните следующие шаги:

1.  Подключите драйвер шагового двигателя (например, A4988 или DRV8825) к Arduino, подключив питание (обычно 5-12 В) к внешнему источнику питания и GND к GND Arduino.
2.  Подключите пины направления (DIR) и шага (STEP) драйвера шагового двигателя к соответствующим пинам Arduino.
3.  Подключите выводы фаз двухфазного шагового двигателя (обычно помечены как A и B) к выходам драйвера шагового двигателя. Обратите внимание, что порядок подключения проводов фаз может влиять на направление вращения двигателя.

###### Управление двухфазным шаговым двигателем с помощью Arduino

С помощью Arduino и специальной библиотеки  `Stepper`  вы можете управлять двухфазным шаговым двигателем. Вот пример кода для поворота двигателя вперед и назад:

```c++
#include <Stepper.h>

// Определение количества шагов на один оборот двигателя
const int stepsPerRevolution = 200;

// Подключение пинов шага и направления к Arduino
const int stepPin = 2;
const int dirPin = 3;

// Создание экземпляра класса Stepper
Stepper myStepper(stepsPerRevolution, stepPin, dirPin);

void setup() {
  // Настройка скорости двигателя
  myStepper.setSpeed(60);
}

void loop() {
  // Вращение двигателя вперед на один оборот
  myStepper.step(stepsPerRevolution);
  delay(1000);

  // Вращение двигателя назад на половину оборота
  myStepper.step(-stepsPerRevolution / 2);
  delay(1000);
}
```

В этом примере мы подключаем пин шага (`STEP`) шагового двигателя к пину `2` `Arduino` и пин направления (`DIR`) к пину `3` `Arduino`. Затем мы создаем экземпляр класса  `Stepper`  с указанием количества шагов на один оборот и пинов управления. В методе  `setup()`  мы устанавливаем скорость двигателя, а в методе  `loop()`  мы выполняем повороты вперед и назад с помощью метода  `step()`.

##### [A4988](https://docs.wokwi.com/parts/wokwi-a4988)
A4988 - это популярный драйвер шагового двигателя, который позволяет управлять шаговыми двигателями с высокой точностью и контролируемостью. Он широко используется в различных промышленных и робототехнических приложениях. A4988 позволяет подключать и управлять двумя фазами шагового двигателя и контролировать его скорость, направление и шаговый режим.

![enter image description here](data:image/jpeg;base64,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)

###### Подключение драйвера A4988 к Arduino

Для подключения драйвера A4988 к Arduino, выполните следующие шаги:

1.  Питание: Подключите питание (обычно 5-12 В) к пинам VCC и GND на драйвере A4988. Обратите внимание, что напряжение питания должно быть совместимо с требованиями вашего шагового двигателя.
    
2.  Шаговые и направляющие пины: Подключите пины шага (STEP) и направления (DIR) на драйвере A4988 к соответствующим пинам Arduino. Эти пины позволяют управлять скоростью и направлением вращения шагового двигателя.
    
3.  Управление микрошагами: Драйвер A4988 также поддерживает функцию микрошага, которая позволяет улучшить контроль и плавность движения шагового двигателя. Для включения или отключения микрошага используйте пины MS1, MS2 и MS3 на драйвере A4988. Выбор определенного режима микрошага определяется сочетанием состояний этих пинов.
    

###### Использование драйвера A4988 с Arduino

Для управления шаговым двигателем с помощью драйвера A4988 и Arduino можно использовать специальную библиотеку  `AccelStepper`. Вот пример кода, демонстрирующий простейший способ управления двигателем с помощью A4988:

```c++
#include <AccelStepper.h>

// Определение пинов шага и направления
const int stepPin = 2;
const int dirPin = 3;

// Создание экземпляра класса AccelStepper
AccelStepper stepper(1, stepPin, dirPin);

void setup() {
  // Установка начальной скорости и длины шага
  stepper.setMaxSpeed(1000);
  stepper.setSpeed(500);
}

void loop() {
  // Вращение двигателя на один оборот вперед
  stepper.move(200);
  stepper.runToPosition();
  delay(1000);

  // Вращение двигателя на половину оборота назад
  stepper.move(-100);
  stepper.runToPosition();
  delay(1000);
}

```

В этом примере мы создаем экземпляр класса  `AccelStepper`  и указываем пины шага и направления. Затем мы устанавливаем максимальную скорость и длину шага с помощью методов  `setMaxSpeed()`  и  `setSpeed()`.

В методе  `loop()`  мы используем методы  `move()`  и  `runToPosition()`  для выполнения движения шагового двигателя. Метод  `move()`  указывает на количество шагов, на которое нужно повернуть двигатель, а метод  `runToPosition()`  запускает двигатель и ожидает, пока он не достигнет целевой позиции. Между поворотами двигателя мы добавляем задержку с помощью функции  `delay()`.
##### [Двухосный шаговый двигатель](https://docs.wokwi.com/parts/wokwi-biaxial-stepper)
Двухосный шаговый двигатель (Two-Axis Stepper Motor) - это тип двигателя, который может выполнять точные пошаговые движения вдоль двух осей одновременно. Он состоит из двух независимых шаговых двигателей, каждый из которых контролирует движение по одной из осей. Arduino позволяет управлять двухосным шаговым двигателем, подключая его к соответствующим драйверам и используя специальные библиотеки.

###### Подключение двухосного шагового двигателя к Arduino

Для подключения двухосного шагового двигателя к Arduino, выполните следующие шаги:

1.  Подключите драйверы шагового двигателя (например, A4988 или DRV8825) к Arduino, подключив питание (обычно 5-12 В) к внешнему источнику питания и GND к GND Arduino.
2.  Подключите пины направления (DIR) и шага (STEP) каждого драйвера шагового двигателя к соответствующим пинам Arduino.
3.  Подключите выводы фаз двухосного шагового двигателя (обычно помечены как A и B для первой оси и C и D для второй оси) к выходам соответствующих драйверов шагового двигателя. Обратите внимание, что порядок подключения проводов фаз может влиять на направление движения каждой из осей.

![enter image description here](data:image/jpeg;base64,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)

###### Управление двухосным шаговым двигателем с помощью Arduino

С помощью Arduino и специальных библиотек, таких как  `AccelStepper`, вы можете управлять двухосным шаговым двигателем. Вот пример кода для управления движением каждой оси независимо:Copy

```c++
#include  <Stepper.h>
const  int stepsPerRevolution =  200;

Stepper stepper1(stepsPerRevolution,  2,  3,  4,  5);
Stepper stepper2(stepsPerRevolution,  8,  9,  10,  11);

void  setup()  {
	// set the speed at 20 rpm for one stepper, 90 rpm for another:
	stepper1.setSpeed(20);
	stepper2.setSpeed(90);
	// initialize the serial port:
	Serial.begin(9600);
}

  

void  loop()  {
	// step one revolution in one direction:
	Serial.println("clockwise");
	stepper1.step(stepsPerRevolution);
	stepper2.step(stepsPerRevolution);
	delay(500);

	// step one revolution in the other direction:

	Serial.println("counterclockwise");
	stepper1.step(-stepsPerRevolution);
	stepper2.step(-stepsPerRevolution);
	delay(500);
}
```

В этом примере мы создаем экземпляры класса  `Stepper`  для каждой оси и указываем пины шага и направления. Затем мы устанавливаем максимальную скорость и длину шага для каждой оси с помощью методов  `setMaxSpeed()`  и  `setSpeed()`.

В методе  `loop()`  мы используем методы  `move()`  и  `runToPosition()`  для выполнения движения каждой оси независимо. Метод  `move()`  указывает на количество шагов, на которое нужно переместить ось, а метод  `runToPosition()`  запускает двигатель и ожидает, пока он не достигнет целевой позиции. Между перемещениями каждой оси мы добавляем задержку с помощью функции  `delay()`.

## Дополнительные материалы

[Подробнее про функции библиотеки TFT](https://wikihandbk.com/wiki/Arduino:%D0%91%D0%B8%D0%B1%D0%BB%D0%B8%D0%BE%D1%82%D0%B5%D0%BA%D0%B8/TFT)
[Большая статья на Амперке, посвященная библиотеке UTFT](http://wiki.amperka.ru/%D0%BF%D1%80%D0%BE%D0%B4%D1%83%D0%BA%D1%82%D1%8B:tft-lcd-240x320) 
[LCDWIKI3](http://www.lcdwiki.com/1.44inch_SPI_Module_ST7735S_SKU:MSP1443) 
[Документация](https://docs.wokwi.com/parts/wokwi-ili9341)
[Пример](https://wokwi.com/projects/377635992487870465)