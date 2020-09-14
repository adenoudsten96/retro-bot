import re



retro = "<@!85098921382125568>"
test = "<@&746774240820199465>"
mobile = "<@745978012692119642>"


print(mobile)
mobile = re.sub("\ |\@|\&|\!|\<|\>", '', mobile)
print(mobile)