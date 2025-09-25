# "Low-Level"

В ходе нашего занятия мы исследовали возможности онлайн-эмуляторов, таких как Wokwi и Tinkercad. Эти платформы позволяют визуализировать и тестировать проекты на микроконтроллерах в реальном времени. Однако большинство разработок программ для микроконтроллеров осуществляется либо в интегрированных средах разработки (IDE), либо с использованием систем сборки, что мы и рассмотрим в этом занятии.

> [Репозиторий](https://github.com/savaleriy/arduino-wokwi-vscode)

#### Основные темы занятия:

1. **Разработка в IDE и системах сборки**:
    
    - Мы обсудим, какие IDE (например, Arduino IDE, PlatformIO) и системы сборки существуют, и как они упрощают процесс разработки.
    - Ознакомимся с основными инструментами и настройками, необходимыми для работы.
2. **Программирование на чистом C**:
    
    - Рассмотрим, как писать программы для микроконтроллеров на чистом языке C без использования фреймворка Arduino.
    - Обсудим основные особенности работы с аппаратными регистрами и манипуляции с портами.
3. **Программирование на Ассемблере**:
    
    - Погрузимся в низкоуровневое программирование, используя Ассемблер.
    - Изучим синтаксис Ассемблера и основные команды, которые позволяют контролировать микроконтроллер на более глубоком уровне.
## Toolchain
Необходимо установить цепочку инструментов *avr-gcc*, соответствующую своей платформе (Linux, macOS или Windows). Инструкции для этого приведены [здесь](https://wellys.com/posts/avr_c_setup/).
Для надежного подхода к отладке в Linux (Linux или WSL) вы можете добавить [Bloom](https://bloom.oscillate.io/) и *avr-gdb*. Bloom обеспечивает графическое отображение регистров и памяти микроконтроллера, а также необходимое соединение чипа с avr-gdb. [gdb](https://www.sourceware.org/gdb/) — простой, но чрезвычайно мощный инструмент отладки. Я считаю, что его проще использовать, чем большинство IDE, таких как Visual Studio, MPLAB IDE и т. д. Дополнительные рекомендации можно найти в [Разработка на C для ATmega328: Настройка Bloom и gdb для аппаратной отладки](https://wellys.com/posts/avr_c_gdb_bloomsetup/ ).

1. Установите набор инструментов. [Подробности здесь](https://www.wellys.com/posts/avr_c_setup/)
2. Если вы используете Linux и хотите попробовать аппаратную отладку, рассмотрите возможность [использования Bloom, avr-gdb и отладчика](https://www.wellys.com/posts/avr_c_gdb_bloomsetup/).

## Источники
- [Datasheet](https://docs.arduino.cc/resources/datasheets/ATmega328P-datasheet.pdf) 
- [Standard AVR C](http://avr-libc.nongnu.org)
- [Заметка по ASM для AVR](https://github.com/TomasGlgg/AVR-ASM) и [еще](https://dims.petrsu.ru/posob/avrlab/avrasm-rus.htm)
- [AVR-libc User Manual](https://avr-libc.nongnu.org/user-manual/pages.html): Руководство по библиотеке AVR для разработки на C.
- [Habr: Программирование Arduino без Arduino IDE](https://habr.com/ru/articles/392639/): Статья о том, как использовать альтернативные инструменты для программирования Arduino.
- [PlatformIO](https://platformio.org/): Замена Arduino IDE: Обзор возможностей PlatformIO как более мощного инструмента для разработки.
- [Программирование Arduino и AVR на Ассемблере](https://dumblebots.com/2022/07/31/programming-arduino-and-avr-microcontrollers-using-the-assembly-language/): Статья о программировании микроконтроллеров на Ассемблере.
- [AVR Libc](https://www.nongnu.org/avr-libc/)
- [Сообщество AVR Freaks](https://www.avrfreaks.net/)
- [Ардуино в C | Встроенная свобода](https://balau82.wordpress.com/arduino-in-c/)
- [Программирование Arduino на «чистом C»](http://audiodiwhy.blogspot.com/2019/01/programming-arduino-in-pure-c-now-were.html)
- [EMBEDDS: Учебные пособия по AVR](https://embedds.com/avr-tutorials/)
- [CCRMA: AVR](https://ccrma.stanford.edu/wiki/AVR#AVR_Microcontrollers)
- [Руководства по электронике и программированию Efundies: AVR](https://efundies.com/avr/)
- [Platformio-docs-flags](https://github.com/platformio/platformio-docs/blob/develop/projectconf/sections/env/options/build/build_flags.rst)
