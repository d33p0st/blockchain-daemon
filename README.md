[![Build](https://github.com/d33p0st/blockchain-daemon/actions/workflows/Build.yml/badge.svg)](https://github.com/d33p0st/blockchain-daemon/actions/workflows/Build.yml)

# Overview

Countering Ransomwares is a challenge. That brings me to this. A preventive measure against Ransomwares.

## Idea

The basic idea behind this project is to merge `Immutable Shadow Copies` and `BlockChain`. Enter `"BlockChain Daemon"`, the idea is to store immutable copies of specific sensitive files on a `BlockChain`.

## Working

```console
   ,----------------,     Launches    ,-------------------,
   | Driver Program |-----------------| BlockChain Daemon |
   ',----------,---'    and exits     '---------,---------'
    |          |                                |
    |          |                                | Maintains a
    | gives    |                                | Blockchain
    | instru-  |                                | and listens
    | ctions   |   Sends User instructions      | for user
    |          '--------------------------,     | instruction
 ,__|___,                                 |     |
 | User |   ,__________,              ,---'-----'----------,
 '------'   | updates/ |______________| User Instruction   |
            | retieves |              | resolver           |
            | from     |              '--------------------'
            | blockch- |
            | ain      |------------,
            '----------'            | During Ransomware attack
                                    | Files can be easily saved on the
                                    | Blockchain and retrieved.
                            ,_______|______,
                            |  FTP Server  |
                            '--------------'
```

> Note: There wont be any physical presence of `Blockchain Daemon` (no program file, that can be corrupted to stop it's working). The `Blockchain Daemon` can maintain presence in either volatile memory or private server as decided by the user.

> Note: Fetching from the blockchain is easy to do and user can choose either to fetch and store it in the infected machine (not recommended) or upload it to a FTP server directly from the blockchain.

> Note: During a `Ransomware` attack [Crypto Ransomwares], The OS remains functional and the blockchain maintained in the RAM would also be intact. Therefore, giving a preventive type advantage, and easy retrieval.

> Note: In case of a shutdown, The `Blockchain` daemon will create a backup, either in local machine or a FTP Server as chosen by the user. The backup will be completely unreadable and encrypted. In this scenario, choosing a FTP server is far secure than having a backup on the local machine.

> Note: Free or temporary FTP servers can be easily created through a lot of websites online. One such is [SFTPCloud](https://sftpcloud.io/tools/free-ftp-server), which even allows to create a free temporary server which self destructs in one hour.