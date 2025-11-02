# leek3 protocol
## Header
- signature: 4 bytes = 'y3ip';
- version: 1 byte uint; версия leek3 по модулю 256
- header_ln: 2 bytes; длина заголовка
- hop_param: 1 byte
    - min_delay: 1 bit; запросить путь с минимальной задержеой
    - max_bandwidth: 1 bit; запросить путь с максимальной шириной полосы пропускания
    - max_safety: 1 bit; запросить самый надежный путь
    - proirity: 3 bit; приоритет пакета, выше важнее
    - dont_fragment: 1 bit - запрет на фрагментацию
    - more_fragment: 1 bit - (0 - пакет либо единственный, либо последний, 1 - за пакетом есть еще пакеты, но нет запрета)
- fragment_off: 2 byte uint; если фрагментация, то смещение фрагмента
- ttl: 1 byte uint; сколько хопов живет пакет
- nt: 1 byte uint; сколько посетил сетей (отбрасывается если число сетей больше, чем разрешенная длина в сети)
- src_addr_ln: 1 byte uint
- src_addr: array[src_addr_ln] of 2 byte uint
- dst_addr_ln: 1 byte uint
- dst_addr: array[dst_addr_ln] of 2 byte uint
- inner_package: 1 byte uint; какой внутри протокол
- data_ln: 2 bytes
- header_crc: 4 byte uint
- data: data_ln bytes
- package_crc: 4 byte uint

# leek3cmd protocol
## Header
- signature: 4 bytes = 'y3cd'
- 

# leek4sm (simple) protocol
## Header
- signature: 4 bytes = 'l4sm'
- src_port: 2 byte uint
- dst_port: 2 byte uint
- data_ln: 2 byte uint
- data: data_ln bytes
- package_crc: 4 byte uint
