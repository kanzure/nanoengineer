// Copyright 2007 Nanorex, Inc.  See LICENSE file for details.

#ifndef TRAJECTORYGRAPHICSWINDOW_H
#define TRAJECTORYGRAPHICSWINDOW_H

#include "Nanorex/Interface/NXEntityManager.h"
#include "Nanorex/Interface/NXGraphicsManager.h"
#include "Nanorex/Interface/NXRenderingEngine.h"
#include "Nanorex/Interface/NXSceneGraph.h"
#include "Nanorex/Interface/NXNamedView.h"
#include "DataWindow.h"

using namespace Nanorex;

#include <QWidget>
#include <QButtonGroup>
#include <ui_TrajectoryGraphicsWindow.h>

#include <vector>

// #include "TrajectoryGraphicsWindowPlayback_sm.h"


/* CLASS: TrajectoryGraphicsWindow */
class TrajectoryGraphicsWindow
: public DataWindow, private Ui::TrajectoryGraphicsWindow {
    
    // friend class TrajectoryGraphicsWindowPlaybackContext;
    
    Q_OBJECT;
    
protected:
    enum RepetitionMode {
        NO_REPETITION=0, LOOP_REPETITION=1, OSCILLATE_REPETITION=2
    };
    enum FrameAdvanceMode {AUTO_FRAME_ADVANCE=0, MANUAL_FRAME_ADVANCE=1};
    
public:
    TrajectoryGraphicsWindow(QWidget *parent,
                             NXEntityManager *entityManager,
                             NXGraphicsManager *graphicsManager);
    ~TrajectoryGraphicsWindow();
    
//     void setEntityManager(NXEntityManager* entityManager) {
//         this->entityManager = entityManager;
//     }
//     
// 	void setGraphicsManager(NXGraphicsManager* graphicsManager) {
// 		this->graphicsManager = graphicsManager;
// 		renderingEngine = graphicsManager->newGraphicsInstance(this);
// 		/// @todo move to .cpp file and initialize plugins in this context
// 	}
	
	// void setRenderingEngine(NXRenderingEngine *renderingEngine) {
	//     this->renderingEngine = renderingEngine;
	// }
    
    void setFrameSetId(int frameSetId);
	
	void setNamedView(Nanorex::NXNamedView const& view) {
		renderingEngine->setNamedView(view);
	}
	
	void resetView(void) { renderingEngine->resetView(); }
    
signals:
    void beginFrameChanged(int);
    void endFrameChanged(int);
    void currentFrameChanged(int);
    
    void beginFrameReached(void);
    void endFrameReached(void);
    
public slots:
    void newFrame(int frameSetId, int newFrameIndex,
                NXMoleculeSet* newMoleculeSet);
    
protected slots:
    // slots named as per QMetaObject's auto-connection nomenclature
    // ** Do not rename **
    // ref: Qt Designer manual, section "Using a component in your application"
    
    // widget update slots
    void on_beginFrameSpinBox_valueChanged(int);
    void on_endFrameSpinBox_valueChanged(int);
    void on_currentFrameSpinBox_valueChanged(int);
    
    void on_trajectoryPlusFiveButton_clicked(bool);
    void on_trajectoryMinusFiveButton_clicked(bool);
    
    void on_trajectoryFirstButton_clicked(bool);
    void on_trajectoryLastButton_clicked(bool);
    void on_playbackSpeedSpinBox_valueChanged(int value);
    void on_trajectoryPlayRevButton_toggled(bool checked);
	// void on_trajectoryPauseButton_toggled(bool checked);
    void on_trajectoryStopButton_clicked(bool);
    void on_trajectoryPlayButton_toggled(bool checked);
    
	// non-QMetaObject slots: note nomenclature difference
	void onFrameAdvanceButtonGroupButtonClicked(int frameAdvanceMode);
	void onRepetitionButtonGroupButtonClicked(int repetitionMode);
	
    // slots to handle repetition behavior
    void onBeginFrameReached(void);
    void onEndFrameReached(void);
    
    // slots extending functionality
    // current frame spin box and slider updates to visual
    void setCurrentFrameIndex(int frameIndex);
    
    // auto-play timer signals to update visual
    void autoPlayFrameAdvance(void);
    
protected:
	// TrajectoryGraphicsWindowPlaybackContext playbackContext;
    
	NXEntityManager* entityManager;
	NXGraphicsManager* graphicsManager;
	int frameSetId;
	///< index of frame-set in entity-manager corresponding to this trajectory
	
	NXRenderingEngine *renderingEngine;
	
	QButtonGroup *repetitionButtonGroup;
    QButtonGroup *frameAdvanceButtonGroup;
    RepetitionMode repetitionMode;
    FrameAdvanceMode frameAdvanceMode;
    QTimer *autoPlayTimer;
    
    /// Are we animating backwards at this time?
	bool playing; ///< is the animation currently playing?
	bool reversed; ///< if playing, is animation being played in reverse?
	int beginFrameIndex; ///< index of first frame in user-defined view-interval
	int currentFrameIndex; ///< index of frame currently being displayed
	int endFrameIndex; ///< index of last frame in user-defined view-interval
	int numFrames; ///< Total number of frames
    
    static double const BASE_FPS;

    void enablePlayButton(void) { trajectoryPlayButton->setEnabled(true); }
    void disablePlayButton(void) { trajectoryPlayButton->setEnabled(false); }
    void enablePlayReverseButton(void) { trajectoryPlayRevButton->setEnabled(true); }
    void disablePlayReverseButton(void) { trajectoryPlayRevButton->setEnabled(false); }
    void releasePlayButton(void) { trajectoryPlayButton->setChecked(false); }
    void pressPlayReverseButton(void) { trajectoryPlayButton->setChecked(true); }
    void releasePlayReverseButton(void) { trajectoryPlayRevButton->setChecked(false); }
	// void releasePauseButton(void) { trajectoryPauseButton->setChecked(false); }
    void pausePlay(void) { autoPlayTimer->stop(); }
    void pausePlayReverse(void) { autoPlayTimer->stop(); }
    
    void setSpinBoxValues(int beginMin, int beginVal, int beginMax,
                        int current, int endMin, int endVal, int endMax);
	void setMaxFrameNumber(int maxFrameNumber);
	
private:
    void connectSignalsAndSlots(void);
	void setupButtonGroups(void);
	bool createRenderingEngine(void);
	bool createAnimation(void);
};

#endif
