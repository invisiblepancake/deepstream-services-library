"""
The MIT License

Copyright (c) 2019-Present, Michael Patrick

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in-
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

#######################################################################################
#
#   Name:            ds_3sgie_test.py
#
#   Description:    This program takes as input a video of cars and uses one primary and
#                   three secondary inference engines to determine color make and model
#
#                   Usage: python3 ds_3sgie_test.py <video file>
#
#######################################################################################
"""
import sys
sys.path.insert(0,"../../")
import os
import pyds
from dsl import *

DSL_RESULT_SUCCESS = 0

# Filespecs for the Primary GIE
inferConfigFile = '../../test/configs/config_infer_primary_nano.txt'
modelEngineFile = '../../test/models/Primary_Detector_Nano/resnet10.caffemodel_b1_fp16.engine'

# Filespecs for the Secondary GIE
sgie_config_file = '../../test/configs/config_infer_secondary_carcolor_nano.txt'
sgie_model_file = '../../test/models/Secondary_CarColor/resnet18.caffemodel_b16_fp16.engine'

# Filespecs for the Secondary GIE
sgie2_config_file = '../../test/configs/config_infer_secondary_carmake_nano.txt'
sgie2_model_file = '../../test/models/Secondary_CarMake/resnet18.caffemodel_b16_fp16.engine'

# Filespecs for the Secondary GIE
sgie3_config_file = '../../test/configs/config_infer_secondary_vehicletypes_nano.txt'
sgie3_model_file = '../../test/models/Secondary_VehicleTypes/resnet18.caffemodel_b16_fp16.engine'

def osd_batch_meta_handler_cb(buffer, user_data):

    batch_meta = pyds.gst_buffer_get_nvds_batch_meta(buffer)
    l_frame = batch_meta.frame_meta_list
    while l_frame is not None:
        try:
            frame_meta = pyds.glist_get_nvds_frame_meta(l_frame.data)
        except StopIteration:
            break    

#        '''
        print("Frame Number is ", frame_meta.frame_num)
        print("Source id is ", frame_meta.source_id)
        print("Batch id is ", frame_meta.batch_id)
        print("Source Frame Width ", frame_meta.source_frame_width)
        print("Source Frame Height ", frame_meta.source_frame_height)
        print("Num object meta ", frame_meta.num_obj_meta)
 #       '''

        try:
            l_frame=l_frame.next
        except StopIteration:
            break
    return True

####################################################
#   This callback handles EOS messages
####################################################

def eos_listener(client_data):
    global eos_count
    if eos_count == 0:
        print("EOS Callback primed")
        eos_count = 1
    else :
        print("EOS shutdown received")
        eos_count = 0
        dsl_main_loop_quit()

####################################################
# Function to be called on XWindow ButtonPress event
####################################################
def xwindow_button_event_handler(xpos, ypos, client_data):
    print('button pressed: xpos = ', xpos, ', ypos = ', ypos)

# Function to be called on XWindow KeyRelease event
def xwindow_key_event_handler(key_string, client_data):
    print('key released = ', key_string)
    if key_string.upper() == 'P':
        dsl_pipeline_pause('pipeline1')
    elif key_string.upper() == 'R':
        dsl_pipeline_play('pipeline1')
    elif key_string.upper() == 'Q':
        dsl_main_loop_quit()


#####################################################
#
#   Function: test1()
#
#   Description:  This test creates a pipeline, adds
#   a video file as a URI and a sink.  It then plays
#   the video and when it ends, it tears down the
#   pipeline
#
#####################################################

