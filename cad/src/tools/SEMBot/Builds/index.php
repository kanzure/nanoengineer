<?php

require_once("../util.inc");

page_head("Snapshot Builds");

?>
<body>
<table class="navbar" border="0" width="100%" cellpadding="0"
       bgcolor="#a0c0ff" cellspacing="0">

  <tr valign="middle">
      <th bgcolor="#70b0f0" class="navbar-select"
          >&nbsp;&nbsp;&nbsp;<a href="../index.php">Home</a>&nbsp;&nbsp;&nbsp;</th>

      <th>&nbsp;&nbsp;&nbsp;<a
        href="../index.php#qa">QA</a>&nbsp;&nbsp;&nbsp;</th>

      <th nowrap>&nbsp;&nbsp;&nbsp;<a
        href="../NE1_Documentation/">API Docs</a>&nbsp;&nbsp;&nbsp;</th>

      <th nowrap>&nbsp;&nbsp;&nbsp;<a
        href="../index.php#builds">Nightly Builds</a>&nbsp;&nbsp;&nbsp;</th>

      <th class="navbar" align="right" width="100%">
        <table border="0" cellpadding="0" cellspacing="0">
          <tr><th class="navbar" align="center">Nanorex Software-Engineering Mechanisms Robot (SEMBot)&nbsp;&nbsp;&nbsp;<a href="http://www.nanoengineer-1.net/" target="_top">NE1 Wiki</a>&nbsp;&nbsp;&nbsp;</th>
          </tr></table></th>
  </tr>
</table>

<p>
<img align="right" src="../Engineer-X-Man-Logo.png">
<pre>

</pre>

<!-- Builds -->
<a name="builds"></a>
<table class="summary" border="1" cellpadding="3"
       cellspacing="0" width="600" bgcolor="white">
  <tr bgcolor="#70b0f0" class="table-header">
    <td colspan="2" class="table-header">
    <span class="table-header">Development Snapshot Builds</span></td>
  </tr>

  <tr>
    <td width="15%" align="right" valign="top" class="summary">
      <span class="summary-type">Summary</span></td>
    <td class="summary">
      Application installers based on the latest code.
      <p>
      <b>WARNING:</b> These builds have not been tested and may be buggy or broken. They may have missing images and old dates and information. Applications installed from these files might crash on startup. They might delete all your files and cause your computer to burst into flames.
      </td>
  </tr>

  <tr>
    <td width="15%" align="right" valign="top" class="summary">
      <span class="summary-type">NanoEngineer-1 Application Suite</span></td>
    <td class="summary">
      Includes:
      <ul>
        <li>NanoEngineer-1
        <li>GROMACS+HDF5
        <li>QuteMolX
        <li>NanoVision-1
      </ul>
      <span class="summary-name"><?php include 'suite_links'; ?></span>
      <p>
      </td>
  </tr>

  <tr>
    <td width="15%" align="right" valign="top" class="summary">
      <span class="summary-type">NanoEngineer-1</span></td>
    <td class="summary">
      <span class="summary-name"><?php include 'ne1_links'; ?></span>
      <p>
      </td>
  </tr>

  <tr>
    <td width="15%" align="right" valign="top" class="summary">
      <span class="summary-type">GROMACS+HDF5</span></td>
    <td class="summary">
      <span class="summary-name"><?php include 'gmx_links'; ?></span>
      <p>
      </td>
  </tr>
  <tr>
    <td width="15%" align="right" valign="top" class="summary">
      <span class="summary-type">QuteMolX</span></td>
    <td class="summary">
      <span class="summary-name"><?php include 'qmx_links'; ?></span>
      <p>
      </td>
  </tr>
  <tr>
    <td width="15%" align="right" valign="top" class="summary">
      <span class="summary-type">NanoVision-1</span></td>
    <td class="summary">
      <span class="summary-name"><?php include 'nv1_links'; ?></span>
      <p>
      </td>
  </tr>
  <tr>
    <td width="15%" align="right" valign="top" class="summary">
      <span class="summary-type">Software Development Kits</span></td>
    <td class="summary">
      <span class="summary-name"><?php include 'sdk_links'; ?></span>
      <p>
      </td>
  </tr>
</table>

</body>
</html>
