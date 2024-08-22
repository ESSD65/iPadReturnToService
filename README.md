# iPadReturnToService
 <hr>
Installation:

Requires Python 3.9+<br>
Open a command prompt in the project folder and enter the command: ```pip install -r requirements.txt``` or ```python3 -m pip install -r requirements.txt``` if python is not on your PATH.
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