def test1():
    """Execute test """
    uri = os.path.abspath(sys.argv[1])

    #########################################
    #   Create source
    #########################################

    retVal = dsl_source_uri_new("video1", uri, False, 0, 0, 0)
    
    if retVal != DSL_RETURN_SUCCESS:
        print(retVal)

    # New Primary GIE using the filespecs above, with interval and Id
    retval = dsl_gie_primary_new('primary-gie', inferConfigFile, modelEngineFile, 1)

    if retval != DSL_RETURN_SUCCESS:
        print(retval)
        
    # New KTL Tracker, setting max width and height of input frame
    retval = dsl_tracker_ktl_new('ktl-tracker', 480, 272)
    if retval != DSL_RETURN_SUCCESS:
        print(retval)

    # New Secondary GIE set to Infer on the Primary GIE defined above
    retval = dsl_gie_secondary_new('sgie', sgie_config_file, sgie_model_file, 'primary-gie')
    if retval != DSL_RETURN_SUCCESS:
        print(retval)

    # New Secondary GIE set to Infer on the Primary GIE defined above
    retval = dsl_gie_secondary_new('sgie2', sgie2_config_file, sgie2_model_file, 'primary-gie')
    if retval != DSL_RETURN_SUCCESS:
        print(retval)
    
    # New Secondary GIE set to Infer on the Primary GIE defined above
    retval = dsl_gie_secondary_new('sgie3', sgie3_config_file, sgie3_model_file, 'primary-gie')
    if retval != DSL_RETURN_SUCCESS:
        print(retval)

    #########################################
    #   Create Display 
    #########################################

    retVal = dsl_tiler_new("display1", 1280, 720)
    
    if retVal != DSL_RETURN_SUCCESS:
        print(retVal)

    # New OSD with clock enabled... using default values.
    retval = dsl_osd_new('on-screen-display', False)
    if retval != DSL_RETURN_SUCCESS:
        print(retval)
    
    # Add the above defined batch meta handler to the Source Pad of the KTL Tracker
    retval = dsl_osd_batch_meta_handler_add('on-screen-display', DSL_PAD_SINK, osd_batch_meta_handler_cb, None)
    if retval != DSL_RETURN_SUCCESS:
        print(retval)

    #########################################
    #   Create Display Overlay 
    #########################################

    retVal = dsl_sink_overlay_new("sink1", 100, 10, 1200, 1200)

    if retVal != DSL_RETURN_SUCCESS:
        print(retVal)

    #########################################
    #   Create sink window
    #########################################

    retVal = dsl_sink_window_new('window-sink', 0, 0, 1280, 720)
    if retVal != DSL_RETURN_SUCCESS:
        print(retVal) 

    #########################################
    #   Create pipeline1
    #########################################

    retVal = dsl_pipeline_new("pipeline1")
    
    if retVal != DSL_RETURN_SUCCESS:
        print(retVal)

    #########################################
    #  Add components to pipeline 
    #########################################
    
    retVal = dsl_pipeline_component_add_many('pipeline1', ['video1', 'display1', 'on-screen-display', 
        'primary-gie','sgie', 'sgie2', 'sgie3', 'ktl-tracker', 'window-sink', None])
    
    if retVal != DSL_RETURN_SUCCESS:
        print(retVal)


    #########################################
    # Play video
    #########################################

    result = dsl_pipeline_play("pipeline1")
    if retVal != DSL_RETURN_SUCCESS:
        print(retVal)


    dsl_pipeline_dump_to_dot('pipeline1',"state-playing")    

    #########################################
    #   Add an EOS listener
    #########################################

    retVal = dsl_pipeline_eos_listener_add('pipeline1', eos_listener, None)

    if retVal != DSL_RETURN_SUCCESS:
        print(retVal)

    #########################################
    # Add the XWindow event handler functions defined above
    #########################################
    
    retval = dsl_pipeline_xwindow_key_event_handler_add("pipeline1", xwindow_key_event_handler, None)
    if retval != DSL_RETURN_SUCCESS:
       print(retVal)

    retval = dsl_pipeline_xwindow_button_event_handler_add("pipeline1", xwindow_button_event_handler, None)
    if retval != DSL_RETURN_SUCCESS:
        print(retVal)


    #########################################
    # Run main loop
    #########################################

    dsl_main_loop_run()

    #########################################
    # Stop  pipeline
    #########################################

    dsl_pipeline_stop("pipeline1")

    #########################################
    # Remove pipeline
    #########################################

    dsl_pipeline_delete_all()

    #########################################
    # Remove component 
    #########################################

    dsl_component_delete_all()

def main():
    """Parse the command line parameters and run test """
    if len(sys.argv) < 2:
        print("")
        print("#################################################################")
        print("#")
        print("#    Error: Missing source file name.")
        print("#    Calling sequence: python3 ds_3sgie_test.py <Video source file>")
        print("#")
        print("##################################################################")
    else:
        for x in range(3):
            print("Starting run number: ",x)
            test1()

if __name__ == '__main__':
    eos_count = 0
    main()
