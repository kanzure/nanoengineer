/*------------------------------------------------------
   CCmdLine

   A utility for parsing command lines.

   Copyright (C) 1999 Chris Losinger, Smaller Animals Software.
   http://www.smalleranimals.com

   This software is provided 'as-is', without any express
   or implied warranty.  In no event will the authors be 
   held liable for any damages arising from the use of this software.

   Permission is granted to anyone to use this software 
   for any purpose, including commercial applications, and 
   to alter it and redistribute it freely, subject to the 
   following restrictions:

     1. The origin of this software must not be misrepresented; 
   you must not claim that you wrote the original software. 
   If you use this software in a product, an acknowledgment 
   in the product documentation would be appreciated but is not required.
   
     2. Altered source versions must be plainly marked as such, 
   and must not be misrepresented as being the original software.
   
     3. This notice may not be removed or altered from any source 
   distribution.

  -------------------------

   Example :
*/
/*! \class Nanorex::NXCommandLine

   Note: This class is a derivative work of Chris Losinger's CCmdLine class
   Copyright (C) 1999 Chris Losinger, Smaller Animals Software
   (www.smalleranimals.com).
   Nano-Hive added the
   \code int SplitLine(const char *line); \endcode function and made the
   documentation Doxygen friendly.

   Our example application uses a command line that has two
   required switches and two optional switches. The app should abort
   if the required switches are not present and continue with default
   values if the optional switches are not present.

      Sample command line : 
	  \code
      MyApp.exe -p1 text1 text2 -p2 "this is a big argument" -opt1 -55 -opt2
	  \endcode

      Switches -p1 and -p2 are required. 
      p1 has two arguments and p2 has one.
      
      Switches -opt1 and -opt2 are optional. 
      opt1 requires a numeric argument. 
      opt2 has no arguments.
      
      Also, assume that the app displays a 'help' screen if the '-h' switch
      is present on the command line.

   \code
   #include "Nanorex/Utility/NXCommandLine.h"

   void main(int argc, char **argv)
   {
      // our cmd line parser object
      Nanorex::NXCommandLine cmdLine;

      // parse argc,argv 
      if (cmdLine.SplitLine(argc, argv) < 1)
      {
         // no switches were given on the command line, abort
         ASSERT(0);
         exit(-1);
      }

      // test for the 'help' case
      if (cmdLine.HasSwitch("-h"))
      {
         show_help();
         exit(0);
      }

      // get the required arguments
      StringType p1_1, p1_2, p2_1;
      try
      {  
         // if any of these fail, we'll end up in the catch() block
         p1_1 = cmdLine.GetArgument("-p1", 0);
         p1_2 = cmdLine.GetArgument("-p1", 1);
         p2_1 = cmdLine.GetArgument("-p2", 0);

      }
      catch (...)
      {
         // one of the required arguments was missing, abort
         ASSERT(0);
         exit(-1);
      }

      // get the optional parameters

      // convert to an int, default to '100'
      int iOpt1Val =    atoi(cmdLine.GetSafeArgument("-opt1", 0, 100));

      // since opt2 has no arguments, just test for the presence of
      // the '-opt2' switch
      bool bOptVal2 =   cmdLine.HasSwitch("-opt2");

      .... and so on....

   }
   \endcode
*/
/*
   If this class is used in an MFC application, StringType is CString, else
   it uses the STL 'string' type.

   If this is an MFC app, you can use the __argc and __argv macros from
   you CYourWinApp::InitInstance() function in place of the standard argc 
   and argv variables. 

------------------------------------------------------*/
#ifndef NH_CMDLINE_H
#define NH_CMDLINE_H


#define StringType std::string


#ifdef WIN32
#	ifdef _MSC_VER
#		pragma warning(disable:4786)
#	endif
#endif

#include <iostream>
#include <map>
#include <string>
#include <vector>

namespace Nanorex {

/* Container for the CmdLine argument vector. */
/**
 * Used internally by nanohive::CmdLine.
 */
struct CCmdParam
{
   std::vector<StringType> m_strings;
};

// this class is actually a map of strings to vectors
typedef std::map<StringType, CCmdParam> _CCmdLine;

/**
 * Command-line parser class.
 * @ingroup NanoHiveUtil
 */
class NXCommandLine : public _CCmdLine
{

public:
	/**
      Parse the command line into switches and arguments.

      @return Number of switches found
	 */
   int         SplitLine(int argc, char **argv);

	/**
      Parse the given line into switches and arguments.

      @return Number of switches found
	 */
   int         SplitLine(const char *line);

	/**
      Was the switch found on the command line ?

      example :
	  \code
	  app.exe -a p1 p2 p3 -b p4 -c -d p5

      call                          return
      ----                          ------
      cmdLine.HasSwitch("-a")       true
      cmdLine.HasSwitch("-z")       false
	  \endcode
	 */
   bool        HasSwitch(const char *pSwitch);

	/**
      Fetch an argument associated with a switch . if the parameter at
      index iIdx is not found, this will return the default that you
      provide.

      example :
	  \code
	  app.exe -a p1 p2 p3 -b p4 -c -d p5

      call                                      return
      ----                                      ------
      cmdLine.GetSafeArgument("-a", 0, "zz")    p1
      cmdLine.GetSafeArgument("-a", 1, "zz")    p2
      cmdLine.GetSafeArgument("-b", 0, "zz")    p4
      cmdLine.GetSafeArgument("-b", 1, "zz")    zz
	  \endcode
	 */
   StringType  GetSafeArgument(const char *pSwitch, int iIdx, const char *pDefault);

	/**
      Fetch a argument associated with a switch. throws an exception 
      of (int)0, if the parameter at index iIdx is not found.

      example :
	  \code
      app.exe -a p1 p2 p3 -b p4 -c -d p5

      call                             return
      ----                             ------
      cmdLine.GetArgument("-a", 0)     p1
      cmdLine.GetArgument("-b", 1)     throws (int)0, returns an empty string
	  \endcode
	 */
   StringType  GetArgument(const char *pSwitch, int iIdx); 

	/**
      @return	The number of arguments found for a given switch. -1 if the
				switch was not found
	 */
   int         GetArgumentCount(const char *pSwitch);

protected:
   /*------------------------------------------------------

   protected member function
   test a parameter to see if it's a switch :

   switches are of the form : -x
   where 'x' is one or more characters.
   the first character of a switch must be non-numeric!

   ------------------------------------------------------*/
   bool        IsSwitch(const char *pParam);
};

} // Nanorex::

#endif

