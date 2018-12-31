# Just a big information about me telling you on how to selfhost

gonna let you know when you selfhost

- I am not going to support you in anything
- If you are going make it public, you are violating the [Legal Terms of Use](https://enternewname.me/pewdiepie/tos)
- You have a big risk of breaking something

i will never give you support in anything relating to this file

# Mininium Requirements

1.3 GBs for RAM
1GB disk

VPS Specs that pewds runs off of:
- 20GBs HDD
- 2GBS RAM

Prefered Enviroment:

- 20GBS SSD
- 5GBS RAM

# Dependencies

- asyncpg
- postgresql
- discord.py@rewrite ~ latest
- jishaku is optional, but i prefer it
- asyncio
- psutil

# To setup database

```sql

CREATE ROLE "my_role" WITH LOGIN PASSWORD "my_password";
CREATE DATABASE "my_db" OWNER "my_role";
-- Then when that is setted up the schema handles whatever other shit i add

```

# Setting up the config.json

just configure this
make a file named `db/config.json`

```json

{
    "db-creds": {
        "user": "user",
        "password": "password",
        "database": "database",
        "host": "host"
    },
    "tokens": {
        "bottoken" : "bot token",
        "dbltoken": "discord bot list token",
        "dbgtoken": "discord bots group token"
    },
    "server": "https://discord.gg/vtJJmWQ",
    "debug": true,
    "cogs": [
        "modules.main",
        "modules.owner",
        "modules.fun",
        "modules.handler",
        "modules.economy"
    ],
    "yt": " api key ",
    "tickno": "<:tickNo:490607198443929620>",
    "tickyes": "<:tickYes:490607182010777620>",
    "ticknoreact": ":tickYes:490607182010777620",
    "tickyesreact": ":tickYes:490607182010777620",
    "ver": "version",
    "8ball": [
        "It is certain",
        "It is decidedly so",
        "Without a doubt",
        "Yes - definitely.",
        "You may rely on it.",
        "As I see it",
        "yes.",
        "Most likely.",
        "Outlook good.",
        "yes",
        "signs point to yes",
        "reply hazy, try again",
        "ask again later",
        "better not tell you now",
        "cannot predict now",
        "Concentrate and ask again",
        "Don't count on it",
        "My reply is no",
        "My sources say no.",
        "outlook not so good",
        "very doubtful",
        "Not at all lolol"
    ]
}

```

and there its done

# Running

just do `run` + `.sh (if linux)` in the cmd prompt and it will run it regardless of what platform your on

> note linux you might have to do 
> chmod +x ./run.sh to make it executable

# Folders and files you should have after running the bot

<pre>

\db -- 
    - config.json
\docs --
    - HOSTING.md

\modules --
    - economy.py
    - fun.py
    - handler.py
    - main.py
    - owner.py
  
\Scripts --
    - run.sh
    - run.bat
    - requirements.txt
.gitignore
build.py
README.md
schema.sql


</pre>