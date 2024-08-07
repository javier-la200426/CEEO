<!-- 
Project Name: SerialTrigger
Author: Ethan Danahy
Last update: October 24th, 2022
Requires: SPIKE 3 Firmware
Description: Use a Chrome Browser and SPIKE Prime to
			 monitor serial stream and trigger response.
(C) Tufts Center for Engineering Education and Outreach (CEEO)
-->
<html>
<head>
  <title>SPIKE Prime Serial Trigger</title>
  <meta charset="UTF-8">
  <!-- Gabriel Sessions' PyREPL Connection -->
  <script defer="defer" src="https://cdn.jsdelivr.net/gh/gabrielsessions/pyrepl-js/build/main.js"></script>
  <!--IDE API-->
  <script src="https://cdnjs.cloudflare.com/ajax/libs/ace/1.4.12/ace.min.js"></script>
  <style>
	.bottom_text {
		color: black;
    }
	.topToolbar {
	    background-color: rgb(243, 250, 254);
	    color: rgb(7, 23, 44);
	    position: relative;
	    width: 500px;
	    height: 70px;
	    border: solid;
	    border-width: 1px;
	    margin: auto;
	    display: inline-block;
	}
	.console {
		border: 1px black solid;
		height: 400px;
		overflow: scroll;
		/* following from: https://stackoverflow.com/questions/4000792/how-can-i-style-code-listings-using-css */
	    background: #f4f4f4;
	    border-left: 3px solid #f36d33;
	    color: #666;
	    page-break-inside: avoid;
		font-family: "Lucida Console", Courier, monospace;
	    font-size: 15px;
	    line-height: 1.6;
	    margin-bottom: 1.6em;
	    max-width: 100%;
	    padding: 1em 1.5em;
	    display: block;
	    word-wrap: break-word;
	}
	.console_input {
		width: 300px;
		border: 1px black solid;
		background: #f4f4f4;
		border-left: 3px solid #f36d33;
		color: #666;
		font-family: "Lucida Console", Courier, monospace;
		font-size: 15px;
	    line-height: 1.6;
	    padding: 1em 1.5em;
	}
	.keyword_line {
		color: red;
		background-color: black;
	}
	.main_table {
		border: 1px gray solid;
	}
	td {
		padding: 10px;
	}
    #editor {
        border: 1px black solid;
        position: relative;
        left: 10px;
        height: 200px;
        width: 500px;
    }
  </style>
</head>
<body onload="setup();">

	<!-- SPIKE PRIME (SPIKE 3) PyREPL Connection -->
	<div class="topToolbar">
        <div style="position: relative; float:left; margin: 20px; text-align: center; top: 20%;">
            Connect SPIKE&trade; 3:
        </div>
        <div id="root"></div>
    </div>
    
    <br /><br />

	<table width='100%'><tr>

		<!-- LEFT SIDE: Serial Feed -->
		<td valign="top" class='main_table' width='50%'>

			<h1>Serial Feed</h1>
			<p>
				<button onclick='return window.pyrepl.stop;'>Emergency Stop</button>
				<button onclick='return window.pyrepl.reboot;'>Reboot (into Slot Mode)</button>
			</p>

			<p>Number of lines in serial feed: <span id='num_lines'></span></p>
			
			<p align=center>
				<pre width='90%' class='console' id='console'></pre>
			</p>
			
			<p>
				<input type=text class='console_input'>
				<button onclick='window.pyrepl.write = this.parentElement.getElementsByTagName("input")[0].value;'>Submit to Serial</button>
			</p>
			
		</td>

		<!-- RIGHT SIDE: trigger info -->
		<td valign="top" class='main_table' width='50%'>

			<h1>Trigger Info</h1>
			<p>Trigger keyword: <input type=text id='keyword' value='SCREAM' class='console_input'></p>
			<p><b>Trigger action:</b> Play Audio</p>
			
			<!-- SOUND -->
			<div align=center>
				<audio controls id='sound'
				    src="./scream.mp3">Your browser does not support the <code>audio</code> element.
				</audio>
			</div>

			<br /><br />
			<p><button onclick='document.getElementById("demobox").style.display="block";'>Show Python IDE</button></p>
			
		    <!--GUI-->
		    <div id = "demobox" style="display: none;">
			    <input type="button" id="execute" value="Execute">
		        <input type="button" id="stop" value="Stop">
		        <br><br>
		        <!-- ####         ***         Code editor          ***        #### -->
		        <!-- #### CHANGE THIS CODE TO CHANGE DEFAULT SPIKE PRIME CODE #### -->
		        <div id="editor">
