// Copyright 2007 Nanorex, Inc.  See LICENSE file for details.

#include "TrajectoryGraphicsWindow.h"
#include <cassert>

double const TrajectoryGraphicsWindow::BASE_FPS = 5.0;

	
/* CONSTRUCTOR */
TrajectoryGraphicsWindow::
TrajectoryGraphicsWindow(QWidget *parent,
                         NXEntityManager *entityMgr,
                         NXGraphicsManager *graphicsMgr)
: DataWindow(parent),
Ui::TrajectoryGraphicsWindow(),
// playbackContext(*this),
entityManager(entityMgr),
graphicsManager(graphicsMgr),
frameSetId(-1),
renderingEngine(NULL),
repetitionButtonGroup(NULL),
frameAdvanceButtonGroup(NULL),
repetitionMode(NO_REPETITION),
frameAdvanceMode(AUTO_FRAME_ADVANCE),
autoPlayTimer(NULL),
playing(false),
reversed(false),
beginFrameIndex(0),
currentFrameIndex(0),
endFrameIndex(0),
numFrames(0)
{
	setupUi(this);
	setupButtonGroups();
	setSpinBoxValues(0, 0, 0, 0, 0, 0, 0);
    // initialize timer
	autoPlayTimer = new QTimer;
	int currentPlaybackSpeed = playbackSpeedSpinBox->value();
	on_playbackSpeedSpinBox_valueChanged(currentPlaybackSpeed);
	
    // initialize rendering engine and scenegraph array
	bool engineCreated = createRenderingEngine();
	
	/// @todo set busy cursor
	// bool animationCreated = false;
	// if(engineCreated)
	// 	animationCreated = createAnimation();
	/// @todo unset busy cursor
	
	/// @todo trap errors	
	/// @todo anything else?
	
	connectSignalsAndSlots();
}


/// Create an instance of the user-selected rendering-engine (info in graphicsManager)
/// and initialize it in this context. Replace glPanePlaceholderTextEdit widget
/// with it. Return true if successful
bool TrajectoryGraphicsWindow::createRenderingEngine(void)
{
	// create rendering-engine instance
	renderingEngine = graphicsManager->newGraphicsInstance(this);
	bool success = (renderingEngine != (NXRenderingEngine*) NULL);
	
	// if successful, replace placeholder widget
	if(success) {
		// first confirm placeholder widget
		QLayout *const trajectoryGraphicsLayout = layout();
		int placeholderWidgetIndex =
			trajectoryGraphicsLayout->indexOf(glPanePlaceholderTextEdit);
		assert(placeholderWidgetIndex >= 0);
		
		// then include engine and delete placeholder
		trajectoryGraphicsLayout->setEnabled(false);
		trajectoryGraphicsLayout->removeWidget(glPanePlaceholderTextEdit);
		trajectoryGraphicsLayout->removeWidget(controlsFrame);
		QWidget *renderingEngineWidget = renderingEngine->asQWidget();
		trajectoryGraphicsLayout->addWidget(renderingEngineWidget);
		trajectoryGraphicsLayout->addWidget(controlsFrame);
		// renderingEngineWidget->resize(glPanePlaceholderTextEdit->size());
		// renderingEngineWidget->move(glPanePlaceholderTextEdit->pos());
		trajectoryGraphicsLayout->setEnabled(true);

		delete glPanePlaceholderTextEdit;
		glPanePlaceholderTextEdit = (QTextEdit*) NULL;
		
		update();
		NXLOG_DEBUG("TrajectoryGraphicsWindow",
		            "Locally instantiated rendering-engine");
	}
	else {
		NXLOG_DEBUG("TrajectoryGraphicsWindow",
		            "Failed to locally instantiate rendering-engine");
	}
	return success;
}


