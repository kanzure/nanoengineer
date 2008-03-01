#include "NXOpenGLCamera.h"
#include "NXOpenGLCamera_sm.h"

using namespace statemap;

// Static class declarations.
Trackball_Initial Trackball::Initial("Trackball::Initial", 0);
Trackball_Rotating Trackball::Rotating("Trackball::Rotating", 1);
Trackball_Translating Trackball::Translating("Trackball::Translating", 2);

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

void NXOpenGLCameraState::translateStartEvent(NXOpenGLCameraContext& context, int x, int y)
{
    Default(context);
    return;
}

void NXOpenGLCameraState::translateStopEvent(NXOpenGLCameraContext& context, int x, int y)
{
    Default(context);
    return;
}

void NXOpenGLCameraState::translatingEvent(NXOpenGLCameraContext& context, int x, int y)
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

void Trackball_Initial::translateStartEvent(NXOpenGLCameraContext& context, int x, int y)
{
    NXOpenGLCamera& ctxt(context.getOwner());

    (context.getState()).Exit(context);
    context.clearState();
    try
    {
        ctxt.translateStart(x, y);
        context.setState(Trackball::Translating);
    }
    catch (...)
    {
        context.setState(Trackball::Translating);
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

void Trackball_Translating::Default(NXOpenGLCameraContext& context)
{


    return;
}

void Trackball_Translating::translateStopEvent(NXOpenGLCameraContext& context, int x, int y)
{
    NXOpenGLCamera& ctxt(context.getOwner());

    (context.getState()).Exit(context);
    context.clearState();
    try
    {
        ctxt.translateStop(x, y);
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

void Trackball_Translating::translatingEvent(NXOpenGLCameraContext& context, int x, int y)
{
    NXOpenGLCamera& ctxt(context.getOwner());

    NXOpenGLCameraState& EndStateName = context.getState();

    context.clearState();
    try
    {
        ctxt.translate(x, y);
        context.setState(EndStateName);
    }
    catch (...)
    {
        context.setState(EndStateName);
        throw;
    }

    return;
}