import time, display
keyword = 'S' + 'C' + 'R' + 'E' + 'A' + 'M'
for i in range(4):
	display.display_text_for_time("3..2..1..", 3000, 100)
	time.sleep(3)
	print(keyword)
	time.sleep(1)</div>
	        </div>
			
		</td>
	</tr></table>

	<br /><br />

	<hr />

	<p class="bottom_text"><b>Disclaimer</b></p>

	<p class="bottom_text">LEGO®, the LEGO® logo, the Brick, MINDSTORMS®, SPIKE™, and the Minifigure are trademarks of ©The LEGO® Group. All other trademarks and copyrights are the property of their respective owners. All rights reserved.</p>

	<p class="bottom_text">This page isn’t affiliated, authorized, or endorsed by The LEGO Group.</p>

	
<script>

	////////////////////////
	// PYTHON EDITOR CODE //
	////////////////////////
    var editor = ace.edit("editor");
    // execute program sequence
    var buttonExecute = document.getElementById("execute");
    buttonExecute.addEventListener("click", function () {
	    if (window.pyrepl && window.pyrepl.isActive) {
			// get text content with Ace.js API
	        var editSession = editor.getSession();
	        var codeSession = editSession.getValue();
			// write out command to SPIKE Prime
			window.pyrepl.write = codeSession;
		}
    });
    var buttonStop = document.getElementById("stop");
    buttonStop.addEventListener("click", function () {
	    if (window.pyrepl && window.pyrepl.isActive) {
	        // issue a Control-C to exit code
	        window.pyrepl.stop;
	        // issues a motor stop in case motors are still running
	        window.pyrepl.write = "import motor\nmotor.motor_stop()";
	    }
    });
    
    /////////////////
    // PYREPL CODE //
    /////////////////

//JAVIEr INTERESTED//
	var timeout_delay = 750;
	var repl_timout_delay = 50;
	var num_lines_in_repl = 0;
	
	function setup() {
		if (window.pyrepl && window.pyrepl.isActive) {
			console.log('SPIKE Connected: SETUP SPIKE 3');
			setTimeout(monitor_serial, timeout_delay);
		} else {
			// PYREPL not ready
			// check back to do setup
			setTimeout(setup, timeout_delay);
		}
	}
	
	function monitor_serial() {
		// make sure they have loaded SPIKE Prime
		if (window.pyrepl.isActive) {
			// parse string
			let consoleOut = window.pyrepl.read;
			// update number of lines:
			var num_lines = consoleOut.length;
			document.getElementById('num_lines').innerHTML = num_lines;
			var found_keyword = false;
			if (num_lines > num_lines_in_repl) {
				var console_text = "";
				for (i=num_lines_in_repl; i<consoleOut.length; i++) {
					if (consoleOut[i].indexOf(document.getElementById('keyword').value) >= 0) {
						console_text += "<span class='keyword_line'>" + consoleOut[i] + "</span>";
						found_keyword = true;
					} else {
						console_text += consoleOut[i];
					}
				}
				document.getElementById('console').innerHTML += console_text;
				document.getElementById('console').scrollTop = document.getElementById('console').scrollHeight;

				document.getElementById('num_lines').innerHTML += " <span style='color: red;'>(number of new lines: <b>" + (num_lines - num_lines_in_repl) + "</b>)</span>";
				num_lines_in_repl = num_lines;
			}
			if (found_keyword) { play_audio(); }
		}
		// keep checking
		setTimeout(monitor_serial, timeout_delay);	
	}
//JAVIEr INTERESTED//

	function play_audio() {
		var audio = document.getElementById("sound");
		audio.play();
	}

</script>
</body>
</html>