bool TrajectoryGraphicsWindow::createAnimation(void)
{
	cerr << "In TrajectoryGraphicsWindow::createAnimation()" << endl;
	assert(entityManager != NULL);
	assert(graphicsManager != NULL);
	assert(frameSetId >= 0);
	
	// create scenegraphs for each frame
	numFrames = entityManager->getFrameCount(frameSetId);
	bool success = true;
	
	renderingEngine->clearFrames();
	
	int frameId = 0;
	for(frameId = 0; (frameId < numFrames) && success; ++frameId) {
		// extract and render molecule-set for frame
		NXMoleculeSet *const molSetPtr_frameId =
			entityManager->getRootMoleculeSet(frameSetId, frameId);
		assert(molSetPtr_frameId != (NXMoleculeSet*) NULL);
		NXCommandResult const *const cmdResult =
			renderingEngine->addFrame(molSetPtr_frameId);
		
		// diagnostic messages
		ostringstream msg;
		
		if(cmdResult->getResult() != (int) NX_CMD_SUCCESS) {
			msg << "Animation creation failed - ";
			vector<QString> const& addFrameMsgs = cmdResult->getParamVector();
			for(int n = 0; n < (int)addFrameMsgs.size(); ++n)
				msg << qPrintable(addFrameMsgs[n]);
			NXLOG_SEVERE("TrajectoryGraphicsWindow", msg.str());
			success = false;
			break;
		}
		else {
			msg << "Created frame " << (frameId+1) << " of " << numFrames;
			NXLOG_INFO("TrajectoryGraphicsWindow", msg.str());
		}
	}
	
		// Update UI elements with frame-count info
	numFrames = frameId; // last frame created if there was failure
	if(numFrames > 0) {
		setCurrentFrameIndex(1);
		renderingEngine->resetView();
		setSpinBoxValues(1, 1, numFrames, 1, 1, numFrames, numFrames);
		// renderingEngine->asQWidget()->update();
		update();
	}
	
	return success;
}


/* DESTRUCTOR */
TrajectoryGraphicsWindow::~TrajectoryGraphicsWindow()
{
	// delete owned engine instance which will in-turn delete owned plugin instances
	if(renderingEngine != (NXRenderingEngine*) NULL)
		delete renderingEngine;
}


void TrajectoryGraphicsWindow::setupButtonGroups(void)
{
	repetitionButtonGroup = new QButtonGroup(this);
	repetitionButtonGroup->setExclusive(true);
	repetitionButtonGroup->addButton(noneRepetitionRadioButton,
	                                 (int) NO_REPETITION);
	repetitionButtonGroup->addButton(loopRepetitionRadioButton,
	                                 (int) LOOP_REPETITION);
	repetitionButtonGroup->addButton(oscillateRepetitionRadioButton,
	                                 (int) OSCILLATE_REPETITION);
	
	frameAdvanceButtonGroup = new QButtonGroup(this);
	frameAdvanceButtonGroup->setExclusive(true);
	frameAdvanceButtonGroup->addButton(autoFrameAdvanceRadioButton,
	                                   (int) AUTO_FRAME_ADVANCE);
	frameAdvanceButtonGroup->addButton(manualFrameAdvanceRadioButton,
	                                   (int) MANUAL_FRAME_ADVANCE);
}


void TrajectoryGraphicsWindow::setMaxFrameNumber(int maxFrameNumber)
{
	QString numFramesString;
	numFramesString.setNum(maxFrameNumber);
	numFramesLineEdit->setText(numFramesString);
	endFrameSpinBox->setMaximum(maxFrameNumber);
}


void TrajectoryGraphicsWindow::setSpinBoxValues(int beginMin, int beginVal,
                                                int beginMax, int current,
                                                int endMin, int endVal, int endMax)
{
	cerr << "setSpinBoxValues: "
		<< beginMin << ", " << beginVal << ", " << beginMax << ", " << current
		<< ", " << endMin << ", " << endVal << ", " << endMax << endl;
	beginFrameSpinBox->setRange(beginMin, beginMax);
	beginFrameSpinBox->setValue(beginVal);
	currentFrameSpinBox->setRange(beginVal, endVal);
	currentFrameHSlider->setRange(beginVal, endVal);
	currentFrameSpinBox->setValue(current); // will also set slider
	endFrameSpinBox->setMinimum(endMin);
	setMaxFrameNumber(endMax); // will set endFrameSpinBox->maximum
	endFrameSpinBox->setValue(endVal);
	// update();
}


