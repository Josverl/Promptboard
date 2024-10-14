from machine import Pin
import utime

keyMatrix = [
    [ "F1",  "F2",   "#",    "*"  ],
    [ "1",    "2",   "3",    "Up" ],
    [ "4",    "5",   "6",   "Down"],
    [ "7",    "8",   "9",   "Esc" ],
    ["Left",  "0", "Right", "Ent" ]
]
colPins = [0,1,2,3]
rowPins = [8,7,6,5,4]

row = []
column = []

for item in rowPins:
    row.append(Pin(item,Pin.OUT))
for item in colPins:
    column.append(Pin(item,Pin.IN,Pin.PULL_DOWN))
key = '0'
def scanKeypad():
    global key
    for rowKey in range(5):
        row[rowKey].value(1)
        for colKey in range(4):
            if column[colKey].value() == 1:
                key = keyMatrix[rowKey][colKey]
                row[rowKey].value(0)
                return(key)
        row[rowKey].value(0)
def printKey():
    key=scanKeypad()
    if key is not None:
        print("Key pressed is:{}".format(key))
    utime.sleep(0.2)
    
while True:
    printKey()