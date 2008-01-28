#include "glt_string.h"

/*! \file 
	\brief   string and wstring utility routines 
	\ingroup Misc
*/

/*! \example string.cpp

	String functionality example and regression test.

	Output:
	\include string.ok
*/

#include <cassert>
#include <cstdlib>
#include <iostream>
#include <iomanip>
using namespace std;

bool isBinary(const std::string  &str)
{
	const char *begin = str.c_str();
	const char *end   = begin + str.size();

	for (const char *i=begin; i!=end; i++)
	{
		char c = *i;
		if ((c<32 || c>126) && c!='\t' && c!='\r' && c!='\n')
			return true;
	}

	return false;
}

// Note, would be faster perhaps to use char *
// instead of integer index

void dos2unix(string &dest,const string &src)
{
	// Find the size of the destination string

	string::size_type size = src.size();
	for (string::size_type i=0;i<src.size();i++)
		if (src[i]==13)
			size--;

	// Bail out early, if possible

	if (size==src.size())
	{
		dest = src;
		return;
	}

	// Allocate the correct size for destination

	dest.resize(size);

	// Copy everything except ASCII 13

	string::size_type k = 0;
	for (string::size_type j=0;j<src.size();j++)
		if (src[j]!=13)
			dest[k++] = src[j];

	assert(k==size);
}

void dos2unix(wstring &dest,const wstring &src)
{
	// Remove all instances of carriage return (ASCII 13)

	// Find the size of the destination string

	wstring::size_type size = src.size();
	for (wstring::size_type i=0;i<src.size();i++)
		if (src[i]==13)
			size--;

	// Bail out early, if possible

	if (size==src.size())
	{
		dest = src;
		return;
	}

	// Allocate the correct size for destination

	dest.resize(size);

	// Copy everything except the linefeeds

	wstring::size_type k = 0;
	for (wstring::size_type j=0;j<src.size();j++)
		if (src[j]!=13)
			dest[k++] = src[j];

	assert(k==size);
}

void unix2dos(string &dest,const string &src)
{
	// Insert carriage returns, where necessary (ASCII 13)

	// Find the size of the destination string

	string::size_type size = src.size();

	// Take first character into account

	if (src.size()>0)
		if (src[0]==10)
			size++;

	for (string::size_type i=0;i<src.size()-1;i++)
		if (src[i]!=13 && src[i+1]==10)
			size++;

	// Allocate the correct size for destination

	dest.resize(size);

	// Copy everything, inserting linefeeds where necessary

	string::size_type j = 0;
	string::size_type k = 0;

	if (src.size()>0)
		if (src[0]==10)
			dest[k++] = 13;

	for (;j<src.size()-1;j++)
		if (src[j]!=13 && src[j+1]==10)
		{
			dest[k++] = src[j];
			dest[k++] = 13;
		}
		else
			dest[k++] = src[j];

	if (j<src.size())
		dest[k++] = src[j++];

	assert(k==size);
}

void unix2dos(wstring &dest,const wstring &src)
{
	// Insert carriage returns, where necessary (ASCII 13)

	// Find the size of the destination string

	wstring::size_type size = src.size();

	// Take first character into account

	if (src.size()>0)
		if (src[0]==10)
			size++;

	for (wstring::size_type i=0;i<src.size()-1;i++)
		if (src[i]!=13 && src[i+1]==10)
			size++;

	// Allocate the correct size for destination

	dest.resize(size);

	// Copy everything, inserting linefeeds where necessary

	wstring::size_type j = 0;
	wstring::size_type k = 0;

	if (src.size()>0)
		if (src[0]==10)
			dest[k++] = 13;

	for (;j<src.size()-1;j++)
		if (src[j]!=13 && src[j+1]==10)
		{
			dest[k++] = src[j];
			dest[k++] = 13;
		}
		else
			dest[k++] = src[j];

	if (j<src.size())
		dest[k++] = src[j++];

	assert(k==size);
}

