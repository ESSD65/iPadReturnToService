# iPadReturnToService
 <hr>
Installation:

Requires Python 3.9+<br>
Open a command prompt in the project folder and enter the command: <br>```pip install -r requirements.txt``` <br>or<br>```python3 -m pip install -r requirements.txt```<br>if python is not on your PATH.
<hr>
Configure LaunchAgent:

Open the return to service .plist file and configure it accordingly.  There are comments in the plist for fields that require configuring, and a description of them below.<br>

Fields to configure:
<ol>
<li>LaunchAgent name (default d65.langec.return_to_service)</li>
<li>Path to Python3</li>
<li>Path to project main.py file</li>
<li>Schedule to run the launchagent on</li>
</ol>
<hr>
Helpful gist for launch agents: https://gist.github.com/masklinn/a532dfe55bdeab3d60ab8e46ccc38a68
<br>Check the comments for help too.<br><br>
You'll need to "bootstrap" the launchagent to add it as a recurring task:<br>

```launchctl bootstrap gui/503 /PATH/TO/PLIST```

You can launch it at any point by doing the "kickstart" command, where "LaunchAgentName" is the name you configured on the plist:<br>
```launchctl kickstart gui/503/LaunchAgentName```

To terminate the recurring task, you'll use the "bootout" parameter:<br>
```launchctl bootout gui/503 /PATH/TO/PLIST```
