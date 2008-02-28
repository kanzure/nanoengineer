#include "glt_error.h"

#include <string>
using namespace std;

//#ifdef GLT_WIN32
//#include <windows.h>
//#endif

/*! \file
    \ingroup GLT
    
    $Id: error.cpp,v 1.2 2002/10/09 15:09:38 nigels Exp $
    
    $Log: error.cpp,v $
    Revision 1.2  2002/10/09 15:09:38  nigels
    Added RCS Id and Log tags


*/        
    
void 
gltError(const std::string &message)
{
	//#ifdef GLT_WIN32
	//MessageBox(NULL,message.c_str(),"Runtime Error",MB_OK | MB_ICONERROR);
	//#endif
	printf("GLT Error: %s\n", message.c_str());
}

void 
gltWarning(const std::string &message)
{
	//#ifdef GLT_WIN32
	//MessageBox(NULL,message.c_str(),"Runtime Warning",MB_OK | MB_ICONWARNING);
	//#endif
	printf("GLT Warning: %s\n", message.c_str());
}
