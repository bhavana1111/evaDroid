import sys

cmd, txt = sys.argv

interval = 10

f = open(txt,encoding='utf-8')
seen = set()
clicked = set()
steps = 0
for line in f.readlines():
    if line.startswith('clickables:'):
        clickables = line[len('clickables:') + 1:-1].split(',')
        for clickable in clickables:
            seen.add(clickable.strip())
    if line.startswith('next_button:'):
        button = line[len('next_button:'):]
        clicked.add(button)
        steps = steps + 1
        if steps%interval == 1:
            print(str(steps) + '\t' + str(len(seen)) + '\t' + str(len(clicked)))
#        print(button)
#        print('seen:' + str(len(seen)))
#        print('clicked:' + str(len(clicked)))


'''import sys

cmd, txt = sys.argv

interval = 10

f = open(txt)
seen = set()
clicked = set()
steps = 0
for line in f.readlines():
    if line.startswith('clicked buttons history:'):
        clickables = line[len('clicked buttons history:') + 1:-1].split(',')
        for clickable in clickables:
            seen.add(clickable.strip())
    if line.startswith('Selected random value:'):
        button = line[len('Selected random value:'):]
        clicked.add(button)
        steps = steps + 1
        if steps%interval == 1:
            print(str(steps) + '\t' + str(len(seen)) + '\t' + str(len(clicked)))
#        print(button)
#        print('seen:' + str(len(seen)))
#        print('clicked:' + str(len(clicked)))




'''