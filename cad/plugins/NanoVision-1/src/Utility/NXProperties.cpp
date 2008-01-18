// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#include "Nanorex/Utility/NXProperties.h"

namespace Nanorex {


/* CONSTRUCTOR */
/**
 * Constructs an empty NXProperties object.
 */
NXProperties::NXProperties() {
}


/* DESTRUCTOR */
NXProperties::~NXProperties() {
}


/* FUNCTION: writeToFile */
/**
 * Writes these properties to the given file. The format of the file is as
 * follows:
 *
	\code
	key1=value1
	key2=value2
	...
	\endcode
 *
 * @return	If the given file was successfully opened and completely written, an
 * empty string ("") is returned. Otherwise, an error message is returned.
 */
std::string NXProperties::writeToFile(const std::string& filename) {
	std::string errors = "";

	// Open file for reading.
	std::ofstream outFile(filename.c_str(), std::ios::out);
	if (!outFile) {
		errors = "File could not be opened: " + filename + ".";

	} else {
		std::string line;
		std::map<std::string, std::string>::iterator iter;
		for (iter = properties.begin(); iter != properties.end(); iter++) {
			line = iter->first;
			line += "=";
			line += iter->second;
			outFile << line << std::endl;
		}
		outFile.close();
	}
	return errors;
}


/* FUNCTION: readFromFile */
/**
 * Opens the given file and reads in the properties it contains. The format
 * of the file is as follows:
 *
	\code
	# Comment
	key1=value1
	key2=value2
	...
	\endcode
 *
 * Comments and blank lines are ignored as are white space around keys and
 * values.
 *
 * @return	If the given file was successfully opened and completely read, an
 * empty string ("") is returned. Otherwise, an error message is returned if
 * any line in the input file is malformed. The whole file is read and parsed
 * and all good/well-formed lines are incorporated into this set of properties.
 */
std::string NXProperties::readFromFile(const std::string& filename) {
	std::string errors = "";

	// Open file for reading.
	std::ifstream inFile(filename.c_str(), std::ios::in);
	if (!inFile) {
		errors = "File could not be opened: " + filename + ".";

	} else {
		// Read properties.
		std::string line;
		while (std::getline(inFile, line, '\n')) {
			try {
				deSerializeLine(line);
			} catch (...) {
				errors += " Bad line: " + line;
			}
		}
		inFile.close();
	}
	return errors;
}


/* FUNCTION: setProperty */
/**
 * Sets the given key's value.
 */
void NXProperties::setProperty(const std::string& key,
							   const std::string& value) {
	properties[key] = value;
}


/* FUNCTION; addProperties */
/**
 * Adds the given Properties to this Properties object, prepending the key of
 * each new key/value pair with the given string. Any existing properties will
 * be over-ridden by those found in the new Properties.
 *
 * @param	newProps
 *			The new key/value pairs to add.
 * @param	prePendChars
 *			The string to prepend to each new key/value pair's key.
 */
void NXProperties::addProperties(NXProperties* newProps,
								 const char* prePendChars) {
	std::string prePendString = std::string(prePendChars);

	std::map<std::string, std::string>::iterator newPropsIter;
	for (newPropsIter = newProps->properties.begin();
		 newPropsIter != newProps->properties.end();
		 newPropsIter++) {
		properties[prePendString + newPropsIter->first] = newPropsIter->second;
	}
}


/* FUNCTION: keyExists */
bool NXProperties::keyExists(const char* key) {
	return (properties.count(key) != 0);
}


/* FUNCTION: getProperty */
/**
 * Returns the value of the given key, or an empty string if the key is not
 * found.
 */
const char* NXProperties::getProperty(const char* key) {
	const char* value = properties[std::string(key)].c_str();
	return value;
}
/**
 * Returns the value of the given key, or an empty string if the key is not
 * found.
 */
const char* NXProperties::getProperty(const std::string& key) {
	const char* value = properties[key].c_str();
	return value;
}
/**
 * Returns the value of the given key with an optional default value if the key
 * is not found.
 */
const char* NXProperties::getProperty(const char* key,
									  const char* defaultValue) {
	if (properties.count(key) == 0)
		return defaultValue;
	else
		return getProperty(key);
}
/**
 * Returns the value of the given key with an optional default value if the key
 * is not found.
 */
const char* NXProperties::getProperty(const std::string& key,
									const char* defaultValue) {
	if (properties.count(key) == 0)
		return defaultValue;
	else
		return getProperty(key);
}


/* FUNCTION: getPropertyKeys */
/**
 * Returns all the keys in a vector.
 */
std::vector<std::string> NXProperties::getPropertyKeys() {
	std::vector<std::string> keys;
	std::map<std::string, std::string>::iterator iter = properties.begin();
	std::map<std::string, std::string>::iterator iterEnd = properties.end();
	while (iter != iterEnd) {
		keys.push_back(iter->first);
		iter++;
	}
	return keys;
}


/* FUNCTION: clear */
/**
 * Clears all properties.
 */
void NXProperties::clear() {
	properties.clear();
}


/* FUNCTION: deSerializeLine */
void NXProperties::deSerializeLine(const std::string& dataLine) {
	std::string key, value;
	std::string line = dataLine;

	// Trim front.
	while ((line.length() != 0) && (line[0] == ' '))
		line.erase(0, 1);

	// Ignore commented and blank lines
	if ((line.length() == 0) || (line[0] == '#'))
		return;

	// Get key/value pair
	unsigned int index = line.find("=", 1);
	if (index != std::string::npos) {

		key = line.substr(0, index);
		// Trim end.
		while ((key.length() != 0) && (key[key.length() - 1] == ' '))
			key.erase(key.length() - 1, 1);

		value = line.substr(index + 1, line.length() - 1);
		//Trim front.
		while ((value.length() != 0) && (value[0] == ' '))
			value.erase(0, 1);
		// Trim end.
		while ((value.length() != 0) && (value[value.length() - 1] == ' '))
			value.erase(value.length() - 1, 1);

		// Add to table
		properties[key] = value;
	}
}

} // Nanorex::
