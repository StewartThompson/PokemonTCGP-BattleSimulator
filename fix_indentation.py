with open('moteur/core/match.py', 'r') as f:
    lines = f.readlines()

with open('moteur/core/match.py', 'w') as f:
    for i, line in enumerate(lines):
        if 'def handle_knockout' in line and i > 450 and i < 460:
            print(f'Found at line {i+1}')
            f.write('    ' + line.lstrip())
        else:
            f.write(line)

print("Fixed indentation in moteur/core/match.py") 