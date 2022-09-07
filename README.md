# :honey_pot: SSH honeypot :honey_pot:
This tool creates an **honeypot server** running an **ssh service**, which detects a brute force attack, communicates with the attacker’s ssh client and provides it with a shell access
to a file system with the ability to execute a few basic commands.

## Run :bee:

	python3 honeypot.py -p [port]
 - **-p**: The port to which the ssh server will be binded to.

## Functionalities :mouse_trap:

- **Detect a brute force attack**: The honeypot detects brute force attacks against a specific user. After the fifth attempt, the honeypot grants access to a shell.
- **SSH functionality**: Once the attacker has been granted access and a connection has been established, the honeypot communicates to the client like a normal ssh server. <br>For instance, on a successful attempt by an attacker for the username john, should be able to see a shell prompt on the client side which resembles the following:

		john@server:/$
	Just like within a normal shell, the client has the ability to type in commands which are sent over to your honeypot server when they hit carriage return. In addition, the server is also be able to keep track of time of an open connection. If the client remains idle for 60 seconds, it should terminate the connection.
- **Basic file system**: A fake file system is created along with the emulation of a few basic commands. The following commands are available:
	- **ls** : lists all files in the current directory.
	- **echo "XXXX" > destionation.txt** : creates a simple text file with the user-supplied name and content. 
	- **cat text.txt** : prints the content of a file.
	- **cp source.txt destination.txt** : creates destination.txt and copies the content of source.txt

## Developer :busts_in_silhouette:
 #### Riccardo Nannini :it:
- [Linkedin](https://www.linkedin.com/in/riccardo-nannini/), [Twitter](https://twitter.com/NanniniRiccardo)
