################################################################################
# The MIT License
#
# Copyright (c) 2019-2023, Prominence AI, Inc.
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.
################################################################################

################################################################################
#
# This example shows how to dynamically add and remove Source components
# while the Pipeline is playing. The Pipeline must have at least once source
# while playing. The Pipeline consists of:
#   - A variable number of File Sources. The Source are created/added and 
#       removed/deleted on user key-input.
#   - The Pipeline's built-in streammuxer muxes the streams into a
#       batched stream as input to the Inference Engine.
#   - Primary GST Inference Engine (PGIE).
#   - IOU Tracker.
#   - Multi-stream 2D Tiler - created with rows/cols to support max-sources.
#   - On-Screen Display (OSD)
#   - Window Sink - with window-delete and key-release event handlers.
# 
# A Source component is created and added to the Pipeline by pressing the 
#  "+" key which calls the following services:
#
#    dsl_source_uri_new(source_name, uri_h265, True, 0, 0)
#    dsl_pipeline_component_add('pipeline', source_name)
#
# A Source component (last added) is removed from the Pipeline and deleted by 
# pressing the "-" key which calls the following services
#
#    dsl_pipeline_component_remove('pipeline', source_name)
#    dsl_component_delete(source_name)
#  
################################################################################

#!/usr/bin/env python

import sys
sys.path.insert(0, "../../")
import time

from dsl import *

uri_h265 = "/opt/nvidia/deepstream/deepstream/samples/streams/sample_1080p_h265.mp4"

streammux_config_file = '../../test/config/all_sources_30fps.txt'

# Filespecs (Jetson and dGPU) for the Primary GIE
primary_infer_config_file = \
    '/opt/nvidia/deepstream/deepstream/samples/configs/deepstream-app/config_infer_primary.txt'
primary_model_engine_file = \
    '/opt/nvidia/deepstream/deepstream/samples/models/Primary_Detector/resnet10.caffemodel_b8_gpu0_int8.engine'

# Filespec for the IOU Tracker config file
iou_tracker_config_file = \
    '/opt/nvidia/deepstream/deepstream/samples/configs/deepstream-app/config_tracker_IOU.yml'

##
# Maximum number of sources that can be added to the Pipeline
##
MAX_SOURCE_COUNT = 8

##
# Current number of sources added to the Pipeline
##
cur_source_count = 0

##
# Number of rows and columns for the Multi-stream 2D Tiler
TILER_COLS = 4
TILER_ROWS = 2

## 
# Function to be called on End-of-Stream (EOS) event
## 
def eos_event_listener(client_data):
    print('Pipeline EOS event')
    dsl_pipeline_stop('pipeline')
    dsl_main_loop_quit()

## 
# Function to be called on XWindow Delete event
## 
def xwindow_delete_event_handler(client_data):
    print('delete window event')
    dsl_pipeline_stop('pipeline')
    dsl_main_loop_quit()

## 
# Function to be called on XWindow KeyRelease event
## 
def xwindow_key_event_handler(key_string, client_data):
    global MAX_SOURCE_COUNT, cur_source_count
    print('key released = ', key_string)
    if key_string.upper() == 'P':
        dsl_pipeline_pause('pipeline')
    elif key_string.upper() == 'R':
        dsl_pipeline_play('pipeline')
    elif key_string.upper() == 'Q' or key_string == '' or key_string == '':
        dsl_pipeline_stop('pipeline')
        dsl_main_loop_quit()

    # Add a new source
    elif key_string == '+': 
        if cur_source_count < MAX_SOURCE_COUNT:
            cur_source_count += 1
            source_name = 'source-' + str(cur_source_count)
            print('adding source ', source_name)
            dsl_source_uri_new(source_name, uri_h265, False, 0, 0)
            dsl_pipeline_component_add('pipeline', source_name)

    # Remove the last source added
    elif key_string == '-': 
        if cur_source_count > 1:
            source_name = 'source-' + str(cur_source_count)
            print('removing source ', source_name)
            dsl_pipeline_component_remove('pipeline', source_name)
            dsl_component_delete(source_name)
            cur_source_count -= 1
  
##  
#  Client handler for our Stream-Event Pad Probe Handler
## 
def stream_event_handler(stream_event, stream_id, client_data):
    if stream_event == DSL_PPH_EVENT_STREAM_ADDED:
        print('Stream Id =', stream_id, ' added to Pipeline')
    elif stream_event == DSL_PPH_EVENT_STREAM_ENDED:
        print('Stream Id =', stream_id, ' ended')
    elif stream_event == DSL_PPH_EVENT_STREAM_DELETED:
        print('Stream Id =', stream_id, ' deleted from Pipeline')
        
    return DSL_PAD_PROBE_OK