void TrajectoryGraphicsWindow::connectSignalsAndSlots(void)
{
	// automatically change playback buttons based on frame-advance mode
	QObject::connect(frameAdvanceButtonGroup, SIGNAL(buttonClicked(int)),
	                 playbackSizingStackedWidget, SLOT(setCurrentIndex(int)));
	
	// auto-play
	QObject::connect(autoPlayTimer, SIGNAL(timeout()),
	                 this, SLOT(autoPlayFrameAdvance()));
	
	QObject::connect(this, SIGNAL(beginFrameReached(void)),
	                 this, SLOT(onBeginFrameReached(void)));
	
	QObject::connect(this, SIGNAL(endFrameReached(void)),
	                 this, SLOT(onEndFrameReached(void)));
	
	QObject::connect(frameAdvanceButtonGroup, SIGNAL(buttonClicked(int)),
	                 this, SLOT(onFrameAdvanceButtonGroupButtonClicked(int)));
	
	QObject::connect(repetitionButtonGroup, SIGNAL(buttonClicked(int)),
	                 this, SLOT(onRepetitionButtonGroupButtonClicked(int)));
}



/* FUNCTION: newFrame */
void TrajectoryGraphicsWindow::newFrame(int frameSetId, int newFrameIndex,
                                        NXMoleculeSet* newMoleculeSet)
{
	cerr << "In TrajectoryGraphicsWindow::newFrame(), numFrames = " << numFrames << endl;
#if 0
	// Start printing all frames available from the first render() call
	unsigned int frameCount = entityManager->getFrameCount(frameSetId);;
	QString line;
	int frameIndex = numFrames;
	NXMoleculeSet* moleculeSet =
		entityManager->getRootMoleculeSet(frameSetId, frameIndex);
	while (moleculeSet != 0) {
		glPanePlaceholderTextEdit->insertPlainText("\n==========================\n");
		line =
			QString("storeComplete=%1 ").arg(entityManager->getDataStoreInfo()->storeIsComplete(frameSetId));
		glPanePlaceholderTextEdit->insertPlainText(line);
		line =
			QString("frame: %1%2/%3\n")
			.arg(frameIndex)
			.arg(moleculeSet == newMoleculeSet ? "*" : "")
			.arg(frameCount);
		glPanePlaceholderTextEdit->insertPlainText(line);
		
		++frameIndex;
		moleculeSet =
			entityManager->getRootMoleculeSet(frameSetId, frameIndex);
	}
#endif
	// bool const firstFrames = (numFrames == 0);

	// Generate frames for each molecule-sets in each new frame
	if(frameSetId == this->frameSetId && newFrameIndex > numFrames) {
		for(int frameId=numFrames+1; frameId <= newFrameIndex; ++frameId) {
			NXMoleculeSet *molSetPtr =
				entityManager->getRootMoleculeSet(frameSetId, frameId);
			renderingEngine->addFrame(molSetPtr);
			if(frameId == 1) {
				setCurrentFrameIndex(frameId);
				assert(0);
			}
		}
		
		bool const endFrameIsLast =
			endFrameSpinBox->value() == endFrameSpinBox->maximum();
		
		bool const showingLastFrame =
			(currentFrameSpinBox->value() == endFrameSpinBox->maximum());
		
		numFrames = newFrameIndex;
		setMaxFrameNumber(numFrames);
		
		// If the end-frame happens to be the last frame then user probably
		// wants to play till the end so revise that value
		if(endFrameIsLast) {
			
			endFrameSpinBox->setValue(numFrames);
			//< will emit signals to update rest of GUI
			
			// If current-frame is the last frame then user wants to update to end
			if(showingLastFrame)
				currentFrameSpinBox->setValue(numFrames);
		}
// 		if(firstFrames) {
// 			cerr << "First frames" << endl;
// 			setCurrentFrameIndex(1);
// 		}
		update();
	}
	// Stop once the data store is complete
	// if (entityManager->getDataStoreInfo()->storeIsComplete(frameSetId))
	// 	exit(0);
}


