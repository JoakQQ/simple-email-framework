# simple-email-framework
*Leung Chun Fai*

It is a simple email framework protocol implemented using TCP connection between server and clients. (for learning propose)

## Commands
0. "#USERNAME" *username*
1. "#PASSWORD" *password*
2. "#SENDTO" *username*
3. "#TITLE" *str*
4. "#CONTENT"
5. "#LIST"
6. "#RETRIEVE" *n*
7. "#DELETE" *n*
8. "#EXIT"

## Compilation and Execution
1. Open a terminal for the server program by ```python3 MailServer.py```, the server program should be ready for clients.
2. Open addition terminal(s) for the client program(s) by ```python3 MailClient.py```, maximum number of clients the server able to response to concurrently = `MAX_USERS` in `MailServer.py` file.
