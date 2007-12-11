// Copyright 2007 Nanorex, Inc.  See LICENSE file for details.


#include <QApplication>
#include "nv1.h"

int main(int argc, char *argv[])
{
      Q_INIT_RESOURCE(application);
      QApplication app(argc, argv);
      nv1 * mw = new nv1();
      mw->show();
      return app.exec();
}