void TrajectoryGraphicsWindow::setFrameSetId(int frameSetId)
{
	this->frameSetId = frameSetId;
	createAnimation();
	on_trajectoryPlayButton_toggled(true); // autoplay
	
#if 0
	int frameCount = entityManager->getFrameCount(frameSetId);
	renderingEngine->clearFrames();
	for(int frameId=0; frameId<frameCount; ++frameId) {
		NXMoleculeSet *molSetPtr =
			entityManager->getRootMoleculeSet(frameSetId, frameId);
		renderingEngine->addFrame(molSetPtr);
	}
#endif
}


void
TrajectoryGraphicsWindow::on_beginFrameSpinBox_valueChanged(int frameIndex)
{
	beginFrameIndex = frameIndex;
	endFrameSpinBox->setMinimum(frameIndex);
	currentFrameSpinBox->setMinimum(frameIndex);
	currentFrameHSlider->setMinimum(frameIndex);
}

void
TrajectoryGraphicsWindow::on_endFrameSpinBox_valueChanged(int frameIndex)
{
	endFrameIndex = frameIndex;
	beginFrameSpinBox->setMaximum(frameIndex);
	currentFrameSpinBox->setMaximum(frameIndex);
	currentFrameHSlider->setMaximum(frameIndex);
}


void
TrajectoryGraphicsWindow::on_currentFrameSpinBox_valueChanged(int frameIndex)
{
	currentFrameIndex = frameIndex;
	
    // update scenegraph to be rendered
	if(renderingEngine != NULL) {
		renderingEngine->setCurrentFrame(currentFrameIndex-1);
		renderingEngine->asQWidget()->update();
	}

	if(playing && (frameIndex == beginFrameIndex))
		emit beginFrameReached();
	
	else if(playing && (frameIndex == endFrameIndex))
		emit endFrameReached();
	/// @todo renderingEngine->update()?
}


void TrajectoryGraphicsWindow::on_trajectoryPlusFiveButton_clicked(bool)
{
	currentFrameSpinBox->stepBy(5);
    // will emit signal to change slider's value
}


void TrajectoryGraphicsWindow::on_trajectoryMinusFiveButton_clicked(bool)
{
	currentFrameSpinBox->stepBy(-5);
    // will emit signal to change slider's value
}


/// Enables/disables the playback-speed spinbox and the oscillate-repetition 
/// radio-button in the auto-/manual- frame-advance mode. The playback
/// button-quartet swap is performed by a parallel direct signal-slot connection.
void
TrajectoryGraphicsWindow::
onFrameAdvanceButtonGroupButtonClicked(int frameAdvanceMode)
{
	this->frameAdvanceMode = static_cast<FrameAdvanceMode>(frameAdvanceMode);
    // Change of controls displayed is achieved by signal from button group
    // Enable/disable playback speed
	bool inAutoFrameAdvanceMode = (frameAdvanceMode == (int) AUTO_FRAME_ADVANCE);
	playbackSpeedSpinBox->setEnabled(inAutoFrameAdvanceMode);
	if(!inAutoFrameAdvanceMode) {
        // disable oscillate-repetition option but before doing so, transfer...
        // ...enabled state to no-repetition button
		bool oscillateRepetitionSelected = oscillateRepetitionRadioButton->isChecked();
		if(oscillateRepetitionSelected) {
			noneRepetitionRadioButton->click(); // emits signals
			assert(noneRepetitionRadioButton->isChecked());
			assert(!oscillateRepetitionRadioButton->isChecked());
		}
        oscillateRepetitionRadioButton->setEnabled(false);
	}
	else
		oscillateRepetitionRadioButton->setEnabled(true);
}


void
TrajectoryGraphicsWindow::
onRepetitionButtonGroupButtonClicked(int repetitionMode)
{
	this->repetitionMode = (RepetitionMode) repetitionMode;
	currentFrameSpinBox->setWrapping(repetitionMode == LOOP_REPETITION);
}


void TrajectoryGraphicsWindow::on_trajectoryFirstButton_clicked(bool)
{
	int beginFrameIndex = currentFrameSpinBox->minimum();
	currentFrameSpinBox->setValue(beginFrameIndex);
    // will emit signal to update other parts of GUI
}


