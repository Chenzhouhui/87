set_property SRC_FILE_INFO {cfile:f:/ax7020/2017/course_s1/hdmi_out_test/hdmi_out_test.srcs/sources_1/ip/video_clock/video_clock.xdc rfile:../../../hdmi_out_test.srcs/sources_1/ip/video_clock/video_clock.xdc id:1 order:EARLY scoped_inst:inst} [current_design]
set_property src_info {type:SCOPED_XDC file:1 line:57 export:INPUT save:INPUT read:READ} [current_design]
set_input_jitter [get_clocks -of_objects [get_ports clk_in1]] 0.2
