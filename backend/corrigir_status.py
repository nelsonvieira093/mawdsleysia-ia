with open('api/routes/chat.py', 'r') as f:
    lines = f.readlines()

# Corrige linha 473-475
lines[472] = '                        or_(\n'
lines[473] = '                            FollowUp.status == "ABERTO",\n'
lines[474] = '                            FollowUp.status == "EM_ANDAMENTO"\n'
lines[475] = '                        )\n'

# Corrige linha 631-633
lines[630] = '                    or_(\n'
lines[631] = '                        FollowUp.status == "ABERTO",\n'
lines[632] = '                        FollowUp.status == "EM_ANDAMENTO",\n'
lines[633] = '                        FollowUp.status == "ABERTO"\n'
lines[634] = '                    )\n'

with open('api/routes/chat.py', 'w') as f:
    f.writelines(lines)

print("Status corrigidos: ABERTO e EM_ANDAMENTO")
