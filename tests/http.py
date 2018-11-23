import requests
import json
b = requests.get("https://api.github.com/repos/EnterNewName/PewDiePie/commits/master").json()
id = b['sha']
a = f"{id[0:6]} | {b['commit']['message']}"
print(a)