void readStream(istream &is,string &dest)
{
	while (is.good() && !is.eof())
	{
		const int bufferSize = 10240;
		char buffer[bufferSize];
		is.read(buffer,bufferSize);
		const int size = is.gcount();
		if (size>0)
			dest.insert(dest.end(),buffer,buffer+size);
	}
}

void writeStream(ostream &os,const string &src)
{
	os.write(src.c_str(),src.length());
}

// 
// Read a file into a Unicode string
//
// This function assumes that the file is
// in "normal" Unicode format, as a sequence
// of 16 bit codes.  The BOM (Byte Order
// Marker) is used to detect Unicode, and
// to swap endianess, if necessary. 
//

const wchar_t BOM  = 0xFEFF;
const wchar_t BOMe = 0xFFFE;	// Handle opposite endian

void readUnicodeStream(istream &is,wstring &dest)
{
	const int  bufferSize=1024;		// Buffer Size
	wchar_t    buffer[bufferSize];	// Buffer
	bool       firstBlock = true;	// Check header of first block
	bool       swap = false;		// Opposite Endian Origin

	dest = wstring();

	// As long as input stream is good

	while (is.good())
	{
		// Read into buffer and find out
		// how many bytes were read.

		is.read((char *) buffer,bufferSize*sizeof(wchar_t));
		int count = is.gcount()/sizeof(wchar_t);

		// If we read something, lets
		// do some processing.

		if (count)
		{
			// Check the first 16 bits
			// of first block for BOM
			// marker.  If it's in the
			// wrong order, enable swapping

			if (firstBlock)
			{
				if (buffer[0]!=BOM && buffer[0]!=BOMe)
					return;

				if (buffer[0]==BOMe)
					swap = true;

				firstBlock = false;
			}

			// If we're in swap mode,
			// swap high and low bytes
			// of each code

			if (swap)
				for (int c=0; c<count; c++)
					buffer[c] = (buffer[c]<<8)|(buffer[c]>>8);

			// Add the buffer to the 
			// Unicode string, ignoring
			// the BOM, if it exists as
			// the first element in the
			// buffer

			if (buffer[0]==BOM)
				dest.append(buffer+1,count-1);
			else
				dest.append(buffer,count);
		}
	}
}

//
// Write a unicode string to a file
//

void writeUnicodeStream(ostream &os,const wstring &src)
{
	os.write(reinterpret_cast<const char *>(&BOM),sizeof(wchar_t));
	os.write(reinterpret_cast<const char *>(src.data()),src.size()*sizeof(wchar_t));
}

void string2wstring(wstring &dest,const string &src)
{
	dest.resize(src.size());
	for (uint32 i=0; i<src.size(); i++)
		dest[i] = static_cast<unsigned char>(src[i]);
}

void wstring2string(string &dest,const wstring &src)
{
	dest.resize(src.size());
	for (uint32 i=0; i<src.size(); i++)
		dest[i] = src[i] < 256 ? src[i] : ' ';
}

//

// http://www.cl.cam.ac.uk/~mgk25/unicode.html#utf-8
//
// TODO: Support U-10000 onwards

void utf8decode(wstring &dest, const string &src)
{
	int i = 0;
	unsigned char *s = (unsigned char *) src.c_str();

        while (i<(int)src.size())
	{
		const wchar_t c = s[i++];

		// U-0 to U-7F 

		if ((c&0x80) == 0x00)
		{
			dest += c;
			continue;
		}

		// U-80 to U-7FF

		if ((c&0xE0) == 0xC0)
		{
                    if (i<(int)src.size())
			{
				const wchar_t d = s[i++];
				dest += (c&0x1f)<<6 | (d&0x3f);
				continue;
			}
		}

		// U-800 to U-FFFF

		if ((c&0xF0) == 0xE0)
		{
                    if ((i+1)<(int)src.size())
			{
				const wchar_t d = s[i++];
				const wchar_t e = s[i++];
				dest += (c&0x0f)<<12 | (d&0x3f)<<6 | (e&0x3f);
				continue;
			}
		}
	}
}

//

