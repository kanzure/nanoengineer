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

      <th>&nbsp;&nbsp;&nbsp;<a
        href="#qa">QA</a>&nbsp;&nbsp;&nbsp;</th>

      <th nowrap>&nbsp;&nbsp;&nbsp;<a
        href="NE1_Documentation">NE1 API Docs</a>&nbsp;&nbsp;&nbsp;</th>

      <th nowrap>&nbsp;&nbsp;&nbsp;<a
        href="#builds">Nightly Builds</a>&nbsp;&nbsp;&nbsp;</th>

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
       cellspacing="0" width="600" bgcolor="white">
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
       cellspacing="0" width="600" bgcolor="white">
  <tr bgcolor="#70b0f0" class="table-header">
    <td colspan="2" class="table-header">
    <span class="table-header">QA Test Harness</span></td>
  </tr>

  <tr>
    <td width="15%" align="right" valign="top" class="summary">
      <span class="summary-type">Summary</span></td>
    <td class="summary">This mechanism runs the following Quality Assurance tools: <a href="http://www.logilab.org/project/eid/857">Pylint</a> and a custom dependency cycles discovery tool. Coming soon: Pychecker, Pyunit, and more.</td>
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
          <td><span class="summary-name"><?php include 'Pylint.result'; ?>&nbsp;out of 10.0</span></td>
          <td><a href="SVN-D/cad/src/pylint_global.0.html">Detail</a> (Filtered: <a href="W0611.txt">W0611</a>*  <a href="E0602.txt">E0602</a>*)</td></tr>
        <tr>
          <td valign="top" align="right">Dependency cycles: </td>
          <td valign="top"><span class="summary-name">Modules (arcs): <?php include 'depend.dot.lines'; ?>&nbsp;</span></td>
          <td><a href="depend.dot">depend.dot</a></td></tr>
        <tr>
          <td></td>
          <td valign="top"><span class="summary-name">Packages (arcs): <?php include 'dependpack.dot.lines'; ?>&nbsp;</span></td>
          <td><a href="dependpack.dot">dependpack.dot</a></td></tr>
      </table></td>
  </tr>

  <tr>
    <td width="15%" align="right" valign="top" class="summary">
      <span class="summary-type">Logs</span></td>
    <td class="summary">
      <span class="summary-name"><!--<a href="QA_TestHarness.log">QA_TestHarness.log</a><br>--><a href="Pylint.log">Pylint.log</a> <a href="DependencyCycles.log">DependencyCycles.log</a></span></td>
  </tr>

  <tr>
    <td width="15%" align="right" valign="top" class="summary">
      <span class="summary-type">Notes</span></td>
    <td class="summary">
      <b>Pylint:</b> Each convention, refactor, warning, and error message code is following by a brief description, but if that is insufficient, you can get a slightly more informative description for it here: <a href="http://www.logilab.org/card/wikiid/pylintfeatures">Pylint man page</a>
      <p>
      <b>Dependency cycles:</b> Fewer arcs is better. Zero is ideal, but not always possible with respect to code clarity and convenience.
      <p>
      * W0611 - Unused import warning. Emitted when an imported module or variable is not used.
      <p>
      * E0602 - Undefined variable error. Emitted when a non-builtin symbol is used, but no definition or import of it can be found.</td>
  </tr>
</table>
<pre>

</pre>

<!-- Epydoc -->
<a name="epydoc"></a>
<table class="summary" border="1" cellpadding="3"
       cellspacing="0" width="600" bgcolor="white">
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
       cellspacing="0" width="600" bgcolor="white">
  <tr bgcolor="#70b0f0" class="table-header">
    <td colspan="2" class="table-header">
    <span class="table-header">Nightly Builds</span></td>
  </tr>

  <tr>
    <td width="15%" align="right" valign="top" class="summary">
      <span class="summary-type">Summary</span></td>
    <td class="summary">

Currently disabled.</td></tr></table>
<!--
      Created nightly from the previous day's work, these builds may or may not work. Use them to verify that a bug you're tracking has been fixed.
      <p>
      We make nightly builds for testing only. We write code and post the results right away so people like you can join our testing process and report bugs. You will find bugs, and lots of them. NanoEngineer-1 might crash on startup. It might delete all your files and cause your computer to burst into flames. Don't bother downloading nightly builds if you're unwilling to put up with problems.
      </td>
  </tr>

  <tr>
    <td width="15%" align="right" valign="top" class="summary">
      <span class="summary-type">Last run</span></td>
    <td class="summary">
      <span class="summary-name"><?php include 'NightlyBuild.timestamp'; ?></span> (Run every night.)</td>
  </tr>

  <tr>
    <td width="15%" align="right" valign="top" class="summary">
      <span class="summary-type">Last result</span></td>
    <td class="summary">
      <span class="summary-name"><?php include 'NightlyBuild.result'; ?></span></td>
  </tr>

  <tr>
    <td width="15%" align="right" valign="top" class="summary">
      <span class="summary-type">Log</span></td>
    <td class="summary">
      <span class="summary-name"><a href="http://www.nanohive-1.org/Engineering/NightlyBuild.log">NightlyBuild.log</a></span></td>
  </tr>

  <tr>
    <td width="15%" align="right" valign="top" class="summary">
      <span class="summary-type">Last build</span></td>
    <td class="summary">
      <span class="summary-name"><?php include 'NightlyBuild.filename'; ?></span>
      <table>
        <tr><td>Cross-platform source-code&nbsp;&nbsp;</td><?php include 'tar.gz.frag'; ?></tr>
        <tr><td>Mac OS X installer</td><td><span class="summary-name"><a href="#">dmg</a></span></td><td><span class="summary-name">[30.5 Mb]</span></td></tr>
        <tr><td>Linux RPM</td><td><span class="summary-name"><a href="#">rpm</a></td><td><span class="summary-name">[10.1 Mb]</span></td></tr>
      </table>
  </tr>

  <tr>
    <td width="15%" align="right" valign="top" class="summary">
      <span class="summary-type">Notes</span></td>
    <td class="summary">
      Nightly build serial numbers, for example NanoEngineer-1_0.9.2_<b>070806a</b>, correspond to the date that the build was created followed by a letter corresponding to that day's build. 070806a indicates the first build (a) on August 6 (0806), 2007 (07). 070806b would indicate the second build (b) on that day.</td>
  </tr>

  <tr>
    <td width="15%" align="right" valign="top" class="summary">
      <span class="summary-type">Build archives</span></td>
    <td class="summary">
      <span class="summary-name">
      <table>
        <?php include 'archives.frag'; ?>
      </table>
      </span>
  </tr>
</table>
-->

</body>
</html>
