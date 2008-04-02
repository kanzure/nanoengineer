#ifndef __RAGELISTREAMPTR_H__
#define __RAGELISTREAMPTR_H__

#include <iostream>
#include <cassert>

class RagelIstreamPtr {
public:
	RagelIstreamPtr() : istream_ref(NULL), pos(0) {}
    
    RagelIstreamPtr(std::istream& instream,
                    std::streamoff off=0,
                    std::ios::seekdir dir=std::ios::beg);
    
    ~RagelIstreamPtr() {}
    
    RagelIstreamPtr& operator = (std::istream *istreamPtr);
    
    RagelIstreamPtr& operator ++ (void);
    RagelIstreamPtr operator ++ (int);
    RagelIstreamPtr& operator -- (void);
    RagelIstreamPtr operator -- (int);
    RagelIstreamPtr& operator += (int n);
    RagelIstreamPtr& operator -= (int n);
	
	std::streamoff operator - (RagelIstreamPtr const& istreamPtr);
    
    char operator * (void);
    
protected:
    std::istream *istream_ref;
    std::streampos pos;

    friend bool operator == (RagelIstreamPtr const& r1,
                             RagelIstreamPtr const& r2);
	
    friend RagelIstreamPtr operator + (RagelIstreamPtr const& p, int const& n);
    friend RagelIstreamPtr operator - (RagelIstreamPtr const& p, int const& n);
};


namespace std {

template<>
	struct iterator_traits<RagelIstreamPtr>
{
	typedef random_access_iterator_tag iterator_category;
	typedef char                        value_type;
	typedef std::streamoff              difference_type;
	// typedef RagelIstreamPtr             pointer;
	//typedef char&                        reference;
};

}

inline
bool operator == (RagelIstreamPtr const& r1, RagelIstreamPtr const& r2)
{
    bool istream_same = (r1.istream_ref == r2.istream_ref);
    bool pos_same = (r1.pos == r2.pos);
    return (istream_same && pos_same);
}


inline
bool operator != (RagelIstreamPtr const& r1, RagelIstreamPtr const& r2)
{
    return !(r1 == r2);
}


inline
RagelIstreamPtr operator + (RagelIstreamPtr const& p, int const& n)
{
    
    return RagelIstreamPtr(*(p.istream_ref), p.pos+(std::streamoff)n);
}


inline
RagelIstreamPtr operator - (RagelIstreamPtr const& p, int const& n)
{
    
    return RagelIstreamPtr(*(p.istream_ref), p.pos-(std::streamoff)n);
}



inline RagelIstreamPtr::RagelIstreamPtr(std::istream& instream,
                                        std::streamoff off,
                                        std::ios::seekdir dir)
: istream_ref(&instream), pos(0)
{
    // save current position
    std::streamoff currPos = istream_ref->tellg();
    // move to given position and test
    istream_ref->seekg(off, dir);
    pos = istream_ref->tellg();
    // restore saved position
    istream_ref->seekg(currPos, std::ios::beg);
}


#if 0
inline RagelIstreamPtr::RagelIstreamPtr(std::istream *istreamPtr,
                                        std::streampos istreamPos)
: istream_ref(istreamPtr), pos(istreamPos)
{
    std::streamoff delta = pos - istreamPtr->tellg();
    istream_ref->seekg(delta, std::ios::cur);
}
#endif


inline RagelIstreamPtr&
RagelIstreamPtr::operator = (std::istream *istreamPtr)
{
    istream_ref = istreamPtr;
    pos = std::ios::beg;
    return *this;
}


inline RagelIstreamPtr& RagelIstreamPtr::operator ++ (void)
{
    // istream_ref->seekg(1, std::ios::cur);
    // pos = istream_ref->tellg(); // to trap errors
    pos += 1;
    return *this;
}


inline RagelIstreamPtr RagelIstreamPtr::operator ++ (int)
{
    RagelIstreamPtr retval = *this;
    // istream_ref->seekg(1, std::ios::cur);
    // pos = istream_ref->tellg(); // to trap errors
    pos += 1;
    return retval;
}


inline RagelIstreamPtr& RagelIstreamPtr::operator -- (void)
{
//     istream_ref->seekg(-1, std::ios::cur);
//     pos = istream_ref->tellg(); // to trap errors
    pos -= 1;
    return *this;
}


inline RagelIstreamPtr RagelIstreamPtr::operator -- (int)
{
     RagelIstreamPtr retval = *this;
//     istream_ref->seekg(-1, std::ios::cur);
//     pos = istream_ref->tellg(); // to trap errors
    pos -= 1;
    return retval;
}


inline RagelIstreamPtr& RagelIstreamPtr::operator += (int n)
{
//     istream_ref->seekg((std::streampos) n, std::ios::cur);
//     pos = istream_ref->tellg(); // to trap errors
    pos += n;
    return *this;
}


inline RagelIstreamPtr& RagelIstreamPtr::operator -= (int n)
{
//     istream_ref->seekg((std::streampos) (-n), std::ios::cur);
//     pos = istream_ref->tellg(); // to trap errors
    pos -= n;
    return *this;
}


// inline RagelIstreamPtr RagelIstreamPtr::operator + (int n) const
// {
//     return RagelIstreamPtr(istream_ref, pos+n);
// }
// 
// 
// inline RagelIstreamPtr RagelIstreamPtr::operator - (int n) const
// {
//     return RagelIstreamPtr(istream_ref, pos-n);
// }


inline
std::streamoff RagelIstreamPtr::operator - (RagelIstreamPtr const& istreamPtr)
{
	assert(istream_ref == istreamPtr.istream_ref);
	std::streamoff diff = pos - istreamPtr.pos;
	return diff;
}


inline char RagelIstreamPtr::operator * (void)
{
    istream_ref->seekg(pos - istream_ref->tellg(), std::ios::cur);
    return istream_ref->peek();
}


#endif // __RAGELISTREAMPTR_H__
