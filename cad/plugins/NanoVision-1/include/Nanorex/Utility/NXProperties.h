// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#ifndef NX_PROPERTIES_H
#define NX_PROPERTIES_H

#ifdef WIN32
#	ifdef _MSC_VER
#		pragma warning(disable:4786)
#	endif
#endif

#include <map>
#include <vector>
#include <string>
#include <iostream>
#include <fstream>

namespace Nanorex {


/* CLASS: NXProperties */
/**
 * A set of key/value pairs.
 * @ingroup NanorexUtility
 */
class NXProperties {
	public:
		NXProperties();
		~NXProperties();
		std::string writeToFile(const std::string& filename);
		std::string readFromFile(const std::string& filename);
		void setProperty(const std::string& key, const std::string& value);
		void addProperties(NXProperties* newProps, const char* prePendChars);
		bool keyExists(const char* key);
		const char* getProperty(const char* key);
		const char* getProperty(const char* key, const char* defaultValue);
		const char* getProperty(const std::string& key);
		const char* getProperty(const std::string& key,
								const char* defaultValue);
		std::vector<std::string> getPropertyKeys();
		void clear();

	private:
		std::map<std::string, std::string> properties;

		void deSerializeLine(const std::string& dataLine);
};

} // Nanorex::

#endif
