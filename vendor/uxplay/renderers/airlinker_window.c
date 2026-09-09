/* AirLinker modifications, GPL-3.0-or-later. */
#include "airlinker_window.h"
#ifdef _WIN32
#include <windows.h>
#include <gst/video/videooverlay.h>
#include <stdio.h>

#define WM_AIRLINKER_VISIBLE (WM_APP + 101)
typedef struct {
    HWND parent, window;
    HANDLE initialized, thread;
    GstElement *pipeline; /* borrowed; sync handler is removed before destruction */
    gint streaming;
    GstElement *sink;
    gulong present_handler;
} AirLinkerWindow;

static void resize_window(AirLinkerWindow *host) {
    RECT parent, child;
    if (!GetClientRect(host->parent, &parent)) return;
    GetClientRect(host->window, &child);
    if (parent.right != child.right || parent.bottom != child.bottom)
        SetWindowPos(host->window, NULL, 0, 0, parent.right, parent.bottom,
                     SWP_NOACTIVATE | SWP_NOZORDER);
}

static LRESULT CALLBACK window_proc(HWND window, UINT message, WPARAM w, LPARAM l) {
    AirLinkerWindow *host = (AirLinkerWindow *) GetWindowLongPtrW(window, GWLP_USERDATA);
    if (message == WM_NCCREATE) {
        host = ((CREATESTRUCTW *) l)->lpCreateParams;
        host->window = window;
        SetWindowLongPtrW(window, GWLP_USERDATA, (LONG_PTR) host);
    }
    if (host) {
        switch (message) {
        case WM_TIMER:
            if (!IsWindow(host->parent)) DestroyWindow(window);
            else resize_window(host);
            return 0;
        case WM_AIRLINKER_VISIBLE:
            resize_window(host);
            ShowWindow(window, w ? SW_SHOWNOACTIVATE : SW_HIDE);
            return 0;
        case WM_ERASEBKGND:
            return 1; /* the sink owns painting */
        case WM_DESTROY:
            PostQuitMessage(0);
            return 0;
        }
    }
    return DefWindowProcW(window, message, w, l);
}

static DWORD WINAPI window_thread(void *data) {
    AirLinkerWindow *host = data;
    /* Match Qt's per-monitor native coordinates, including mixed-DPI displays. */
    SetThreadDpiAwarenessContext(DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2);
    WNDCLASSW klass = {0};
    klass.lpfnWndProc = window_proc;
    klass.hInstance = GetModuleHandleW(NULL);
    klass.lpszClassName = L"AirLinkerVideoHost";
    RegisterClassW(&klass); /* multiple renderers share this class */
    CreateWindowExW(WS_EX_NOACTIVATE, klass.lpszClassName, L"", 
                    WS_CHILD | WS_CLIPCHILDREN | WS_CLIPSIBLINGS,
                    0, 0, 1, 1, host->parent, NULL, klass.hInstance, host);
    if (host->window) {
        resize_window(host);
        SetTimer(host->window, 1, 50, NULL);
    }
    SetEvent(host->initialized);
    if (!host->window) return 1;
    MSG message;
    while (GetMessageW(&message, NULL, 0, 0) > 0) {
        TranslateMessage(&message);
        DispatchMessageW(&message);
    }
    return 0;
}

static void free_window(gpointer data) {
    AirLinkerWindow *host = data;
    if (host->sink) {
        g_signal_handler_disconnect(host->sink, host->present_handler);
        gst_object_unref(host->sink);
    }
    if (host->window) PostMessageW(host->window, WM_CLOSE, 0, 0);
    if (host->thread) {
        WaitForSingleObject(host->thread, INFINITE);
        CloseHandle(host->thread);
    }
    CloseHandle(host->initialized);
    g_free(host);
}

static void frame_present(GstElement *sink, GstObject *device, gpointer target, gpointer data) {
    AirLinkerWindow *host = data;
    /* The sink has rendered a decoded frame into its swapchain backbuffer.
     * Do not call synchronous window APIs while GStreamer's device lock is held. */
    if (g_atomic_int_compare_and_exchange(&host->streaming, 0, 1)) {
        PostMessageW(host->window, WM_AIRLINKER_VISIBLE, 1, 0);
        fprintf(stdout, "AIRLINKER/1 STREAMING\n");
        fflush(stdout);
    }
}

static GstBusSyncReply overlay_message(GstBus *bus, GstMessage *message, gpointer data) {
    AirLinkerWindow *host = data;
    if (gst_is_video_overlay_prepare_window_handle_message(message)) {
        /* d3d11videosink subclasses this HWND. It MUST belong to this process,
         * even though its parent belongs to the Qt application. */
        GstElement *sink = GST_ELEMENT(GST_MESSAGE_SRC(message));
        if (!host->sink) {
            host->sink = gst_object_ref(sink);
            host->present_handler = g_signal_connect(sink, "present", G_CALLBACK(frame_present), host);
            g_object_set(sink, "emit-present", TRUE, NULL);
        }
        gst_video_overlay_set_window_handle(GST_VIDEO_OVERLAY(GST_MESSAGE_SRC(message)),
                                            (guintptr) host->window);
        gst_message_unref(message);
        return GST_BUS_DROP;
    }
    if (GST_MESSAGE_SRC(message) == GST_OBJECT(host->pipeline)) {
        if (GST_MESSAGE_TYPE(message) == GST_MESSAGE_STATE_CHANGED) {
            GstState old_state, new_state, pending;
            gst_message_parse_state_changed(message, &old_state, &new_state, &pending);
            if (new_state <= GST_STATE_READY) {
                g_atomic_int_set(&host->streaming, 0);
                PostMessageW(host->window, WM_AIRLINKER_VISIBLE, 0, 0);
            }
        }
    }
    return GST_BUS_PASS;
}

gboolean airlinker_window_attach(GstElement *pipeline) {
    const gchar *value = g_getenv("AIRLINKER_WINDOW_HANDLE");
    if (!value || !*value) return TRUE;
    gchar *end = NULL;
    guint64 handle = g_ascii_strtoull(value, &end, 10);
    if (!handle || !end || *end || !IsWindow((HWND) (guintptr) handle)) return FALSE;
    AirLinkerWindow *host = g_new0(AirLinkerWindow, 1);
    host->parent = (HWND) (guintptr) handle;
    host->pipeline = pipeline;
    host->initialized = CreateEventW(NULL, TRUE, FALSE, NULL);
    if (!host->initialized) { g_free(host); return FALSE; }
    host->thread = CreateThread(NULL, 0, window_thread, host, 0, NULL);
    if (!host->thread) { free_window(host); return FALSE; }
    WaitForSingleObject(host->initialized, INFINITE);
    if (!host->window) { free_window(host); return FALSE; }
    GstBus *bus = gst_element_get_bus(pipeline);
    gst_bus_set_sync_handler(bus, overlay_message, host, free_window);
    gst_object_unref(bus);
    return TRUE;
}
#else
gboolean airlinker_window_attach(GstElement *pipeline) { return TRUE; }
#endif
