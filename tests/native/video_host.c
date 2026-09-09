/* GPL-3.0-or-later. Exercises the SAME cross-process window bridge as UxPlay. */
#include <gst/gst.h>
#include <gst/app/gstappsrc.h>
#include <stdio.h>
#include <string.h>
#include "airlinker_window.h"

int main(void) {
    gst_init(NULL, NULL);
    setvbuf(stdout, NULL, _IONBF, 0);
    GstElement *pipeline = gst_parse_launch(
        "appsrc name=source is-live=true format=time caps=video/x-raw,format=RGB,width=320,height=240,framerate=30/1 "
        "! queue ! videoconvert ! videoscale ! d3d11videosink sync=false", NULL);
    if (!pipeline || !airlinker_window_attach(pipeline)) return 2;
    GstElement *source = gst_bin_get_by_name(GST_BIN(pipeline), "source");
    gst_element_set_state(pipeline, GST_STATE_PAUSED);
    puts("AIRLINKER/1 READY");
    char command[32];
    while (fgets(command, sizeof(command), stdin)) {
        if (!strncmp(command, "quit", 4)) break;
        if (!strncmp(command, "stop", 4)) {
            gst_element_set_state(pipeline, GST_STATE_NULL);
            puts("AIRLINKER/1 IDLE");
            continue;
        }
        gst_element_set_state(pipeline, GST_STATE_PLAYING);
        GstBuffer *buffer = gst_buffer_new_allocate(NULL, 320 * 240 * 3, NULL);
        GstMapInfo map;
        gst_buffer_map(buffer, &map, GST_MAP_WRITE);
        for (int i = 0; i < 320 * 240; i++) {
            map.data[i * 3] = command[0] == 'r' ? 255 : 0;
            map.data[i * 3 + 1] = command[0] == 'g' ? 255 : 0;
            map.data[i * 3 + 2] = 0;
        }
        gst_buffer_unmap(buffer, &map);
        gst_app_src_push_buffer(GST_APP_SRC(source), buffer);
    }
    gst_element_set_state(pipeline, GST_STATE_NULL);
    GstBus *bus = gst_element_get_bus(pipeline);
    gst_bus_set_sync_handler(bus, NULL, NULL, NULL);
    gst_object_unref(bus);
    gst_object_unref(source);
    gst_object_unref(pipeline);
    return 0;
}
