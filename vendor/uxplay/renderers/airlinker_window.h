/* AirLinker modifications, GPL-3.0-or-later. */
#ifndef AIRLINKER_WINDOW_H
#define AIRLINKER_WINDOW_H
#include <gst/gst.h>
/* Installs an engine-owned overlay window when AIRLINKER_WINDOW_HANDLE is set.
 * The pipeline must reach NULL before removing its bus sync handler. */
gboolean airlinker_window_attach(GstElement *pipeline);
#endif
