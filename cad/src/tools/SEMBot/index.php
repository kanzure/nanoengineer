<?php

require_once("util.inc");

page_head("");

?>
<body>
<table class="navbar" border="0" width="100%" cellpadding="0"
       bgcolor="#a0c0ff" cellspacing="0">

  <tr valign="middle">
      <th bgcolor="#70b0f0" class="navbar-select"
          >&nbsp;&nbsp;&nbsp;Home&nbsp;&nbsp;&nbsp;</th>

      <th nowrap>&nbsp;&nbsp;&nbsp;<a
        href="NE1_Documentation">NE1 API Docs</a>&nbsp;&nbsp;&nbsp;</th>

      <th>&nbsp;&nbsp;&nbsp;<a
        href="#qa">QA</a>&nbsp;&nbsp;&nbsp;</th>

      <th>&nbsp;&nbsp;&nbsp;<a
        href="#">Builds</a>&nbsp;&nbsp;&nbsp;</th>

      <th class="navbar" align="right" width="100%">
        <table border="0" cellpadding="0" cellspacing="0">
          <tr><th class="navbar" align="center">Nanorex Software-Engineering Mechanisms Robot (SEMBot)&nbsp;&nbsp;&nbsp;<a href="http://www.nanoengineer-1.net/" target="_top">NE1 Wiki</a>&nbsp;&nbsp;&nbsp;</th>
          </tr></table></th>
  </tr>
</table>

<p>
<img align="right" src="Engineer-X-Man-Logo.png">
Welcome to the Nanorex Software-Engineering Mechanisms Robot (SEMBot).
<pre>

</pre>

<!-- SEMBot -->
<table class="summary" border="1" cellpadding="3"
       cellspacing="0" width="500" bgcolor="white">
  <tr bgcolor="#70b0f0" class="table-header">
    <td colspan="2" class="table-header">
    <span class="table-header">SEMBot</span></td>
  </tr>

  <tr>
    <td width="15%" align="right" valign="top" class="summary">
      <span class="summary-type">Summary</span></td>
    <td class="summary">This mechanism updates a local copy of the NE1 codebase, then automates the execution of the following set of software engineering tools against that codebase.</td>
  </tr>

  <tr>
    <td width="15%" align="right" valign="top" class="summary">
      <span class="summary-type">Last run</span></td>
    <td class="summary">
      <span class="summary-name"><?php include 'SEMBot.timestamp'; ?></span> (Run every night.)</td>
  </tr>

  <tr>
    <td width="15%" align="right" valign="top" class="summary">
      <span class="summary-type">Last result</span></td>
    <td class="summary">
      <span class="summary-name"><?php include 'SEMBot.result'; ?></span></td>
  </tr>

  <tr>
    <td width="15%" align="right" valign="top" class="summary">
      <span class="summary-type">Log</span></td>
    <td class="summary">
      <span class="summary-name"><a href="http://www.nanohive-1.org/Engineering/SEMBot.log">SEMBot.log</a></span></td>
  </tr>

  <tr>
    <td width="15%" align="right" valign="top" class="summary">
      <span class="summary-type">Notes</span></td>
    <td class="summary">
      SEMBot files are checked in under /cad/src/tools/SEMBot/ and are updated before each run.</td>
  </tr>
</table>
<pre>

</pre>

