import sys
sys.path.insert(0, "../../")
import time

from dsl import *

DSL_RETURN_SUCCESS = 0

# Filespecs for the Primary GIE
inferConfigFile = '../../test/configs/config_infer_primary_nano.txt'
modelEngineFile = '../../test/models/Primary_Detector_Nano/resnet10.caffemodel_b4_fp16.engine'

MAX_SOURCE_COUNT = 4
cur_source_count = 0

# Function to be called on End-of-Stream (EOS) event
def eos_event_listener(client_data):
    print('Pipeline EOS event')
    dsl_main_loop_quit()

# Function to be called on XWindow Delete event
## 
def xwindow_delete_event_handler(client_data):
    print('delete window event')
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
    elif key_string.upper() == 'Q' or key_string == '':
        dsl_main_loop_quit()

    # Add a new source
    elif key_string == '+': 
        if cur_source_count < MAX_SOURCE_COUNT:
            print(cur_source_count)
            cur_source_count += 1
            print(cur_source_count)
            source_name = 'uri-source-' + str(cur_source_count)
            print('add source ', source_name)
            dsl_source_uri_new(source_name, "../../test/streams/sample_1080p_h264.mp4", False, 0, 0, 0)
            dsl_pipeline_component_add('pipeline', source_name)

    # Remove the last source added
    elif key_string == '-': 
        if cur_source_count > 1:
            source_name = 'uri-source-' + str(cur_source_count)
            print('removing source ', source_name)
            dsl_pipeline_component_remove('pipeline', source_name)
            dsl_component_delete(source_name)
            cur_source_count -= 1
        

def main(args):

    global MAX_SOURCE_COUNT, cur_source_count

    # Since we're not using args, we can Let DSL initialize GST on first call
    while True:

        ## 
        # First new URI File Source
        ## 
        retval = dsl_source_uri_new('uri-source-1', "../../test/streams/sample_1080p_h264.mp4", False, 0, 0, 0)
        if retval != DSL_RETURN_SUCCESS:
            break

        ## 
        # New Primary GIE using the filespecs above, with infer interval
        ## 
        retval = dsl_gie_primary_new('primary-gie', inferConfigFile, modelEngineFile, 1)
        if retval != DSL_RETURN_SUCCESS:
            break

        ## 
        # New Tiled Display, setting width and height, use default cols/rows set by source count
        ## 
        retval = dsl_tiler_new('tiler', 1280, 720)
        if retval != DSL_RETURN_SUCCESS:
            break

        ## 
        # New OSD for single tiled stream - will be added to Pipeline since using Tiler
        ## 
        retval = dsl_osd_new('on-screen-display', False)
        if retval != DSL_RETURN_SUCCESS:
            break

        ## 
        # New Window Sink, 0 x/y offsets and same dimensions as Tiled Display
        ## 
        retval = dsl_sink_window_new('window-sink', 0, 0, 1280, 720)
        if retval != DSL_RETURN_SUCCESS:
            break

        ## 
        # New Pipeline to use with the above components
        ## 
        retval = dsl_pipeline_new('pipeline')
        if retval != DSL_RETURN_SUCCESS:
            break

        ## 
        # Add all the components to our pipeline
        ## 
        retval = dsl_pipeline_component_add_many('pipeline', 
            ['uri-source-1' , 'primary-gie', 'tiler', 'on-screen-display', 'window-sink', None])
        if retval != DSL_RETURN_SUCCESS:
            break
        cur_source_count = 1

        ##
        ## IMPORTANT: we need to explicitely set the stream-muxer Batch properties, otherwise the Pipeline
        ## will use the number of Sources when set to Playing, which would be 1 and too small
        ##
        retval = dsl_pipeline_streammux_batch_properties_set('pipeline', MAX_SOURCE_COUNT, 40000)
        if retval != DSL_RETURN_SUCCESS:
            break
        
        ## 
        ## Add the XWindow event handlers and EOS listener functions defined above
        ##
        retval = dsl_pipeline_xwindow_key_event_handler_add("pipeline", xwindow_key_event_handler, None)
        if retval != DSL_RETURN_SUCCESS:
            break

        retval = dsl_pipeline_xwindow_delete_event_handler_add("pipeline", xwindow_delete_event_handler, None)
        if retval != DSL_RETURN_SUCCESS:
            break

        retval = dsl_pipeline_eos_listener_add('pipeline', eos_event_listener, None)
        if retval != DSL_RETURN_SUCCESS:
            break

        ## 
        # Play the pipeline
        ## 
        retval = dsl_pipeline_play('pipeline')
        if retval != DSL_RETURN_SUCCESS:
            break

        ## 
        # Start/join the main-loop until dsl_main_loop_exit()
        ## 
        dsl_main_loop_run()
        retval = DSL_RETURN_SUCCESS
        break

    # Print out the final result
    print(dsl_return_value_to_string(retval))

    dsl_pipeline_delete_all()
    dsl_component_delete_all()

if __name__ == '__main__':
    sys.exit(main(sys.argv))