void TrajectoryGraphicsWindow::on_trajectoryLastButton_clicked(bool)
{
	int endFrameIndex = currentFrameSpinBox->maximum();
	currentFrameSpinBox->setValue(endFrameIndex);
    // will emit signal to update other parts of GUI
}


void TrajectoryGraphicsWindow::on_playbackSpeedSpinBox_valueChanged(int newSpeed)
{
	double scale = double(newSpeed)/100.0;
	int newTimerInterval = int(1.0 / (scale*BASE_FPS) * 1000); // in msec
	autoPlayTimer->setInterval(newTimerInterval);
}


void TrajectoryGraphicsWindow::on_trajectoryPlayButton_toggled(bool checked)
{
	if(checked) { // user pressed play
		// cerr << "Play button pressed" << endl;
		disablePlayButton();
		reversed = false;
		if(playing) {
			enablePlayReverseButton();
			releasePlayReverseButton();
		}
		else {
			playing = true;
			autoPlayTimer->start();
		}
	}
}


void TrajectoryGraphicsWindow::on_trajectoryPlayRevButton_toggled(bool checked)
{
	if(checked) { // user pressed play-reverse
		// cerr << "Play-reverse button pressed" << endl;
		disablePlayReverseButton();
		reversed = true;
		if(playing) {
			enablePlayButton();
			releasePlayButton();
		}
		else {
			playing = true;
			autoPlayTimer->start();
		}
	}
}


void TrajectoryGraphicsWindow::on_trajectoryStopButton_clicked(bool)
{
	if(playing) {
		// release all play buttons because we don't know which one
		// started the motion because we have oscillate mode which reverses dir
		enablePlayReverseButton();
		releasePlayReverseButton();
		enablePlayButton();
		releasePlayButton();
		autoPlayTimer->stop();
		playing = false;
	}
}


// slot called by autoPlayTimer->timeout()
void TrajectoryGraphicsWindow::autoPlayFrameAdvance(void)
{
	if(!playing) {
		autoPlayTimer->stop();
		assert(0);
	}
	if(reversed)
		currentFrameSpinBox->stepDown();
	else
		currentFrameSpinBox->stepUp();
}


void TrajectoryGraphicsWindow::onBeginFrameReached(void)
{
	if(frameAdvanceMode == AUTO_FRAME_ADVANCE) {
        // State reached by
        // (1) no-repetition, play-reverse
        // (2) repetition (loop or oscillate) with play or play-reverse
		switch(repetitionMode) {
		case NO_REPETITION:
            // emit signal to stop animation
			trajectoryStopButton->click();
			break;
		case LOOP_REPETITION:
			break; // no-op
		case OSCILLATE_REPETITION:
			assert(reversed);
			// reversed = false; // change direction of animation
			on_trajectoryPlayButton_toggled(true);
			break;
		}
	}
	
    // For manual-frame-advance mode, only NO_REPETITION and LOOP_REPETITION
    // are active and in both of these cases, nothing needs to be done because
    // the current-frame-index spin-box wrapping mode takes care of setting
    // the current value
}


void TrajectoryGraphicsWindow::onEndFrameReached(void)
{
	if(frameAdvanceMode == AUTO_FRAME_ADVANCE) {
        // State reached by
        // (1) no-repetition, play
        // (2) repetition (loop or oscillate) with play or play-reverse
		switch(repetitionMode) {
		case NO_REPETITION:
            // emit signal to stop animation
			trajectoryStopButton->click();
			break;
		case LOOP_REPETITION:
			break; // no-op
		case OSCILLATE_REPETITION:
			// reversed = true;
			on_trajectoryPlayRevButton_toggled(true);
			break;
		}
	}
	
    // For manual-frame-advance mode, only NO_REPETITION and LOOP_REPETITION
    // are active and in both of these cases, nothing needs to be done because
    // the current-frame-index spin-box wrapping mode takes care of setting
    // the current value
}


void TrajectoryGraphicsWindow::setCurrentFrameIndex(int frameIndex)
{
	currentFrameIndex = frameIndex;
	renderingEngine->setCurrentFrame(frameIndex-1);
	/// @todo Post-FNANO resetView() shouldn't be a part of setCurrentFrameIndex() - set lastView instead
	renderingEngine->resetView();
}