<!-- QA Test Harness -->
<a name="qa"></a>
<table class="summary" border="1" cellpadding="3"
       cellspacing="0" width="500" bgcolor="white">
  <tr bgcolor="#70b0f0" class="table-header">
    <td colspan="2" class="table-header">
    <span class="table-header">QA Test Harness</span></td>
  </tr>

  <tr>
    <td width="15%" align="right" valign="top" class="summary">
      <span class="summary-type">Summary</span></td>
    <td class="summary">This mechanism runs the following Quality Assurance tools: <a href="http://www.logilab.org/project/eid/857">Pylint</a>. Coming soon: Pychecker, Pyunit, and more.</td>
  </tr>

  <tr>
    <td width="15%" align="right" valign="top" class="summary">
      <span class="summary-type">Last run</span></td>
    <td class="summary">
      <span class="summary-name"><?php include 'QA_TestHarness.timestamp'; ?></span> (Run every night.)</td>
  </tr>

  <tr>
    <td width="15%" align="right" valign="top" class="summary">
      <span class="summary-type">Last results</span></td>
    <td class="summary">
      <table border="0" cellpadding="3" cellspacing="0" bgcolor="#e8f0f8">
        <tr>
          <td align="right">Harness: </td>
          <td><span class="summary-name"><?php include 'QA_TestHarness.result'; ?></span></td></tr>
        <tr>
          <td align="right">Pylint: </td>
          <td><span class="summary-name"><?php include 'Pylint.result'; ?>/10.0</span></td>
          <td><a href="SVN-D/cad/src/pylint_global.0.html">Detail</a></td></tr>
      </table></td>
  </tr>

  <tr>
    <td width="15%" align="right" valign="top" class="summary">
      <span class="summary-type">Logs</span></td>
    <td class="summary">
      <span class="summary-name"><a href="QA_TestHarness.log">QA_TestHarness.log</a><br><a href="Pylint.log">Pylint.log</a></span></td>
  </tr>

<!--
  <tr>
    <td width="15%" align="right" valign="top" class="summary">
      <span class="summary-type">Notes</span></td>
    <td class="summary">
      </td>
  </tr>
-->
</table>
<pre>

</pre>

<!-- Epydoc -->
<a name="epydoc"></a>
<table class="summary" border="1" cellpadding="3"
       cellspacing="0" width="500" bgcolor="white">
  <tr bgcolor="#70b0f0" class="table-header">
    <td colspan="2" class="table-header">
    <span class="table-header">Epydoc API Documentation Generation</span></td>
  </tr>

  <tr>
    <td width="15%" align="right" valign="top" class="summary">
      <span class="summary-type">Summary</span></td>
    <td class="summary">This mechanism runs <a href="http://epydoc.sourceforge.net/">Epydoc</a> on the codebase to generate formatted <a href="NE1_Documentation">NE1 API documentation</a>.</td>
  </tr>

  <tr>
    <td width="15%" align="right" valign="top" class="summary">
      <span class="summary-type">Last run</span></td>
    <td class="summary">
      <span class="summary-name"><?php include 'NE1_Docs.timestamp'; ?></span> (Updated every night.)</td>
  </tr>

  <tr>
    <td width="15%" align="right" valign="top" class="summary">
      <span class="summary-type">Last result</span></td>
    <td class="summary">
      <span class="summary-name"><?php include 'NE1_Docs.result'; ?></span></td>
  </tr>

  <tr>
    <td width="15%" align="right" valign="top" class="summary">
      <span class="summary-type">Log</span></td>
    <td class="summary">
      <span class="summary-name"><a href="http://www.nanohive-1.org/Engineering/NE1_Docs.log">NE1_Docs.log</a></span></td>
  </tr>

  <tr>
    <td width="15%" align="right" valign="top" class="summary">
      <span class="summary-type">Notes</span></td>
    <td class="summary">
      The Epydoc configuration file is checked in as /cad/src/epydoc.config and is updated before each Epydoc run.
      <p>
      To add images to your Epydoc documentation, use the following format: <tt>IMAGE(<i>URL</i>)</tt> which gets transcribed as <tt>&lt;img src="<i>URL</i>"&gt;</tt>
      <p>
      Epydoc chokes on <tt>__author__ = ['Mark', 'Bruce']</tt> so please use <tt>__author__ = "Mark, Bruce"</tt> instead.</td>
  </tr>
</table>
<pre>

</pre>

<!-- Builds -->
<a name="builds"></a>
<table class="summary" border="1" cellpadding="3"
       cellspacing="0" width="500" bgcolor="white">
  <tr bgcolor="#70b0f0" class="table-header">
    <td colspan="2" class="table-header">
    <span class="table-header">Builds</span></td>
  </tr>

  <tr>
    <td width="15%" align="right" valign="top" class="summary">
      <span class="summary-type">Summary</span></td>
    <td class="summary">Nightly builds, etc.</td>
  </tr>
</table>

</body>
</html>
