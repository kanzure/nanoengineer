#ifndef _H_NXOPENGLCAMERA_SM
#define _H_NXOPENGLCAMERA_SM

#define SMC_USES_IOSTREAMS

#include "statemap.h"

// Forward declarations.
class Trackball;
class Trackball_Initial;
class Trackball_Rotating;
class Trackball_Panning;
class Trackball_Default;
class NXOpenGLCameraState;
class NXOpenGLCameraContext;
class NXOpenGLCamera;

class NXOpenGLCameraState :
    public statemap::State
{
public:

    NXOpenGLCameraState(const char *name, int stateId)
    : statemap::State(name, stateId)
    {};

    virtual void Entry(NXOpenGLCameraContext&) {};
    virtual void Exit(NXOpenGLCameraContext&) {};

    virtual void panEvent(NXOpenGLCameraContext& context, int x, int y);
    virtual void panStartEvent(NXOpenGLCameraContext& context, int x, int y);
    virtual void panStopEvent(NXOpenGLCameraContext& context, int x, int y);
    virtual void rotateStartEvent(NXOpenGLCameraContext& context, int x, int y);
    virtual void rotateStopEvent(NXOpenGLCameraContext& context, int x, int y);
    virtual void rotatingEvent(NXOpenGLCameraContext& context, int x, int y);

protected:

    virtual void Default(NXOpenGLCameraContext& context);
};

class Trackball
{
public:

    static Trackball_Initial Initial;
    static Trackball_Rotating Rotating;
    static Trackball_Panning Panning;
};

class Trackball_Default :
    public NXOpenGLCameraState
{
public:

    Trackball_Default(const char *name, int stateId)
    : NXOpenGLCameraState(name, stateId)
    {};

};

class Trackball_Initial :
    public Trackball_Default
{
public:
    Trackball_Initial(const char *name, int stateId)
    : Trackball_Default(name, stateId)
    {};

    void Default(NXOpenGLCameraContext& context);
    void panStartEvent(NXOpenGLCameraContext& context, int x, int y);
    void rotateStartEvent(NXOpenGLCameraContext& context, int x, int y);
};

class Trackball_Rotating :
    public Trackball_Default
{
public:
    Trackball_Rotating(const char *name, int stateId)
    : Trackball_Default(name, stateId)
    {};

    void Default(NXOpenGLCameraContext& context);
    void rotateStopEvent(NXOpenGLCameraContext& context, int x, int y);
    void rotatingEvent(NXOpenGLCameraContext& context, int x, int y);
};

class Trackball_Panning :
    public Trackball_Default
{
public:
    Trackball_Panning(const char *name, int stateId)
    : Trackball_Default(name, stateId)
    {};

    void Default(NXOpenGLCameraContext& context);
    void panEvent(NXOpenGLCameraContext& context, int x, int y);
    void panStopEvent(NXOpenGLCameraContext& context, int x, int y);
};

class NXOpenGLCameraContext :
    public statemap::FSMContext
{
public:

    NXOpenGLCameraContext(NXOpenGLCamera& owner)
    : _owner(owner)
    {
        setState(Trackball::Initial);
        Trackball::Initial.Entry(*this);
    };

    NXOpenGLCamera& getOwner() const
    {
        return (_owner);
    };

    NXOpenGLCameraState& getState() const
    {
        if (_state == NULL)
        {
            throw statemap::StateUndefinedException();
        }

        return (dynamic_cast<NXOpenGLCameraState&>(*_state));
    };

    void panEvent(int x, int y)
    {
        (getState()).panEvent(*this, x, y);
    };

    void panStartEvent(int x, int y)
    {
        (getState()).panStartEvent(*this, x, y);
    };

    void panStopEvent(int x, int y)
    {
        (getState()).panStopEvent(*this, x, y);
    };

    void rotateStartEvent(int x, int y)
    {
        (getState()).rotateStartEvent(*this, x, y);
    };

    void rotateStopEvent(int x, int y)
    {
        (getState()).rotateStopEvent(*this, x, y);
    };

    void rotatingEvent(int x, int y)
    {
        (getState()).rotatingEvent(*this, x, y);
    };

private:

    NXOpenGLCamera& _owner;
};

#endif // _H_NXOPENGLCAMERA_SM
