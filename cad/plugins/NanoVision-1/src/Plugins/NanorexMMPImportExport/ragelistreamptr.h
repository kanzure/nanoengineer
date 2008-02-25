#ifndef __RAGELISTREAMPTR_H__
#define __RAGELISTREAMPTR_H__

/* CLASS: RagelIstreamPtr */
/**
 * Behaves like a char* but actually sequentially accesses a file.
 * This is to fool Ragel into thinking that it is accessing a char[].
 * Implements just enough methods to be compatible with Ragel v6.0.
 */


class RagelIstreamPtr {
public:
    RagelIstreamPtr() {}
    RagelIstreamPtr(std::istream& instream,
                    std::streamoff off = 0,
                    std::ios::seekdir dir = std::ios::beg);
    ~RagelIstreamPtr() {}
    
    RagelIstreamPtr& operator ++ (void);
    RagelIstreamPtr operator ++ (int);
    RagelIstreamPtr& operator -- (void);
    RagelIstreamPtr operator -- (int);
    RagelIstreamPtr& operator += (int n);
    RagelIstreamPtr& operator -= (int n);
    
    char operator * (void);
    
protected:
    std::istream *istream_ref;
    std::streampos pos;

    friend bool operator == (RagelIstreamPtr const& r1,
                             RagelIstreamPtr const& r2);
};


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


inline RagelIstreamPtr::RagelIstreamPtr(std::istream& instream,
                                        std::streamoff off,
                                        std::ios::seekdir dir)
: istream_ref(&instream), pos(0)
{
    // save current position
    std::streamoff currPos = instream.tellg();
    // move to given position and test
    istream_ref->seekg(off, dir);
    pos = istream_ref->tellg();
    // restore saved position
    instream.seekg(currPos, std::ios::beg);
}


inline RagelIstreamPtr& RagelIstreamPtr::operator ++ (void)
{
    istream_ref->seekg(1, std::ios::cur);
    pos = istream_ref->tellg(); // to trap errors
    return *this;
}


inline RagelIstreamPtr RagelIstreamPtr::operator ++ (int)
{
    RagelIstreamPtr retval = *this;
    istream_ref->seekg(1, std::ios::cur);
    pos = istream_ref->tellg(); // to trap errors
    return retval;
}


inline RagelIstreamPtr& RagelIstreamPtr::operator -- (void)
{
    istream_ref->seekg(-1, std::ios::cur);
    pos = istream_ref->tellg(); // to trap errors
    return *this;
}


inline RagelIstreamPtr RagelIstreamPtr::operator -- (int)
{
    RagelIstreamPtr retval = *this;
    istream_ref->seekg(-1, std::ios::cur);
    pos = istream_ref->tellg(); // to trap errors
    return retval;
}


inline RagelIstreamPtr& RagelIstreamPtr::operator += (int n)
{
    istream_ref->seekg((std::streampos) n, std::ios::cur);
    pos = istream_ref->tellg(); // to trap errors
    return *this;
}


inline RagelIstreamPtr& RagelIstreamPtr::operator -= (int n)
{
    istream_ref->seekg((std::streampos) (-n), std::ios::cur);
    pos = istream_ref->tellg(); // to trap errors
    return *this;
}


inline char RagelIstreamPtr::operator * (void)
{
    return istream_ref->peek();
}


#endif // __RAGELISTREAMPTR_H__
