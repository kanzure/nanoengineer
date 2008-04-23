#include "NXOpenGLCamera.h"
#include "NXOpenGLCamera_sm.h"

using namespace statemap;

// Static class declarations.
Trackball_Initial Trackball::Initial("Trackball::Initial", 0);
Trackball_Rotating Trackball::Rotating("Trackball::Rotating", 1);
Trackball_Panning Trackball::Panning("Trackball::Panning", 2);

void NXOpenGLCameraState::panEvent(NXOpenGLCameraContext& context, int x, int y)
{
    Default(context);
    return;
}

void NXOpenGLCameraState::panStartEvent(NXOpenGLCameraContext& context, int x, int y)
{
    Default(context);
    return;
}

void NXOpenGLCameraState::panStopEvent(NXOpenGLCameraContext& context, int x, int y)
{
    Default(context);
    return;
}

void NXOpenGLCameraState::rotateStartEvent(NXOpenGLCameraContext& context, int x, int y)
{
    Default(context);
    return;
}

void NXOpenGLCameraState::rotateStopEvent(NXOpenGLCameraContext& context, int x, int y)
{
    Default(context);
    return;
}

void NXOpenGLCameraState::rotatingEvent(NXOpenGLCameraContext& context, int x, int y)
{
    Default(context);
    return;
}

void NXOpenGLCameraState::Default(NXOpenGLCameraContext& context)
{
    throw (
        TransitionUndefinedException(
            context.getState().getName(),
            context.getTransition()));

    return;
}

void Trackball_Initial::Default(NXOpenGLCameraContext& context)
{


    return;
}

void Trackball_Initial::panStartEvent(NXOpenGLCameraContext& context, int x, int y)
{
    NXOpenGLCamera& ctxt(context.getOwner());

    (context.getState()).Exit(context);
    context.clearState();
    try
    {
        ctxt.panStart(x, y);
        context.setState(Trackball::Panning);
    }
    catch (...)
    {
        context.setState(Trackball::Panning);
        throw;
    }
    (context.getState()).Entry(context);

    return;
}

void Trackball_Initial::rotateStartEvent(NXOpenGLCameraContext& context, int x, int y)
{
    NXOpenGLCamera& ctxt(context.getOwner());

    (context.getState()).Exit(context);
    context.clearState();
    try
    {
        ctxt.rotateStart(x, y);
        context.setState(Trackball::Rotating);
    }
    catch (...)
    {
        context.setState(Trackball::Rotating);
        throw;
    }
    (context.getState()).Entry(context);

    return;
}

void Trackball_Rotating::Default(NXOpenGLCameraContext& context)
{


    return;
}

void Trackball_Rotating::rotateStopEvent(NXOpenGLCameraContext& context, int x, int y)
{
    NXOpenGLCamera& ctxt(context.getOwner());

    (context.getState()).Exit(context);
    context.clearState();
    try
    {
        ctxt.rotateStop(x, y);
        context.setState(Trackball::Initial);
    }
    catch (...)
    {
        context.setState(Trackball::Initial);
        throw;
    }
    (context.getState()).Entry(context);

    return;
}

void Trackball_Rotating::rotatingEvent(NXOpenGLCameraContext& context, int x, int y)
{
    NXOpenGLCamera& ctxt(context.getOwner());

    NXOpenGLCameraState& EndStateName = context.getState();

    context.clearState();
    try
    {
        ctxt.rotate(x, y);
        context.setState(EndStateName);
    }
    catch (...)
    {
        context.setState(EndStateName);
        throw;
    }

    return;
}

void Trackball_Panning::Default(NXOpenGLCameraContext& context)
{


    return;
}

void Trackball_Panning::panEvent(NXOpenGLCameraContext& context, int x, int y)
{
    NXOpenGLCamera& ctxt(context.getOwner());

    NXOpenGLCameraState& EndStateName = context.getState();

    context.clearState();
    try
    {
        ctxt.pan(x, y);
        context.setState(EndStateName);
    }
    catch (...)
    {
        context.setState(EndStateName);
        throw;
    }

    return;
}

void Trackball_Panning::panStopEvent(NXOpenGLCameraContext& context, int x, int y)
{
    NXOpenGLCamera& ctxt(context.getOwner());

    (context.getState()).Exit(context);
    context.clearState();
    try
    {
        ctxt.panStop(x, y);
        context.setState(Trackball::Initial);
    }
    catch (...)
    {
        context.setState(Trackball::Initial);
        throw;
    }
    (context.getState()).Entry(context);

    return;
}