##  
#  Application main.
## 
def main(args):

    global MAX_SOURCE_COUNT, cur_source_count

    # Since we're not using args, we can Let DSL initialize GST on first call
    while True:

        # First new URI File Source
        retval = dsl_source_uri_new('source-1', uri_h265, False, 0, 0)
        if retval != DSL_RETURN_SUCCESS:
            break

        ## New Primary GIE using the filespecs above with interval = 0
        retval = dsl_infer_gie_primary_new('primary-gie', 
            primary_infer_config_file, primary_model_engine_file, 0)
        if retval != DSL_RETURN_SUCCESS:
            break

        # New IOU Tracker, setting operational width and hieght
        retval = dsl_tracker_new('iou-tracker', iou_tracker_config_file, 480, 272)
        if retval != DSL_RETURN_SUCCESS:
            break

        # New Tiled Display, setting width and height, 
        retval = dsl_tiler_new('tiler', 1280, 720)
        if retval != DSL_RETURN_SUCCESS:
            break

        # Set the Tiled Displays tiles to accommodate max sources.
        retval = dsl_tiler_tiles_set('tiler', columns=TILER_COLS, rows=TILER_ROWS)
        if retval != DSL_RETURN_SUCCESS:
            break

        # New OSD with text, clock and bbox display all enabled. 
        retval = dsl_osd_new('on-screen-display', 
            text_enabled=True, clock_enabled=True, 
            bbox_enabled=True, mask_enabled=False)
        if retval != DSL_RETURN_SUCCESS:
            break

        # New Window Sink, 0 x/y offsets and same dimensions as Tiled Display
        retval = dsl_sink_window_egl_new('egl-sink', 0, 0, 1280, 720)
        if retval != DSL_RETURN_SUCCESS:
            break

        # Add the XWindow event handler functions defined above to the Window Sink
        retval = dsl_sink_window_key_event_handler_add('egl-sink', 
            xwindow_key_event_handler, None)
        if retval != DSL_RETURN_SUCCESS:
            break
        retval = dsl_sink_window_delete_event_handler_add('egl-sink', 
            xwindow_delete_event_handler, None)
        if retval != DSL_RETURN_SUCCESS:
            break

        # Add all the components to a new Pipeline
        retval = dsl_pipeline_new_component_add_many('pipeline', 
            ['source-1' , 'primary-gie', 'iou-tracker', 'tiler', 
            'on-screen-display', 'egl-sink', None])
        if retval != DSL_RETURN_SUCCESS:
            break

        # Update the current source count
        cur_source_count = 1

        # Set the Pipeline's config-file
        retval = dsl_pipeline_streammux_config_file_set('pipeline',
            streammux_config_file)
        if retval != DSL_RETURN_SUCCESS:
            break

        # IMPORTANT: we need to explicitely set the stream-muxer Batch size,
        # otherwise the Pipeline will use the current number of Sources when set to 
        # Playing, which would be 1 and too small
        retval = dsl_pipeline_streammux_batch_size_set('pipeline',
            MAX_SOURCE_COUNT)
        if retval != DSL_RETURN_SUCCESS:
            break

        # Create a Stream-Event Pad Probe Handler (PPH) to manage new Streammuxer 
        # stream-events: stream-added, stream-ended, and stream-deleted.
        retval = dsl_pph_stream_event_new('stream-event-pph',
            stream_event_handler, None)
        if retval != DSL_RETURN_SUCCESS:
            break
            
        # Add the PPH to the source (output) pad of the Pipeline's Streammuxer
        retval = dsl_pipeline_streammux_pph_add('pipeline',
            'stream-event-pph')
        if retval != DSL_RETURN_SUCCESS:
            break
            
        retval = dsl_pipeline_eos_listener_add('pipeline', 
            eos_event_listener, None)
        if retval != DSL_RETURN_SUCCESS:
            break

        # Play the pipeline
        retval = dsl_pipeline_play('pipeline')
        if retval != DSL_RETURN_SUCCESS:
            break

        # Start/join the main-loop until dsl_main_loop_exit()
        dsl_main_loop_run()
        retval = DSL_RETURN_SUCCESS
        break

    # Print out the final result
    print(dsl_return_value_to_string(retval))

    dsl_pipeline_delete_all()
    dsl_component_delete_all()

if __name__ == '__main__':
    sys.exit(main(sys.argv))