void bin2src_(std::ostream &os,bool &begin,const unsigned char *buffer,const int n)
{
	os.setf(ios::hex,ios::basefield);

	if (n>0 && !begin)
	{
		os << ',';
		os << endl;
	}

	begin = false;

	for (int i=0; i<n;i++)
	{
		os << "0x" << setw(2) << setfill('0') << (unsigned int) buffer[i];
		if (i<n-1)
			os << ',';
	}
}

void bin2src(std::ostream &os,const unsigned char *buffer,const int n)
{
	os << '{' << endl;
	
	bool begin = true;

	for (int i=0; i<n; i+=16)
		if (n-i>16)
			bin2src_(os,begin,buffer+i,16);
		else
			bin2src_(os,begin,buffer+i,n-i);

	os << endl << "};" << endl;
}

void bin2src(std::ostream &os, const std::string &src)
{
	bin2src(os,(const unsigned char *) src.c_str(),src.length());
}

void bin2src(std::ostream &os, std::istream &is)
{
	os << '{' << endl;
	
	bool begin = true;

	while (is.good() && !is.eof())
	{
		unsigned char buffer[16];
		is.read((char *) buffer,16);
		int size = is.gcount();
		bin2src_(os,begin,buffer,size);
	}

	os << endl << "};" << endl;
}

//

void bin2asm_(std::ostream &os,const unsigned char *buffer,const int n)
{
	if (n<=0)
		return;

	os.setf(ios::hex,ios::basefield);

	os << "\t.byte ";

	for (int i=0; i<n;i++)
	{
		os << "0x" << setw(2) << setfill('0') << (unsigned int) buffer[i];
		if (i<n-1)
			os << ',';
	}

	os << endl;
}

void bin2asm(std::ostream &os,const unsigned char *buffer,const int n)
{
	for (int i=0; i<n; i+=16)
		if (n-i>16)
			bin2asm_(os,buffer+i,16);
		else
			bin2asm_(os,buffer+i,n-i);
}

void bin2asm(std::ostream &os, const std::string &src)
{
	bin2asm(os,(const unsigned char *) src.c_str(),src.length());
}

void bin2asm(std::ostream &os, std::istream &is)
{
	while (is.good() && !is.eof())
	{
		unsigned char buffer[16];
		is.read((char *) buffer,16);
		int size = is.gcount();
		bin2asm_(os,buffer,size);
	}
}

unsigned int fromHex4(unsigned char ch)
{
	if (ch>='0' && ch<='9')
		return ch-'0';

	if (ch>='a' && ch<='f')
		return ch-'a'+10;

	if (ch>='A' && ch<='F')
		return ch-'A'+10;

	return 0;
}

unsigned char toHex4(unsigned int val)
{
	const unsigned char table[16] = { 
		'0', '1', '2', '3', '4', 
		'5', '6', '7', '8', '9', 
		'A', 'B', 'C', 'D', 'E', 'F'
	};

	return table[val&15];
}

bool stringSplit(vector<string> &vec,const string &str,const string &delim)
{
	vec.clear();

	if (delim.empty())
	{
		vec.push_back(str);
		return false;
	}

	string::size_type i = 0;
	string::size_type j = 0;

	for (;;)
	{
		j = str.find(delim,i);
		if (j==string::npos)
		{
			vec.push_back(str.substr(i));
			break;
		}

		vec.push_back(str.substr(i,j-i));
		i = j + delim.size();

		if (i==str.size())
		{
			vec.push_back(string());
			break;
		}
	}

	return true;
}

bool stringMerge(const vector<string> &vec, string &str,const string &delim)
{
	str = string();

        for (int i=0; i<(int)vec.size(); i++)
	{
		if (i>0)
			str += delim;

		str += vec[i];
	}

	return true;
}

double atof(const std::string &str) { return atof(str.c_str());                   }
int    atoi(const std::string &str) { return atoi(str.c_str());                   }
long   atol(const std::string &str) { return atol(str.c_str());                   }
bool   atob(const std::string &str) { return atoi(str.c_str())!=0 || str.substr(0,4)=="true"; }
