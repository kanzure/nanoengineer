<?php

function page_head($title) {
	echo "<?xml version=\"1.0\" encoding=\"ascii\"?>\n";
	echo "<!DOCTYPE html PUBLIC \"-//W3C//DTD XHTML 1.0 Transitional//EN\" \"DTD/xhtml1-transitional.dtd\">\n";
	echo "<html xmlns=\"http://www.w3.org/1999/xhtml\" xml:lang=\"en\" lang=\"en\">\n";
	echo "<head>\n<title>Nanorex SEMBot";
	if ($title) {
		echo " - $title";
	}
	echo "</title>\n";
	echo "<link rel=\"stylesheet\" href=\"/Engineering/styles.css\" type=\"text/css\"/>\n";
	echo "<link rel=\"shortcut icon\" href=\"/Engineering/favicon.ico\" />";
	echo "</head>\n";
}

